"""
anse/gwaya/cli.py
=================
Command Line Interface for GWAYA (Qwen + Laya Advisor & Verifier).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from anse.gwaya.advisor import GwayaAdvisor
from anse.gwaya.verifier import verify_gemini_output


def main():
    parser = argparse.ArgumentParser(description="GWAYA: AI Advisor & Verifier Companion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: verify
    verify_p = subparsers.add_parser("verify", help="Verify code against hallucinations, stubs, and security risks")
    verify_p.add_argument("target", help="Code string or path to code file")
    verify_p.add_argument("--mock", action="store_true", help="Use lightweight mock engine")

    # Command: advise
    advise_p = subparsers.add_parser("advise", help="Get engineering advice and grounded recommendations")
    advise_p.add_argument("prompt", help="Engineering task prompt")
    advise_p.add_argument("--context", help="Code context string or file", default=None)
    advise_p.add_argument("--mock", action="store_true", help="Use lightweight mock engine")

    args = parser.parse_args()

    if args.command == "verify":
        # Check if target is a file
        target_path = Path(args.target)
        if target_path.exists() and target_path.is_file():
            code = target_path.read_text(encoding="utf-8")
            print(f"📄 Read {len(code)} characters from {target_path}")
        else:
            code = args.target

        print("\n🔍 Running GWAYA Parallel Verification...")
        result = verify_gemini_output(code, mock=args.mock)

        status_icon = "✅" if result.passed else "🚨"
        print(f"\n{status_icon} [VERDICT]: {result.verdict.value}")
        print(f"  Confidence:     {result.confidence:.3f}")
        print(f"  Physical Energy: {result.physical_energy:.2f} {'(Barrier E=1e6 applied)' if result.physical_energy >= 1e6 else ''}")
        print(f"  Specialist:     {result.specialist_pillar.value}")
        print(f"  Latency:        {result.latency_ms:.2f} ms")
        if result.stubs_detected:
            print(f"  Stubs Detected: {'; '.join(result.stubs_detected)}")
        if result.security_flags:
            print(f"  Security Flags: {'; '.join(result.security_flags)}")
        print(f"  Recommendation: {result.recommendation}")
        sys.exit(0 if result.passed else 1)

    elif args.command == "advise":
        advisor = GwayaAdvisor(mock=args.mock)
        ctx = None
        if args.context:
            ctx_path = Path(args.context)
            ctx = ctx_path.read_text(encoding="utf-8") if ctx_path.exists() else args.context

        print(f"\n🧠 Consulting GWAYA Advisor on: '{args.prompt}'...")
        advice = advisor.advise(args.prompt, code_context=ctx)
        print(f"\n[Specialist Pillar]: {advice.specialist_pillar.value}")
        print(f"[Verdict]:           {advice.verdict.value}")
        print(f"[Latency]:           {advice.latency_ms:.1f} ms")
        print(f"[Explanation]:\n{advice.explanation}")
        print(f"\n[Suggested Implementation]:\n{advice.suggested_code}")


if __name__ == "__main__":
    main()
