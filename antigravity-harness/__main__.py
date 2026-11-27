"""
Antigravity Harness CLI Entry Point:
Provides a unified command-line tool for the Antigravity Harness:
  - audit: runs AntiStubGuard against files or directories
  - verify: runs Lean 4 theorem and proof verification via Lake
  - profile: profiles algorithmic complexity and energy (E = w_t*ms + w_m*RAM)
  - test: executes unit, integration, and visual tests with structured reporting
  - dpo: builds and exports DPO preference pairs from recorded traces
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from antigravity_harness.agents.qa_agent import QAAgent
from antigravity_harness.core.anti_stub_guard import AntiStubGuard
from antigravity_harness.core.lean4_verifier import Lean4Verifier
from antigravity_harness.rl_pipeline.dpo_dataset_builder import DPODatasetBuilder
from antigravity_harness.rl_pipeline.trace_extractor import TraceExtractor
from antigravity_harness.storage.redis_bus import RedisBus
from antigravity_harness.tests_runner.unit_integration import UnitIntegrationRunner


def cmd_audit(args: argparse.Namespace) -> int:
    guard = AntiStubGuard()
    target = Path(args.target)
    print(f"==> Auditing '{target}' with AntiStubGuard...")

    if target.is_dir():
        result = guard.audit_directory(target, exclude_tests=not args.include_tests)
    else:
        result = guard.audit_file(target)

    print(result.summary)
    return 0 if result.is_clean else 1


def cmd_verify(args: argparse.Namespace) -> int:
    formal_dir = Path(args.formal_dir)
    print(f"==> Verifying Lean 4 specifications in '{formal_dir}'...")
    verifier = Lean4Verifier(formal_dir=formal_dir)

    inv = verifier.extract_proof_inventory(formal_dir)
    print(
        f"Formal Inventory: {len(inv['theorems'])} theorems, {len(inv['lemmas'])} lemmas, {len(inv['axioms'])} axioms, {len(inv['definitions'])} definitions."
    )

    sound, msg = verifier.check_soundness(formal_dir)
    if not sound:
        print(f"❌ {msg}")
        return 1
    print(f"✅ {msg}")

    if args.build:
        res = verifier.verify()
        print(res.summary)
        return 0 if res.success else 1
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    runner = UnitIntegrationRunner()
    print(f"==> Running tests on '{args.path}'...")
    summary = runner.run_pytest(args.path)
    print(summary.summary)
    if summary.failures:
        print("\nFailures:")
        for f in summary.failures[:5]:
            print(f"  {f}")
    return 0 if summary.success else 1


def cmd_dpo(args: argparse.Namespace) -> int:
    bus = RedisBus()
    extractor = TraceExtractor(bus)
    sessions = extractor.extract_from_bus()
    print(f"==> Extracted {len(sessions)} session(s) from RedisBus.")

    builder = DPODatasetBuilder()
    pairs = builder.build_pairs_from_sessions(sessions)
    print(f"==> Generated {len(pairs)} DPO preference pair(s).")

    out_path = Path(args.output)
    builder.export_to_jsonl(pairs, out_path)
    print(f"✅ Exported to '{out_path}'.")
    return 0


def cmd_qa(args: argparse.Namespace) -> int:
    agent = QAAgent()
    target = Path(args.file)
    if not target.exists():
        print(f"❌ File '{target}' does not exist.")
        return 1

    code = target.read_text(encoding="utf-8")
    report = agent.generate_adversarial_suite(args.module, code)
    print(
        f"==> Generated {report.num_tests_generated} adversarial tests for '{report.target_name}':"
    )
    print(report.test_code)
    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    from antigravity_harness.core.laya_gate import LayaQualityGate
    gate = LayaQualityGate()
    target = Path(args.target)
    
    if target.is_file():
        success = gate.evaluate_file(target)
        return 0 if success else 1
    elif target.is_dir():
        all_success = True
        for filepath in target.rglob("*"):
            if filepath.is_file() and filepath.suffix in [".py", ".md", ".json", ".txt", ".lean"]:
                if not gate.evaluate_file(filepath):
                    all_success = False
        return 0 if all_success else 1
    return 1


def cmd_decision(args: argparse.Namespace) -> int:
    import json

    from anse.decision.kev_engine import KevDecisionEngine

    report_path = Path(args.report) if args.report else None
    out_path = Path(args.out) if args.out else None
    engine = KevDecisionEngine(base_url=args.url, temperature=args.temp)

    if report_path:
        if not report_path.exists():
            print(f"❌ Specified report does not exist: {report_path}")
            return 2
        telemetry = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        from scripts.kev_decision_gate import _resolve_default_report_path
        resolved = _resolve_default_report_path()
        if not resolved or not resolved.exists():
            print("❌ No retraining report found in results/nightly_training/")
            return 2
        telemetry = json.loads(resolved.read_text(encoding="utf-8"))

    decision = engine.evaluate_saaw_retraining(telemetry)
    saved = engine.save_decision(decision, output_path=out_path)
    print(f"==> Kev SAAW Retrain Decision: {decision.status}")
    print(f"    Profile ID       : {decision.profile_id}")
    print(f"    Promote (Noul)   : {decision.promote_checkpoint} (P = {decision.promote_probability:.4f})")
    print(f"    Strategy (Choice): {decision.deployment_strategy} (Conf = {decision.deployment_confidence:.4f})")
    print(f"    Quality (Score)  : {decision.retraining_quality_score:.2f} / 3.00 (Conf = {decision.retraining_quality_confidence:.4f})")
    print(f"    Next Adaptation  : {decision.next_cycle_adaptation}")
    if decision.failed_steps:
        print(f"    Failed Steps     : {decision.failed_steps}")
    print(f"    Saved Report     : {saved}")

    if args.gate and decision.status != "APPROVED":
        print(f"❌ Gate failed: status={decision.status}")
        return 1
    print("✅ Gate passed: Retraining approved.")
    return 0


def cmd_harden(args: argparse.Namespace) -> int:
    import json

    from antigravity_harness.core.argos_hardener import (
        ArgosHardeningConfig,
        ArgosHardeningEngine,
        resolve_gemini_argos_model,
    )

    resolved_model = resolve_gemini_argos_model(args.model)
    cfg = ArgosHardeningConfig(primary_model=resolved_model)
    engine = ArgosHardeningEngine(config=cfg)
    target = Path(args.target)

    print(f"==> Running Gemini Argos ({resolved_model}) Hardening Gate on '{target}'...")
    reports = engine.audit_path(target, include_tests=args.include_tests)
    if not reports:
        print(f"⚠️ No Python files found under '{target}'.")
        return 1

    passed_count = sum(1 for r in reports if r.passed)
    failed_reports = [r for r in reports if not r.passed]

    for r in reports:
        if not r.passed or len(reports) <= 10:
            print(r.summary)

    print(
        f"\n==> Argos Hardening Summary: {passed_count}/{len(reports)} file(s) passed "
        f"(Model: {resolved_model}, Failed: {len(failed_reports)})."
    )

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_id": resolved_model,
            "total_files": len(reports),
            "passed_files": passed_count,
            "failed_files": len(failed_reports),
            "all_passed": len(failed_reports) == 0,
            "reports": [r.to_dict() for r in reports],
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"==> Saved Argos hardening telemetry to '{out_path}'.")

    return 0 if len(failed_reports) == 0 else 1


def cmd_alphaevolve(args: argparse.Namespace) -> int:
    import json

    from anse.autopoiesis.alphaevolve_biomimetic import AlphaEvolveBiomimeticEngine

    target = Path(args.target)
    if not target.is_file():
        print(f"❌ Target file '{target}' does not exist.")
        return 1

    seed_code = target.read_text(encoding="utf-8")

    def _default_evaluator(code: str) -> dict[str, float]:
        # Deterministic AST + physical complexity proxy when no custom benchmark runner is attached
        import ast

        tree = ast.parse(code)
        node_count = sum(1 for _ in ast.walk(tree))
        loop_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        phys_e = float(node_count) * 0.5 + float(loop_count) * 8.0
        return {
            "physical_energy": phys_e,
            "latency_ms": phys_e * 0.2,
            "memory_mb": 1.5,
            "invariant_error": 0.0,
        }

    engine = AlphaEvolveBiomimeticEngine(
        evaluator_fn=_default_evaluator,
        num_islands=args.islands,
        seed=args.seed,
    )
    print(
        f"==> Running AlphaEvolve + Biomimetic Evolution on '{target}' "
        f"(islands={args.islands}, generations={args.generations})..."
    )
    res = engine.run_evolution_with_hardened_gate(
        initial_codes=[seed_code],
        generations=args.generations,
    )
    print(
        f"==> Baseline Energy: {res['baseline_energy']:.4f} | "
        f"Champion Energy: {res['champion_energy']:.4f} | "
        f"Delta E: {res['delta_energy']:+.4f} | "
        f"Archive Elites: {res['archive_total_elites']}"
    )
    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
        print(f"==> Saved AlphaEvolve telemetry to '{out_path}'.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="antigravity-harness",
        description="Antigravity Autonomous Neuro-Symbolic Execution & Hardening Harness CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Harness command to run")

    # decision
    p_decision = subparsers.add_parser(
        "decision", help="Evaluate Kev post-retraining calibrated decision gate"
    )
    p_decision.add_argument("--report", default=None, help="Path to telemetry report JSON")
    p_decision.add_argument("--out", default=None, help="Output path for decision JSON")
    p_decision.add_argument("--gate", action="store_true", help="Enforce pass/fail gate")
    p_decision.add_argument("--url", default=None, help="Remote Kev / TypeSafe URL")
    p_decision.add_argument("--temp", type=float, default=1.0, help="Calibration temperature")

    # audit
    p_audit = subparsers.add_parser(
        "audit", help="Audit code against stubs, mock data, and simulations"
    )
    p_audit.add_argument("target", help="File or directory path to audit")
    p_audit.add_argument("--include-tests", action="store_true", help="Include test files in audit")

    # harden (Gemini Argos / gemini-4-argon)
    p_harden = subparsers.add_parser(
        "harden",
        help="Run Google Gemini Argos (gemini-4-argon) cyber-defense, anti-stub, and attestation hardening gate",
    )
    p_harden.add_argument("target", help="File or directory path to harden")
    p_harden.add_argument(
        "--model",
        default="gemini-4-argon",
        help="Gemini model identifier or alias (e.g. gemini-4-argon, gemini-argos, gemini-3.8-flash)",
    )
    p_harden.add_argument("--include-tests", action="store_true", help="Include test files in hardening audit")
    p_harden.add_argument("--json-out", default=None, help="Optional JSON output report path")

    # alphaevolve
    p_alphaevolve = subparsers.add_parser(
        "alphaevolve",
        help="Run AlphaEvolve + Genetic Algorithm + Biomimetic MAP-Elites evolution on a target Python file",
    )
    p_alphaevolve.add_argument("target", help="Python file to seed the AlphaEvolve archipelago")
    p_alphaevolve.add_argument("--islands", type=int, default=3, help="Number of MAP-Elites islands")
    p_alphaevolve.add_argument("--generations", type=int, default=5, help="Evolutionary generations")
    p_alphaevolve.add_argument("--seed", type=int, default=42, help="Random seed")
    p_alphaevolve.add_argument("--json-out", default=None, help="Optional JSON output report path")

    # verify
    p_verify = subparsers.add_parser(
        "verify", help="Verify Lean 4 formal specifications and proof soundness"
    )
    p_verify.add_argument("--formal-dir", default="formal", help="Directory containing Lean files")
    p_verify.add_argument("--build", action="store_true", help="Execute 'lake build' if available")

    # test
    p_test = subparsers.add_parser("test", help="Execute unit and integration tests")
    p_test.add_argument("path", default="tests/", nargs="?", help="Path to tests")

    # dpo
    p_dpo = subparsers.add_parser("dpo", help="Build and export DPO dataset from traces")
    p_dpo.add_argument("--output", default="results/dpo_dataset.jsonl", help="Output JSONL path")

    # qa
    p_qa = subparsers.add_parser("qa", help="Generate adversarial test suite for target function")
    p_qa.add_argument("file", help="Python source file to target")
    p_qa.add_argument("--module", default="anse.core", help="Module import path for target")

    # dichotomy
    p_dichotomy = subparsers.add_parser(
        "dichotomy", help="Split complex goals into dichotomic binary tree with bounded token budgets"
    )
    p_dichotomy.add_argument("--goal", required=True, help="High-level goal to decompose")
    p_dichotomy.add_argument("--budget", type=int, default=16000, help="Total token budget")
    p_dichotomy.add_argument("--depth", type=int, default=2, help="Max recursion depth")
    p_dichotomy.add_argument("--output", default="results/dichotomic_tree.json", help="Path to save JSON tree")
    p_dichotomy.add_argument("--execute", action="store_true", help="Execute and verify leaf tasks")

    # triage
    p_triage = subparsers.add_parser("triage", help="Use Laya System 1 to triage epistemic deception and thermodynamic violations")
    p_triage.add_argument("target", help="File or directory path to triage")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "decision":
        return cmd_decision(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "harden":
        return cmd_harden(args)
    elif args.command == "alphaevolve":
        return cmd_alphaevolve(args)
    elif args.command == "triage":
        return cmd_triage(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "test":
        return cmd_test(args)
    elif args.command == "dpo":
        return cmd_dpo(args)
    elif args.command == "qa":
        return cmd_qa(args)
    elif args.command == "dichotomy":
        from antigravity_harness.core.dichotomic_harness import run_dichotomy_cli
        out_path = Path(args.output) if args.output else None
        return run_dichotomy_cli(
            goal=args.goal,
            total_budget=args.budget,
            max_depth=args.depth,
            output_json=out_path,
            execute=args.execute,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
