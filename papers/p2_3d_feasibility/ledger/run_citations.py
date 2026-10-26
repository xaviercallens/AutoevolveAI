"""Build Tier-L claim files from pdftotext output of the arXiv PDFs and run the Elenchus citation gate on each.

Quotations are located programmatically in the source text (first line to last line), never retyped. Statements that are
not theorem-like (remarks, abstracts, status sentences) cannot enter Tier L; for them this script only checks that the
quotation is verbatim in the source text (same normalisation as the gate) and records a flag, and the ledger files them at Tier C.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I run_citations.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path("/home/callensxavier_gmail_com/p2-b3-sources")
GATE = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/citation_check.py"
OUT = HERE.parent / "data"
CL = HERE / "citations"


def norm(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).replace("­", "")
    t = re.sub(r"-\s*\n\s*", "", t)
    return re.sub(r"\s+", "", t)


def sha(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def lines_between(txt: str, start: str, end: str) -> str:
    """Return the source text from the first line containing `start` to the first later line containing `end` (inclusive)."""
    ls = (SRC / txt).read_text().split("\n")
    i = next(k for k, l in enumerate(ls) if start in l)
    j = next(k for k in range(i, len(ls)) if end in ls[k])
    return "\n".join(ls[i:j + 1])


GATED = {
    "mn_thm1": dict(txt="mn.txt", sid="arXiv:2610.29732v1 (C. B. Muratov, M. Novaga), Theorem 1, p. 4", kind="theorem",
                    start="Theorem 1. For every Bravais lattice", end="up to an orthogonal transformation",
                    hyp=["L ranges over Bravais lattices in R^3 of covolume one",
                         "E(L) is the Born Coulombic lattice energy, equal to the continued Epstein zeta function E(L, 1/2), eqs. (6)-(9)",
                         "L_B is the covolume-one BCC lattice of eq. (10)"],
                    used="B3 section 2: lattice-restricted bcc optimality; the non-periodic problem is not covered"),
    "mn_prop6": dict(txt="mn.txt", sid="arXiv:2610.29732v1 (C. B. Muratov, M. Novaga), Proposition 6, p. 13", kind="proposition",
                     start="Proposition 6. The bisection described above terminates", end="with no",
                     hyp=["the covering is of the rectangle (34) in the reduced Iwasawa parametrization of the Bravais lattices",
                          "the terminal boxes are closed boxes certified by arithmetic in one of the four tests (R), (C), (B), (E)"],
                     used="B3 section 8: 46 414 boxes at relative gap 6.2e-5 as the calibration scale of a certificate"),
    "lw_thm11": dict(txt="lw.txt", sid="arXiv:2610.31456v1 (S. Luo, J. Wei), Theorem 1.1 item (2), p. 2", kind="theorem",
                     start="(2) If 0 < κ < κ∗ , then", end="to BCC lattice.",
                     hyp=["L is a three-dimensional lattice with |L| = 1 (covolume one)", "kappa > 0 is the Yukawa screening parameter",
                          "E_kappa(L) is the Yukawa lattice energy of eq. (1.3); L_B is the BCC lattice and kappa_* the threshold of Theorem 1.1"],
                     used="B3 section 2: Bravais-lattice Yukawa interpolation, lattice-only"),
    "rs_thm1": dict(txt="rs.txt", sid="arXiv:1307.2805v5 (N. Rougerie, S. Serfaty), Theorem 1, p. 12", kind="theorem",
                    start="is achieved and is finite. Moreover, there exists a sequence", end="in A1 such that",
                    hyp=["d >= 2 is the dimension", "A_1 is the class of admissible electric fields of Definition 2.1 with background density 1",
                         "W is the renormalized (jellium) energy defined in (2.16)-(2.17) of the source"],
                    used="B3 section 3, step G1: reduction to periodic configurations exists in every dimension d >= 2 for the smeared energy"),
}

# (key, txt, sid, start line, end line, role)
PROSE = {
    "bl_open": ("bl.txt", "arXiv:1504.01153v2 (X. Blanc, M. Lewin), section 2.6, p. 19",
                "numerical simulations presented in", "Proving this fact is still an open problem."),
    "bl_ln": ("bl.txt", "arXiv:1504.01153v2 (X. Blanc, M. Lewin), section 2.6, p. 19",
              "in dimension d = 3 [37, 115]. Using an argument due to Onsager", "for any ρ > 0."),
    "lewin_c1": ("lew.txt", "arXiv:2202.09240v2 (M. Lewin), Remark 19, p. 22", "In d = 3 one obtains c1", "1.4508 which is surprisingly close to the"),
    "ai_gersho": ("ai.txt", "arXiv:2610.28547v1 (A. D. Aydin, M. Iacobelli), abstract and p. 4",
                  "Note that these results concern the restricted minimization problem over lattices", "which remains open for d ≥ 3."),
    "rs_remark_b2": ("rs.txt", "arXiv:1307.2805v5 (Rougerie, Serfaty), Remark B.2, p. 67",
                     "Remark B.2. The fact that Lemma 3.2", "contrarily to what happens for d = 2 as proven in [SS3]."),
    "mn_harder": ("mn.txt", "arXiv:2610.29732v1 (Muratov, Novaga), Section 7, p. 14",
                  "minimizes the renormalized Coulomb energy among configurations without any periodicity assumption.",
                  "This is a substantially harder three-dimensional crystallization problem"),
    "mn_gap": ("mn.txt", "arXiv:2610.29732v1 (Muratov, Novaga), p. 3", "chief difficulty in proving such a result is a very small relative energy gap of 6.2",
               "which necessitates a very accurate evaluation of the Coulombic energy."),
    "hm_abstract": ("hm.txt", "arXiv:math/9811079v3 (T. C. Hales, S. McLaughlin), abstract only",
                    "This article gives a proof of Fejes", "at least the volume of a regular dodecahedron of unit inradius."),
}


def main() -> int:
    CL.mkdir(exist_ok=True)
    report: dict[str, object] = {}
    for key, g in GATED.items():
        src = (SRC / g["txt"]).read_bytes()
        quote = lines_between(g["txt"], g["start"], g["end"])
        claim = {"source_id": g["sid"], "source_sha256": sha(src), "kind": g["kind"], "quote": quote, "hypotheses": g["hyp"],
                 "statement_match": "match", "used_for": g["used"]}
        p = CL / f"claim_{key}.json"
        p.write_text(json.dumps(claim, indent=1, ensure_ascii=False))
        r = subprocess.run([sys.executable, "-I", GATE, str(p), str(SRC / g["txt"])], capture_output=True, text=True)
        report[key] = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "claim": claim}
        print(key, "rc", r.returncode, json.loads(r.stdout)["verdict"] if r.stdout.strip() else r.stderr)
    for key, (txt, sid, start, end) in PROSE.items():
        text = (SRC / txt).read_text()
        quote = lines_between(txt, start, end)
        found = norm(quote) in norm(text)
        report[key] = {"verbatim_in_source": found, "kind": "remark-or-status (not theorem-like; cannot enter Tier L)", "source_id": sid,
                       "source_sha256": sha((SRC / txt).read_bytes()), "quote": quote}
        print(key, "verbatim", found)
    (OUT / "citation_check.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    ok = all(v.get("rc", 0) == 0 for v in report.values()) and all(v.get("verbatim_in_source", True) for v in report.values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
