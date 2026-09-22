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


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="antigravity-harness",
        description="Antigravity Autonomous Neuro-Symbolic Execution & Hardening Harness CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Harness command to run")

    # audit
    p_audit = subparsers.add_parser(
        "audit", help="Audit code against stubs, mock data, and simulations"
    )
    p_audit.add_argument("target", help="File or directory path to audit")
    p_audit.add_argument("--include-tests", action="store_true", help="Include test files in audit")

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

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "audit":
        return cmd_audit(args)
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
