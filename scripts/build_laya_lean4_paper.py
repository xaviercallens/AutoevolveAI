#!/usr/bin/env python3
"""
Build pipeline for the Lean 4 Formalized Laya Paper.

Steps:
  1. (Optional) Verify Lean 4 proofs compile via `lake build`
  2. Compile XeLaTeX paper (2 passes for cross-references)
  3. Check for Unicode missing characters
  4. Output SHA256 hash of final PDF

Usage:
  uv run python scripts/build_laya_lean4_paper.py [--skip-lean]
"""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = ROOT / "papers"
FORMAL_DIR = ROOT / "formal"
TEX_FILE = PAPER_DIR / "laya_lean4_formal_paper.tex"
PDF_FILE = PAPER_DIR / "laya_lean4_formal_paper.pdf"
LOG_FILE = PAPER_DIR / "laya_lean4_formal_paper.log"


def run_cmd(cmd: list[str], cwd: Path, label: str) -> bool:
    """Run a command and return True on success."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        print(f"FAILED (exit code {result.returncode})")
        if result.stderr:
            print(result.stderr[-2000:])
        if result.stdout:
            print(result.stdout[-2000:])
        return False
    print("SUCCESS")
    return True


def compile_xelatex() -> bool:
    cmd = [
        "xelatex", "-interaction=nonstopmode",
        f"-output-directory={PAPER_DIR}", str(TEX_FILE),
    ]
    for p in (1, 2):
        if not run_cmd(cmd, ROOT, f"XeLaTeX pass {p}"):
            return False
    return True


def check_unicode() -> list[str]:
    if not LOG_FILE.exists():
        return ["Log file not found"]
    errs = []
    with open(LOG_FILE, errors="replace") as f:
        for line in f:
            if "Missing character:" in line:
                errs.append(line.strip())
    return errs


def sha256(fp: Path) -> str:
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    skip_lean = "--skip-lean" in sys.argv
    print("=" * 60)
    print("  Laya Lean 4 Formal Paper Build Pipeline")
    print("=" * 60)

    if not skip_lean:
        if not run_cmd(["lake", "build"], FORMAL_DIR, "Lean 4 Compilation"):
            print("\n❌ Lean 4 FAILED")
            sys.exit(1)
        print("✅ Lean 4 proofs verified")
    else:
        print("⏭️  Skipping Lean 4 (--skip-lean)")

    if not compile_xelatex():
        print("\n❌ XeLaTeX FAILED")
        sys.exit(1)
    print("✅ XeLaTeX succeeded")

    errs = check_unicode()
    if errs:
        print(f"\n⚠️  {len(errs)} Unicode issues:")
        for e in errs[:10]:
            print(f"  {e}")
    else:
        print("✅ No Unicode issues")

    if PDF_FILE.exists():
        s = sha256(PDF_FILE)
        kb = PDF_FILE.stat().st_size / 1024
        print(f"\n{'='*60}")
        print(f"  PDF: {PDF_FILE}")
        print(f"  Size: {kb:.1f} KB | SHA256: {s}")
        print(f"{'='*60}")
    else:
        print("\n❌ PDF not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
