"""Write ledger/sources/MANIFEST.md: how to re-fetch the arXiv texts behind the Tier-L source hashes and re-check them.

The full texts are not redistributed (arXiv licences differ per paper). The manifest records the arXiv identifier, the
sha256 of the PDF that was fetched on 2026-10-25, the sha256 of its default `pdftotext` extraction (this is the
`source_sha256` in data/claim_*.json), and the commands to reproduce both.
Usage: python -I make_sources_manifest.py SRC_DIR   (SRC_DIR holds src_luowei/ and src_dengluo/)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ITEMS = [("src_luowei", "2302.05042v1", "S. Luo, J. Wei, On lattice hexagonal crystallization for non-monotone potentials"),
         ("src_dengluo", "2411.17199v1", "K. Deng, S. Luo, Minimizing lattice energy and hexagonal crystallization")]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    src = Path(sys.argv[1])
    claimed = {json.loads(p.read_text())["source_sha256"] for p in (HERE / "data").glob("claim_*.json")}
    (HERE / "ledger/sources").mkdir(parents=True, exist_ok=True)
    lines = ["# Tier-L source texts (not redistributed)", "",
             "The Tier-L ledger rows quote two arXiv papers. Their full texts are not bundled; this file lets a reader re-fetch and re-check them.",
             "Fetch `https://arxiv.org/pdf/<id>v1`, compare the PDF hash, then run `pdftotext <id>.pdf <id>.txt` (poppler 22.02.0, default options) "
             "and compare the text hash with `source_sha256` in `data/claim_*.json`.", "",
             "| arXiv id | paper | pdf sha256 | pdftotext sha256 | text hash is a claim source_sha256 | re-extraction identical |", "|---|---|---|---|---|---|"]
    for d, aid, title in ITEMS:
        pdf, txt = src / d / f"{aid}.pdf", src / d / f"{aid}.txt"
        out = HERE / "tmp_check.txt"
        subprocess.run(["pdftotext", str(pdf), str(out)], check=True)
        redo = sha(out)
        out.unlink()
        in_claims = "sha256:" + sha(txt) in claimed
        lines.append(f"| arXiv:{aid} | {title} | `{sha(pdf)}` | `{sha(txt)}` | {'yes' if in_claims else 'NO'} | {'yes' if redo == sha(txt) else 'NO'} |")
    lines += ["", "Local copies of the fetched files on the machine that produced the paper: "
              "`/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/src_luowei/` and `.../src_dengluo/`.",
              "The ledger quotations were copied programmatically from this default `pdftotext` output (`run_citation.py` next to those folders)."]
    (HERE / "ledger/sources/MANIFEST.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
