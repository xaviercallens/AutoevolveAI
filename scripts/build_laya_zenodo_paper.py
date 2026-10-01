#!/usr/bin/env python3
"""
Automated LaTeX Builder and PDF Compiler for Laya-LoRA Zenodo Publication Paper.
Compiles papers/laya_lora_zenodo_paper.tex into papers/laya_lora_zenodo_paper.pdf using pdflatex.
Performs 2 passes for cross-references, table resolution, and hyperlinks.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BuildLayaPaper")

PAPERS_DIR = Path("papers")
PAPERS_DIR.mkdir(parents=True, exist_ok=True)
TEX_FILE = PAPERS_DIR / "laya_lora_zenodo_paper.tex"
PDF_FILE = PAPERS_DIR / "laya_lora_zenodo_paper.pdf"


def compile_laya_paper() -> bool:
    if not TEX_FILE.exists():
        logger.error("TeX file not found at %s", TEX_FILE)
        return False

    logger.info("Compiling %s with pdflatex (Pass 1)...", TEX_FILE)
    cmd = ["pdflatex", "-interaction=nonstopmode", "-output-directory=papers", str(TEX_FILE)]
    p1 = subprocess.run(cmd, capture_output=True, text=True)
    if p1.returncode != 0:
        logger.error("pdflatex Pass 1 failed with return code %d", p1.returncode)
        logger.error("Output tail:\n%s", p1.stdout[-1500:])
        return False

    logger.info("Compiling with pdflatex (Pass 2 for cross-references & citations)...")
    p2 = subprocess.run(cmd, capture_output=True, text=True)
    if p2.returncode != 0:
        logger.error("pdflatex Pass 2 failed with return code %d", p2.returncode)
        logger.error("Output tail:\n%s", p2.stdout[-1500:])
        return False

    if PDF_FILE.exists():
        size_kb = PDF_FILE.stat().st_size / 1024.0
        logger.info("✅ Compilation successful! PDF created: %s (%.1f KB)", PDF_FILE.resolve(), size_kb)
        return True
    else:
        logger.error("PDF file %s was not found after compilation", PDF_FILE)
        return False


if __name__ == "__main__":
    ok = compile_laya_paper()
    sys.exit(0 if ok else 1)
