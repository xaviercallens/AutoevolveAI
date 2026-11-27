"""Assemble results/proposal4/2026-10-27/M3/result.json from the run outputs, with sha256 of every code/data/log/Lean file.

usage: python -I make_result.py M3_DIR LEAN_DIR STATUS
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    m3 = Path(sys.argv[1]).resolve()
    lean = Path(sys.argv[2]).resolve()
    status = sys.argv[3]
    arb = json.loads((m3 / "data" / "arb_results.json").read_text())
    flo = json.loads((m3 / "data" / "float_results.json").read_text())
    ext = json.loads((m3 / "data" / "extra_results.json").read_text())
    gate = json.loads((m3 / "logs" / "gate_summary.json").read_text())
    files = {}
    for d in (m3 / "code", m3 / "data", m3 / "logs", lean):
        for p in sorted(d.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                files[str(p.relative_to(m3.parents[3]))] = sha(p)
    out = {
        "id": "M3",
        "status": status,
        "paper": "Luo & Wei, arXiv 2610.31456v1 (read in full via alphaXiv get_paper_content, 6023 lines)",
        "kappa_star": {
            "ewald_arb_bracket": arb["kappa_star_bracket_ewald"][2:],
            "direct_sum_arb_bracket": arb["kappa_star_bracket_direct"],
            "eq14_mpmath_dps40": flo["kappa_star_eq14_mpmath"],
            "ieee_double_direct": flo["kappa_star_double_direct"],
            "paper_printed": "1.71792186846990 (Thm 6.1); 1.717921868469903 < kappa* < 1.717921868469904 (A.9)",
        },
        "lemmaA6_G_values": arb["G_values"],
        "lemmaA6_claims": {k: arb[k] for k in ("A6_claim_lower", "A6_claim_upper")},
        "lemmaA6_paper_truncation": {k: v for k, v in ext.items() if k.startswith("A6_")},
        "lemmaA5_arb": arb["lemmaA5"],
        "lemmaA1_arb": arb["lemmaA1"],
        "lemmaA3_A4_endpoints": {k: v for k, v in ext.items() if k.startswith("A4_e")},
        "counts": {k: v for k, v in ext.items() if k.startswith(("A3_", "A4_1", "A4_c", "N_", "M_"))},
        "lean_gate": gate,
        "sha256": files,
    }
    (m3 / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("wrote", m3 / "result.json", len(files), "files hashed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
