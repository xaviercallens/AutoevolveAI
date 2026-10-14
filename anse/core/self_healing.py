"""
Self-Healing Loop Pattern with Gemini 4 Argon (`gemini-4-argon` / Gemini Argos) and Antigravity Guard.

Connects LLM code generation directly to deterministic verification (Argos Cyber-Defense AST,
anti-stub validation, phantom import auditing, Ruff linting, MyPy type checks) in an automated closed-loop.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from antigravity_harness.core.argos_hardener import (
    GEMINI_ARGOS_MODEL_ID,
    ArgosHardeningConfig,
    ArgosHardeningEngine,
    ArgosInteractionsClient,
    resolve_gemini_argos_model,
)

logger = logging.getLogger(__name__)


def generate_and_heal(
    prompt: str,
    target_file: str,
    max_iterations: int = 3,
    model_name: str = GEMINI_ARGOS_MODEL_ID,
    api_key: str | None = None,
    client: Any | None = None,
) -> str:
    """
    Generate code with Gemini 4 Argon (`gemini-4-argon`) and iteratively repair it
    using deterministic guard tracebacks and Argos cyber-defense AST checks.

    Parameters:
        prompt: Initial engineering instruction or task specification.
        target_file: Path to write the candidate Python code.
        max_iterations: Number of self-repair cycles before raising RuntimeError.
        model_name: Gemini model ID (defaults to 'gemini-4-argon'; aliases like 'gemini-argos' resolve automatically).
        api_key: Optional Gemini API key (defaults to GEMINI_API_KEY environment variable).
        client: Optional pre-initialized genai.Client (for testing or custom transports).

    Returns:
        The verified, fully compliant Python code.
    """
    resolved_model = resolve_gemini_argos_model(model_name)
    argos_cfg = ArgosHardeningConfig(primary_model=resolved_model)
    argos_client = ArgosInteractionsClient(config=argos_cfg, api_key=api_key, client=client)
    hardening_engine = ArgosHardeningEngine(config=argos_cfg)

    current_prompt = prompt
    previous_interaction_id: str | None = None
    target_path = Path(target_file).resolve()
    guard_script = Path(__file__).parent.parent.parent / "antigravity_guard.py"
    python_exe = sys.executable

    system_instruction = (
        "Generate production-grade, cyber-hardened Python code adhering to strict typing (PEP 484), "
        "zero-trust execution safety (no eval/exec/shell=True/pickle.loads), and clean formatting. "
        "Output only clean, executable Python code inside a single ```python block."
    )

    for iteration in range(max_iterations):
        logger.info(
            "Argos self-healing iteration %d/%d for %s (model=%s)",
            iteration + 1,
            max_iterations,
            target_path.name,
            resolved_model,
        )
        interaction_res = argos_client.create_interaction(
            current_prompt,
            system_instruction=system_instruction,
            previous_interaction_id=previous_interaction_id,
            model=resolved_model,
        )
        previous_interaction_id = interaction_res.get("interaction_id") or previous_interaction_id
        raw_text = interaction_res.get("text", "")
        code = ArgosHardeningEngine.extract_python_code(raw_text)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(code, encoding="utf-8")

        # 1. Run Argos Cyber-Defense & Anti-Stub AST Gate
        argos_report = hardening_engine.audit_code(
            code,
            target=str(target_path),
            thought_signature=interaction_res.get("thought_signature", ""),
            interaction_id=previous_interaction_id or "",
        )

        # 2. Run deterministic antigravity_guard.py subprocess
        result = subprocess.run(
            [python_exe, str(guard_script), str(target_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if argos_report.passed and result.returncode == 0:
            logger.info(
                "Code verified cleanly on iteration %d (attestation=%s).",
                iteration + 1,
                argos_report.attestation_token,
            )
            return code

        # Feed deterministic guard + Argos cyber violations back into Gemini 4 Argon
        logger.warning(
            "Verification failed on iteration %d. Extracting pain signal...", iteration + 1
        )
        argos_violations_str = "\n".join(
            f"- [{v.severity}:{v.rule_id}] {v.message}" for v in argos_report.violations
        )
        current_prompt = (
            f"Original Goal: {prompt}\n\n"
            f"The generated code failed deterministic verification with the following errors:\n"
            f"ARGOS HARDENING VIOLATIONS:\n{argos_violations_str or 'None'}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n\n"
            f"Fix all issues, eliminate cyber-defense violations, phantom/unresolved imports, and stubs, "
            f"satisfy MyPy/Ruff, and return the corrected code."
        )

    raise RuntimeError(
        f"Agent failed to satisfy deterministic quality gates for {target_file} within {max_iterations} iterations."
    )


def generate_and_evolve_hardened(
    prompt: str,
    target_file: str,
    *,
    evaluator_fn: Any,
    generations: int = 4,
    num_islands: int = 3,
    max_heal_iterations: int = 3,
    model_name: str = GEMINI_ARGOS_MODEL_ID,
    api_key: str | None = None,
    client: Any | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    r"""Generate code via Gemini 4 Argon (`generate_and_heal`), then optimize it with
    `AlphaEvolveBiomimeticEngine` (structural GP operators + NSGA-II + $\epsilon$-Lexicase + AIS)
    and verify the champion with `ArgosHardeningEngine`.
    """
    from anse.autopoiesis.alphaevolve_biomimetic import AlphaEvolveBiomimeticEngine

    baseline_code = generate_and_heal(
        prompt=prompt,
        target_file=target_file,
        max_iterations=max_heal_iterations,
        model_name=model_name,
        api_key=api_key,
        client=client,
    )

    engine = AlphaEvolveBiomimeticEngine(
        evaluator_fn=evaluator_fn,
        num_islands=num_islands,
        seed=seed,
    )
    evo_summary = engine.run_evolution_with_hardened_gate(
        initial_codes=[baseline_code],
        generations=generations,
    )

    champion_code = (
        evo_summary["champion"]["dominant_code"]
        if evo_summary.get("promoted") and "champion" in evo_summary
        else baseline_code
    )
    hardening_engine = ArgosHardeningEngine(
        config=ArgosHardeningConfig(primary_model=resolve_gemini_argos_model(model_name))
    )
    final_audit = hardening_engine.audit_code(champion_code, target=target_file)
    if not final_audit.passed:
        champion_code = baseline_code
        final_audit = hardening_engine.audit_code(baseline_code, target=target_file)

    Path(target_file).resolve().write_text(champion_code, encoding="utf-8")
    return {
        "final_code": champion_code,
        "promoted": bool(evo_summary.get("promoted", False) and final_audit.passed),
        "baseline_energy": evo_summary.get("baseline_energy"),
        "champion_energy": evo_summary.get("champion_energy"),
        "delta_energy": evo_summary.get("delta_energy"),
        "pareto_front_size": evo_summary.get("pareto_front_size", 0),
        "archive_total_elites": evo_summary.get("archive_total_elites", 0),
        "attestation_token": final_audit.attestation_token,
        "hardening_passed": final_audit.passed,
    }


