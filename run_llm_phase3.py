#!/usr/bin/env python3
"""Phase 3 use cases on real hardware: zero-trust gates applied to live Qwen3-8B output.

Three measurements, none scripted:

1. **Micro-ML Architect (live active inference)** — the LLM designs a `CustomNet` under
   physical constraints; the reality engine returns a deterministic error trace; the
   trace becomes the next prompt. Reports how many turns to reach ENERGY 0.
2. **Anti-Simulation Axiom on real output** — every generated candidate is passed
   through `ImplementationAuditor`. Reports how often a real model emits stubs.
3. **Proof-of-execution attestation** — a token is minted only for candidates that
   actually pass the physical harness.

Usage::

    python run_llm_phase3.py --trials 5 --out .scratchpad/llm_phase3
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import time
from pathlib import Path

from anse.autopoiesis.neuro_surgeon import ActiveInferenceLoop, MicroMLRealityEngine
from anse.core.ollama_extractor import OllamaConfig, OllamaExtractor
from execution_attestation import ImplementationAuditor

SYSTEM = (
    "You are an expert PyTorch engineer. Return only a single ```python code block. "
    "Never emit placeholder stubs such as `pass`, `...` or NotImplementedError."
)

STUB_BAIT_PROMPTS = [
    "Implement `def parse_config(path: str) -> dict:` that reads a real TOML file and "
    "returns its parsed contents. Handle a missing file by raising FileNotFoundError.",
    "Implement `def fetch_user(user_id: int) -> dict:` that looks up a user in a sqlite3 "
    "database table `users(id, name, email)` and returns the row as a dict.",
    "Implement `class RetryPolicy` with a method `next_delay(attempt: int) -> float` "
    "giving exponential backoff with jitter, plus `reset()`.",
    "Implement `def merge_intervals(intervals: list[tuple[int,int]]) -> list[tuple[int,int]]` "
    "merging all overlapping intervals.",
]


PARAM_RE = re.compile(r"Parameter budget exceeded \((\d+)")


def _param_count(error: str | None) -> int | None:
    """Pull the measured parameter count out of a budget-violation trace."""
    m = PARAM_RE.search(error or "")
    return int(m.group(1)) if m else None


def audit(code: str) -> list[str]:
    """Run the Axiom 2 AST auditor over a candidate, tolerating syntax errors."""
    try:
        tree = ast.parse(code or "pass", filename="candidate.py")
    except SyntaxError as e:
        return [f"SyntaxError line {e.lineno}: {e.msg}"]
    auditor = ImplementationAuditor("candidate.py")
    auditor.visit(tree)
    return list(auditor.violations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--max-turns", type=int, default=3)
    parser.add_argument("--out", default=".scratchpad/llm_phase3")
    parser.add_argument("--model", default="qwen3:8b")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    extractor = OllamaExtractor(OllamaConfig(gen_model=args.model, max_new_tokens=900))

    def generate(prompt: str) -> str:
        text, _ = extractor.generate(prompt, system_prompt=SYSTEM)
        return text

    # ── 1. Live active inference ────────────────────────────────────────────
    print(f"[phase3-llm] Micro-ML Architect: {args.trials} live trials, "
          f"max {args.max_turns} turns each", flush=True)
    loop = ActiveInferenceLoop(generator=generate)
    trials: list[dict] = []
    for t in range(1, args.trials + 1):
        started = time.time()
        steps = loop.run_live(max_turns=args.max_turns)
        converged = steps[-1].is_valid
        trials.append({
            "trial": t,
            "turns": len(steps),
            "converged": converged,
            "energies": [s.energy for s in steps],
            "first_error": steps[0].error_trace,
            "turn_errors": [s.error_trace for s in steps],
            "turn_param_counts": [_param_count(s.error_trace) for s in steps],
            "proof_token": steps[-1].proof_token,
            "wall_s": round(time.time() - started, 1),
            "final_code": steps[-1].candidate_code,
        })
        print(f"  trial {t}: turns={len(steps)} energies={[s.energy for s in steps]} "
              f"converged={converged} ({trials[-1]['wall_s']}s)", flush=True)

    solved = [t for t in trials if t["converged"]]
    turns_to_solve = [t["turns"] for t in solved]

    # ── 2. Anti-simulation axiom on real generations ────────────────────────
    print("[phase3-llm] Axiom 2 (anti-simulation) on real output", flush=True)
    audits: list[dict] = []
    for prompt in STUB_BAIT_PROMPTS:
        from anse.symbolic.parser import extract_code

        raw, _ = extractor.generate(prompt, system_prompt=SYSTEM)
        code = extract_code(raw).code
        violations = audit(code)
        audits.append({
            "prompt": prompt[:70],
            "violations": violations,
            "clean": not violations,
            "code_chars": len(code),
        })
        print(f"  clean={not violations} violations={violations or '-'}", flush=True)

    # Control: the auditor must still fire on a deliberate stub.
    control = audit("def f(x):\n    pass\n")

    report = {
        "model": args.model,
        "micro_ml_architect": {
            "trials": len(trials),
            "converged": len(solved),
            "convergence_rate_pct": round(100.0 * len(solved) / max(len(trials), 1), 1),
            "mean_turns_to_energy_zero": (
                round(sum(turns_to_solve) / len(turns_to_solve), 2) if turns_to_solve else None
            ),
            "first_turn_success": sum(1 for t in solved if t["turns"] == 1),
            "self_healed_after_failure": sum(1 for t in solved if t["turns"] > 1),
            "trials_detail": trials,
        },
        "anti_simulation_axiom": {
            "generations_audited": len(audits),
            "clean": sum(a["clean"] for a in audits),
            "stubbed": sum(not a["clean"] for a in audits),
            "auditor_control_fires_on_stub": bool(control),
            "detail": audits,
        },
        "attestation": {
            "tokens_minted": sum(1 for t in trials if t["proof_token"]),
            "tokens_withheld": sum(1 for t in trials if not t["proof_token"]),
            "minted_only_when_valid": all(
                bool(t["proof_token"]) == t["converged"] for t in trials
            ),
        },
        "llm_calls": extractor.calls,
        "generated_tokens": extractor.total_eval_tokens,
    }
    (out_dir / "phase3_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    m = report["micro_ml_architect"]
    a = report["anti_simulation_axiom"]
    print("\n=== PHASE 3 (real LLM) ===")
    print(f"Micro-ML architect: {m['converged']}/{m['trials']} reached ENERGY 0 "
          f"({m['convergence_rate_pct']}%), mean turns={m['mean_turns_to_energy_zero']}")
    print(f"  first-turn success={m['first_turn_success']}  self-healed={m['self_healed_after_failure']}")
    print(f"Axiom 2: {a['clean']}/{a['generations_audited']} clean, {a['stubbed']} stubbed "
          f"(control fires: {a['auditor_control_fires_on_stub']})")
    print(f"Attestation minted only when physically valid: "
          f"{report['attestation']['minted_only_when_valid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
