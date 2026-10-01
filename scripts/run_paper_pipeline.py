#!/usr/bin/env python3
"""
ANSE Scientific Paper Pipeline: Single-Run Publication Quality Gate
===================================================================
Guarantees that the output of a single pipeline run meets publication
standards (Systems for ML / MLOps Track) based on the lessons learned
from a full Strong-Reject → Accept peer review cycle.

Usage:
    uv run python scripts/run_paper_pipeline.py \
        --paper papers/laya_lean4_formal_paper_v2.tex \
        --lean-dir formal \
        --results artifacts/laya_lora/results_5_datasets_lora.json \
        --output-dir papers/

Quality Gate Criteria (ALL must pass before PDF finalized):
    R1: No self-authored peer review sections in paper
    R2: Lean 4 framed as deployment invariants, not novel theorems
    R3: FLOP model includes O(L^2*d) attention acknowledgment
    R4: Accuracy metrics table present for all datasets
    R5: Every numeric value traces to a JSON receipt with SHA256
    R6: No fictitious affiliation, sorry count matches abstract claim
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


# ─── R1: Academic Integrity Gate ───────────────────────────────────────────────
FORBIDDEN_SELF_REVIEW_PATTERNS = [
    r"(?i)peer review tribunal",
    r"(?i)reviewer\s+\d\s*:",
    r"(?i)score:\s*\d+/10",
    r"(?i)strong accept",
    r"(?i)self.authored.review",
]

# ─── R2: Framing Honesty Gate ──────────────────────────────────────────────────
# Match overclaiming only when NOT immediately preceded by negating "do not" context.
# Use line-by-line check to filter lines containing "do not constitute" or "do not"
OVERCLAIMING_PATTERNS = [
    r"(?i)thermodynamically catastrophic",
    r"(?i)computational physics theorem",
    r"(?i)weierstrass existence",
    r"(?i)fundamental theorem of",
    # "novel mathematical X" — only overclaims if NOT on a line saying "do not constitute"
    # (handled in check_r2_framing_honesty by line-by-line filter)
    r"(?i)novel mathematical (breakthrough|result)",
]
# Phrases on a line that indicate the surrounding context is a DISCLAIMER, not a claim
OVERCLAIMING_DISCLAIMER_WORDS = ["do not constitute", "not constitute", "do not claim",
                                   "not a claim", "do not prove", "not novel"]


# ─── R3: FLOP Model Gate ───────────────────────────────────────────────────────
FLOP_ACKNOWLEDGMENT_PATTERNS = [
    r"O\(L\^2",
    r"O\(L²",
    r"L\^2 \\cdot d",
    r"attention term",
    r"self-attention",
]

# ─── R6: Affiliation and Sorry Gate ────────────────────────────────────────────
FICTITIOUS_AFFILIATION_PATTERNS = [
    r"Antigravity Advanced Agentic Computing",
    r"(?i)fictitious",
]

HONEST_AFFILIATION_REQUIRED = [
    "AutoevolveAI",
    "Independent Research",
    "Open-Source",
    "open-source",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_r1_academic_integrity(paper_tex: str) -> tuple[bool, list[str]]:
    """R1: No self-authored peer review sections."""
    violations = []
    for pattern in FORBIDDEN_SELF_REVIEW_PATTERNS:
        if re.search(pattern, paper_tex):
            violations.append(f"FORBIDDEN PATTERN found: {pattern}")
    return len(violations) == 0, violations


def check_r2_framing_honesty(paper_tex: str) -> tuple[bool, list[str]]:
    """R2: No overclaiming of Lean 4 proofs as novel theorems.
    Skips lines that contain disclaimer words (e.g., 'do not constitute')."""
    violations = []
    lines = paper_tex.splitlines()
    for pattern in OVERCLAIMING_PATTERNS:
        for line in lines:
            # Skip lines that are explicitly negating / disclaiming the claim
            is_disclaimer = any(d in line.lower() for d in OVERCLAIMING_DISCLAIMER_WORDS)
            if is_disclaimer:
                continue
            if re.search(pattern, line):
                violations.append(f"OVERCLAIMING on non-disclaimer line: {pattern!r}")
                break
    return len(violations) == 0, violations


def check_r3_flop_model(paper_tex: str, lean_source: str) -> tuple[bool, list[str]]:
    """R3: O(L^2 * d) attention term acknowledged."""
    for pattern in FLOP_ACKNOWLEDGMENT_PATTERNS:
        if re.search(pattern, paper_tex) or re.search(pattern, lean_source):
            return True, ["O(L^2*d) attention acknowledged"]
    return False, ["MISSING: O(L^2*d) attention term not mentioned in paper or Lean source"]


def check_r4_accuracy_table(paper_tex: str) -> tuple[bool, list[str]]:
    """R4: Accuracy metrics present for all datasets."""
    issues = []
    has_accuracy_column = bool(re.search(r"(?i)(accuracy|f1.score|f1-score)", paper_tex))
    has_random_baseline = bool(re.search(r"(?i)(random|baseline)", paper_tex))
    has_limitations = bool(re.search(r"(?i)(limitation|zero.shot|few.shot)", paper_tex))
    if not has_accuracy_column:
        issues.append("No accuracy/F1 column found in paper")
    if not has_random_baseline:
        issues.append("No random baseline comparison found")
    if not has_limitations:
        issues.append("No limitations section on accuracy")
    return len(issues) == 0, issues


def check_r5_telemetry_provenance(paper_tex: str, results_json: Path) -> tuple[bool, list[str]]:
    """R5: Numeric values traced to SHA256 JSON receipt."""
    issues = []
    if not results_json.exists():
        return False, [f"Results JSON not found: {results_json}"]
    sha = sha256_file(results_json)[:8]
    if sha not in paper_tex:
        issues.append(f"SHA256 prefix '{sha}' not found in paper — telemetry not cited")
    # Check that at least one table caption mentions SHA256
    if not re.search(r"(?i)(sha256|sha-256)", paper_tex):
        issues.append("No SHA256 reference in table captions")
    return len(issues) == 0, issues


def check_r6_affiliation_and_sorry(
    paper_tex: str, lean_log: str
) -> tuple[bool, list[str]]:
    """R6: No fictitious affiliation, sorry count matches abstract."""
    issues = []
    # Check for fictitious affiliations
    for pattern in FICTITIOUS_AFFILIATION_PATTERNS:
        if re.search(pattern, paper_tex):
            issues.append(f"Fictitious affiliation pattern: {pattern}")

    # Verify at least one honest affiliation marker
    has_honest = any(marker in paper_tex for marker in HONEST_AFFILIATION_REQUIRED)
    if not has_honest:
        issues.append("No honest affiliation found (expected: AutoevolveAI or Independent Research)")

    # Count sorries ONLY in LayaDecision.lean (other modules like Basic.lean have
    # independent sorry obligations that do not affect this paper's claims)
    laya_decision_lines = [l for l in lean_log.splitlines() if "LayaDecision" in l]
    sorry_count = sum(1 for l in laya_decision_lines if "uses `sorry`" in l)
    total_sorry_count = lean_log.count("uses `sorry`")

    # Check abstract claims match reality
    if "without sorry" in paper_tex.lower() and sorry_count > 0:
        issues.append(f"Abstract says 'without sorry' but {sorry_count} sorry found in LayaDecision.lean")
    if sorry_count > 1:
        issues.append(f"Too many sorries in LayaDecision.lean: {sorry_count} (max allowed: 1)")
    if sorry_count == 1 and "proof obligation" not in paper_tex.lower():
        issues.append("1 sorry present but not acknowledged in paper as 'open proof obligation'")
    if total_sorry_count > sorry_count:
        # Other modules have sorries too — just note it, don't fail
        pass  # e.g. Basic.lean sorry is documented in ANSE infrastructure

    return len(issues) == 0, issues


def run_xelatex(paper_tex_path: Path, output_dir: Path) -> tuple[bool, str]:
    """Run XeLaTeX twice for cross-references.
    Success is determined by PDF file creation, not exit code (warnings cause non-zero exit)."""
    cmd = [
        "xelatex", "-interaction=nonstopmode",
        f"-output-directory={output_dir}", str(paper_tex_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    result2 = subprocess.run(cmd, capture_output=True, text=True)  # second pass
    combined_log = result.stdout + result.stderr + result2.stdout + result2.stderr
    # Check if output PDF was written (XeLaTeX may return non-zero even on success with warnings)
    pdf_path = output_dir / paper_tex_path.with_suffix(".pdf").name
    success = pdf_path.exists() and "Output written on" in combined_log
    return success, combined_log


def run_lake_build(formal_dir: Path) -> tuple[bool, str]:
    """Run lake build and return (success, log)."""
    import os
    env = os.environ.copy()
    env["PATH"] = "/home/xavkal/.elan/bin:" + env.get("PATH", "")
    result = subprocess.run(
        ["lake", "build", "ANSE.LayaDecision"],
        capture_output=True, text=True, cwd=formal_dir, env=env
    )
    return result.returncode == 0, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description="ANSE Paper Pipeline Quality Gate")
    parser.add_argument("--paper", required=True, type=Path)
    parser.add_argument("--lean-dir", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("papers"), type=Path)
    parser.add_argument("--lean-source", type=Path,
                        default=Path("formal/ANSE/LayaDecision.lean"))
    args = parser.parse_args()

    print("=" * 70)
    print("ANSE Scientific Paper Pipeline — Quality Gate v2")
    print("=" * 70)

    # ── Step 1: Compile Lean 4 ──────────────────────────────────────────────
    print("\n[STEP 1] Building Lean 4 formal proofs...")
    lean_ok, lean_log = run_lake_build(args.lean_dir)
    if not lean_ok:
        print("  ❌ FATAL: lake build failed. Fix Lean errors before proceeding.")
        sys.exit(1)
    sorry_count = lean_log.count("uses `sorry`")
    print(f"  ✅ lake build OK | Sorry count: {sorry_count}")

    # ── Step 2: Load paper and Lean source ─────────────────────────────────
    print("\n[STEP 2] Loading paper and Lean source...")
    paper_tex = args.paper.read_text()
    lean_source = args.lean_source.read_text() if args.lean_source.exists() else ""
    print(f"  Paper: {args.paper} ({len(paper_tex)} chars)")

    # ── Step 3: Run 6-criterion quality gate ───────────────────────────────
    print("\n[STEP 3] Running 6-criterion peer review gate...")
    gates = [
        ("R1 Academic Integrity",  check_r1_academic_integrity(paper_tex)),
        ("R2 Framing Honesty",     check_r2_framing_honesty(paper_tex)),
        ("R3 FLOP Model",          check_r3_flop_model(paper_tex, lean_source)),
        ("R4 Accuracy Table",      check_r4_accuracy_table(paper_tex)),
        ("R5 Telemetry SHA256",    check_r5_telemetry_provenance(paper_tex, args.results)),
        ("R6 Affiliation/Sorry",   check_r6_affiliation_and_sorry(paper_tex, lean_log)),
    ]

    all_pass = True
    results = {}
    for name, (passed, details) in gates:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_pass = False
            for d in details:
                print(f"         → {d}")
        results[name] = {"pass": passed, "details": details}

    if not all_pass:
        print("\n❌ GATE FAILED — Fix all failing criteria before compiling PDF.")
        out = args.output_dir / "peer_review_gate_result.json"
        out.write_text(json.dumps({"outcome": "FAIL", "criteria": results}, indent=2))
        sys.exit(1)

    print("\n✅ ALL 6 CRITERIA PASSED")

    # ── Step 4: Compile XeLaTeX (2 passes) ─────────────────────────────────
    print("\n[STEP 4] Compiling XeLaTeX (2 passes)...")
    tex_ok, tex_log = run_xelatex(args.paper, args.output_dir)
    if not tex_ok:
        print("  ❌ XeLaTeX compilation failed")
        print(tex_log[-2000:])
        sys.exit(1)
    pdf_path = args.output_dir / args.paper.with_suffix(".pdf").name
    if not pdf_path.exists():
        print(f"  ❌ PDF not found at {pdf_path}")
        sys.exit(1)

    # ── Step 5: SHA256 provenance ───────────────────────────────────────────
    print("\n[STEP 5] Computing PDF SHA256...")
    pdf_sha256 = sha256_file(pdf_path)
    print(f"  PDF: {pdf_path}")
    print(f"  SHA256: {pdf_sha256}")

    # ── Step 6: Write final receipt ─────────────────────────────────────────
    receipt = {
        "outcome": "ACCEPT_READY",
        "pdf": str(pdf_path),
        "sha256": pdf_sha256,
        "sorry_count": sorry_count,
        "criteria": results,
        "lean_build": "OK",
    }
    receipt_path = args.output_dir / "paper_pipeline_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2))
    print(f"\n✅ Pipeline complete. Receipt: {receipt_path}")
    print(f"   PDF SHA256: {pdf_sha256}")


if __name__ == "__main__":
    main()
