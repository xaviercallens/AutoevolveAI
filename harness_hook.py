#!/usr/bin/env python3
"""
Symbiotic Teacher-Student Developer Reality Engine: Harness Hook.

Connects the ANSE / SuperGravity continuous learning AI directly to the developer's
active IDE and test harness (e.g., pytest, npm test, cargo test, lake build).
Treats daily developer test harnesses and validation assertions as the absolute Laws of Physics.

Modes of Operation:
1. Active Co-Pilot (Energy Minimizer / TDD on Steroids):
   Developer provides test harness; AI drafts code and self-repairs in background
   until test passes (E = 0) before returning code to developer.
2. Shadow Mode (Apprenticeship):
   Watches cursor, predicts next implementation in latent space, measures surprise
   against human-validated code, and triggers micro-DPO updates.
3. Golden Signal DPO Harvester:
   Extracts (prompt, human_fix [chosen], ai_attempt [rejected]) to train local LoRA adapter.
"""

from __future__ import annotations

import ast
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from execution_attestation import ImplementationAuditor, generate_attestation_proof  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("anse.harness_hook")


@dataclass
class HarnessResult:
    energy: float
    is_valid: bool
    duration_ms: float
    feedback: str
    returncode: int
    proof_token: str | None = None
    ast_violations: list[str] = field(default_factory=list)


@dataclass
class CoPilotStep:
    attempt: int
    candidate_code: str
    energy: float
    is_valid: bool
    feedback: str
    duration_ms: float


@dataclass
class CoPilotSummary:
    task_prompt: str
    target_file: str
    converged: bool
    attempts_used: int
    final_code: str | None
    steps: list[CoPilotStep]
    proof_token: str | None
    dpo_pair_recorded: bool


# ─────────────────────────────────────────────────────────────────────────────
# 1. Harness Evaluation Engine
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_in_harness(
    generated_code: str,
    target_file: str | Path,
    test_command: str,
    timeout_sec: float = 20.0,
    check_ast_stubs: bool = True,
) -> HarnessResult:
    """
    Injects candidate code into target file, runs the test harness, and computes physical energy E.
    Zero Energy (E = 0): Tests pass cleanly, no stubs.
    High Energy (E = 100): Tests fail, syntax error, or stub detected.
    """
    target_path = Path(target_file).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Anti-Stub & Anti-Simulation AST Inspection
    violations: list[str] = []
    if check_ast_stubs:
        try:
            tree = ast.parse(generated_code, filename=target_path.name)
            auditor = ImplementationAuditor(target_path.name)
            auditor.visit(tree)
            violations = auditor.violations
        except SyntaxError as se:
            return HarnessResult(
                energy=100.0,
                is_valid=False,
                duration_ms=0.0,
                feedback=f"SyntaxError on line {se.lineno}: {se.msg}",
                returncode=-1,
                ast_violations=[f"SyntaxError: {se.msg}"],
            )

    if violations:
        return HarnessResult(
            energy=100.0,
            is_valid=False,
            duration_ms=0.0,
            feedback=f"AST Whistleblower Violation: {'; '.join(violations)}",
            returncode=-2,
            ast_violations=violations,
        )

    # 2. Write proposed code to project file
    target_path.write_text(generated_code, encoding="utf-8")

    # 3. Execute Developer Harness Command
    start_t = time.perf_counter()
    try:
        proc = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
            cwd=str(PROJECT_ROOT),
        )
        dur_ms = (time.perf_counter() - start_t) * 1000.0

        if proc.returncode == 0:
            token = generate_attestation_proof("symbiotic_harness")
            return HarnessResult(
                energy=0.0,
                is_valid=True,
                duration_ms=dur_ms,
                feedback="Success: All harness validations passed.",
                returncode=0,
                proof_token=token,
            )
        else:
            err_output = proc.stderr.strip() or proc.stdout.strip()
            return HarnessResult(
                energy=100.0,
                is_valid=False,
                duration_ms=dur_ms,
                feedback=err_output,
                returncode=proc.returncode,
            )
    except subprocess.TimeoutExpired:
        return HarnessResult(
            energy=100.0,
            is_valid=False,
            duration_ms=timeout_sec * 1000.0,
            feedback=f"Harness execution timed out after {timeout_sec}s",
            returncode=-3,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Active Co-Pilot (Energy Minimizer / TDD on Steroids)
# ─────────────────────────────────────────────────────────────────────────────

class FallbackMockAgent:
    """Deterministic agent providing realistic multi-turn code synthesis for offline mode."""

    def __init__(self) -> None:
        self.call_count = 0

    def think(self, prompt: str) -> tuple[str, str]:
        self.call_count += 1
        if self.call_count == 1:
            # Turn 1: Buggy implementation missing edge case
            thought = "Naive attempt without handling empty input or off-by-one."
            code = (
                "def solve(nums: list[int]) -> int:\n"
                "    return nums[0] + nums[-1]  # Fails when list is empty or single element\n"
            )
            return thought, code
        else:
            # Turn 2: Robust self-corrected implementation
            thought = "Handled empty lists, single elements, and full bounds checking."
            code = (
                "def solve(nums: list[int]) -> int:\n"
                "    if not nums:\n"
                "        return 0\n"
                "    if len(nums) == 1:\n"
                "        return nums[0]\n"
                "    return nums[0] + nums[-1]\n"
            )
            return thought, code


def _handle_copilot_outcome(
    converged: bool,
    first_failed_code: str | None,
    final_code: str | None,
    prompt: str,
    target_path: Path,
    orig_content: str | None,
    steps_count: int,
    backup_original: bool,
) -> bool:
    """Handle DPO logging or file rollback upon completion of copilot attempts."""
    if converged and first_failed_code and final_code:
        return record_golden_signal_dpo(
            prompt=prompt,
            chosen_code=final_code,
            rejected_code=first_failed_code,
            metadata={"target_file": str(target_path), "attempts": steps_count},
        )
    if not converged and backup_original and orig_content is not None:
        target_path.write_text(orig_content, encoding="utf-8")
    return False


def active_inference_copilot(
    prompt: str,
    target_file: str | Path,
    test_command: str,
    agent: Any | None = None,
    max_attempts: int = 5,
    backup_original: bool = True,
) -> CoPilotSummary:
    """
    Active inference loop: intercepts test failures, formulates physical error feedback,
    and drives the AI agent to self-heal until E = 0.
    """
    target_path = Path(target_file).resolve()
    orig_content: str | None = target_path.read_text(encoding="utf-8") if target_path.exists() else None

    ai_agent = agent or FallbackMockAgent()
    current_prompt = prompt
    steps: list[CoPilotStep] = []
    converged = False
    final_code: str | None = None
    proof_token: str | None = None
    first_failed_code: str | None = None

    for attempt in range(1, max_attempts + 1):
        _, candidate_code = ai_agent.think(current_prompt)
        harness_res = evaluate_in_harness(candidate_code, target_path, test_command)

        steps.append(CoPilotStep(
            attempt=attempt,
            candidate_code=candidate_code,
            energy=harness_res.energy,
            is_valid=harness_res.is_valid,
            feedback=harness_res.feedback,
            duration_ms=harness_res.duration_ms,
        ))

        if harness_res.energy == 0.0:
            converged, final_code, proof_token = True, candidate_code, harness_res.proof_token
            break

        if first_failed_code is None:
            first_failed_code = candidate_code
        current_prompt += (
            f"\n\n[LAWS OF PHYSICS VIOLATION - ATTEMPT {attempt}]\n"
            f"Your code failed the project harness with the following trace:\n"
            f"{harness_res.feedback}\nFix the logic and return complete code."
        )

    dpo_recorded = _handle_copilot_outcome(
        converged=converged,
        first_failed_code=first_failed_code,
        final_code=final_code,
        prompt=prompt,
        target_path=target_path,
        orig_content=orig_content,
        steps_count=len(steps),
        backup_original=backup_original,
    )

    return CoPilotSummary(
        task_prompt=prompt,
        target_file=str(target_path),
        converged=converged,
        attempts_used=len(steps),
        final_code=final_code,
        steps=steps,
        proof_token=proof_token,
        dpo_pair_recorded=dpo_recorded,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Golden Signal DPO Harvester (Learning from Human Correction)
# ─────────────────────────────────────────────────────────────────────────────

def record_golden_signal_dpo(
    prompt: str,
    chosen_code: str,
    rejected_code: str,
    metadata: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
) -> bool:
    """
    Writes aligned (prompt, chosen, rejected) triplets for Direct Preference Optimization (DPO).
    The delta between what the AI proposed and what actually passed the harness becomes
    the exact gradient for fine-tuning the continuous LoRA adapter.
    """
    save_dir = Path(output_dir) if output_dir else PROJECT_ROOT / ".scratchpad"
    save_dir.mkdir(parents=True, exist_ok=True)
    dpo_file = save_dir / "golden_dpo_pairs.jsonl"

    record = {
        "timestamp": time.time(),
        "prompt": prompt,
        "chosen": chosen_code.strip(),
        "rejected": rejected_code.strip(),
        "metadata": metadata or {},
    }

    try:
        with open(dpo_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return True
    except OSError as e:
        logger.error("Failed to write DPO pair: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# 4. Shadow Mode (Apprenticeship Observer)
# ─────────────────────────────────────────────────────────────────────────────

def shadow_mode_observe(
    predicted_code: str,
    human_written_code: str,
    prompt: str,
    target_file: str,
) -> dict[str, Any]:
    """
    While the developer codes, compares AI's latent prediction against human code.
    If human code differs and passes tests, experiences 'Surprise Energy' and records DPO pair.
    """
    import difflib

    is_exact_match = predicted_code.strip() == human_written_code.strip()
    diff_lines = list(difflib.unified_diff(
        predicted_code.splitlines(),
        human_written_code.splitlines(),
        fromfile="ai_prediction.py",
        tofile="human_solution.py",
        lineterm="",
    ))

    surprise_energy = 0.0 if is_exact_match else min(100.0, float(len(diff_lines)) * 10.0)
    dpo_logged = False
    if not is_exact_match:
        dpo_logged = record_golden_signal_dpo(
            prompt=prompt,
            chosen_code=human_written_code,
            rejected_code=predicted_code,
            metadata={"target_file": target_file, "mode": "shadow_mode_cursor"},
        )

    return {
        "is_exact_match": is_exact_match,
        "surprise_energy": surprise_energy,
        "diff_line_count": len(diff_lines),
        "unified_diff": "\n".join(diff_lines[:15]),
        "dpo_pair_logged": dpo_logged,
    }


def main() -> None:
    print("=" * 70)
    print("  ANSE Symbiotic Teacher-Student Reality Engine: Harness Hook")
    print("=" * 70)
    print("Run `active_inference_copilot` or attach this hook to your IDE watcher.\n")


if __name__ == "__main__":
    main()
