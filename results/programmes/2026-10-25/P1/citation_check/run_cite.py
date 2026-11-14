"""P1 REVISE (audit N5): run Elenchus citation_check.py on pdftotext PRIMARY text of the arXiv PDFs for the
theorem-type L rows. Quotes are cut from the pdftotext output between two anchor strings (never retyped), so a
quote cannot drift from the source; the claim's `statement_match` is the agent's judgment after reading (see REVISION.md).
Controls: (neg-1) the ledger's own rejoined excerpt (subscripts rewritten to ASCII) must be REFUSED as non-verbatim;
(neg-2) a one-word tamper of a real quote must be REFUSED; (pos) the real quotes must be ACCEPTED.
Usage: python -I run_cite.py OUT_JSON
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/citation_check.py"
SRC = {"ss": HERE / "src_ss/ss2012_full.txt", "bs": HERE / "src_bs/bs2018_full.txt"}
LEDGER_EXC = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/papers/prog_sandier_serfaty_audit/ledger/sources/excerpts.json")

# (id, source key, kind, source_id, start anchor, end anchor, hypotheses)
ITEMS = [
    ("ss_thm1_3_4", "ss", "theorem", "arXiv:1011.4617v2 Theorem 1 items 3 and 4 (pdf p.5)",
     "3. minA1 WU is achieved and finite", "of sidelength", ["W as in Definition 1.2 over A_1", "{U_R} satisfies (1.4)-(1.5)"]),
    ("ss_thm2", "ss", "theorem", "arXiv:1011.4617v2 Theorem 2 (pdf p.5)",
     "Theorem 2. Let L = ", "by the triangular lattice", ["Lambda a lattice with j_Lambda in A_m"]),
    ("ss_prop31", "ss", "proposition", "arXiv:1011.4617v2 Proposition 3.1 (pdf p.26)",
     "Proposition 3.1. Assume", "(3.2)", ["Lambda = Zu + Zv and j as above", "{U_R} satisfying (1.4), (1.5)"]),
    ("ss_prop49", "ss", "proposition", "arXiv:1011.4617v2 Proposition 4.9 (pdf p.41)",
     "Proposition 4.9. Assume U", "(4.12)", ["U open in R^2", "nu = 2 pi sum delta_p, Lambda finite in U-hat", "curl j = nu - m, div j = 0, m in L^infinity"]),
    ("bs_thm15", "bs", "theorem", "arXiv:1404.4485v5 Theorem 1.5 (pdf p.3)",
     "Theorem 1.5. There exists", "the triangular lattice of density one.", ["E_log(n) minimal log energy of n points on S^2", "W, A_1 as in BS2018 Section 2"]),
]


def cut(text: str, a: str, b: str) -> str:
    i = text.index(a)
    j = text.index(b, i) + len(b)
    return text[i:j]


def run(claim: dict, src: Path) -> dict:
    cf = HERE / "tmp_claim.json"
    cf.write_text(json.dumps(claim, ensure_ascii=False))
    r = subprocess.run([sys.executable, "-I", TOOL, str(cf), str(src)], capture_output=True, text=True)
    cf.unlink()
    try:
        verdict = json.loads(r.stdout)["verdict"]
    except (ValueError, KeyError):
        verdict = "NO_VERDICT: " + (r.stderr.strip()[:200] or r.stdout.strip()[:200])
    return {"exit": r.returncode, "verdict": verdict}


def claim_of(quote: str, kind: str, sid: str, hyps: list[str], src: Path) -> dict:
    return {"source_sha256": "sha256:" + hashlib.sha256(src.read_bytes()).hexdigest(), "kind": kind, "quote": quote,
            "hypotheses": hyps, "source_id": sid, "statement_match": "match"}


def main() -> int:
    out: dict[str, object] = {"sources": {k: {"file": str(v), "sha256": hashlib.sha256(v.read_bytes()).hexdigest()} for k, v in SRC.items()},
                              "positive": {}, "negative": {}}
    quotes: dict[str, str] = {}
    for cid, key, kind, sid, a, b, hyps in ITEMS:
        text = SRC[key].read_text()
        # a, b appear in the raw text with the extraction's own line breaks; match on the whitespace-flattened view
        flat = " ".join(text.split())
        quote = cut(flat, " ".join(a.split()), " ".join(b.split()))
        quotes[cid] = quote
        res = run(claim_of(quote, kind, sid, hyps, SRC[key]), SRC[key])
        res["quote"] = quote
        out["positive"][cid] = res  # type: ignore[index]
    # neg-1: the ledger's rejoined excerpts (ASCII subscripts) are not verbatim primary text
    exc = json.loads(LEDGER_EXC.read_text())
    for cid, key, kind, sid, a, b, hyps in ITEMS:
        led = {"ss_thm1_3_4": "ss_thm1", "ss_thm2": "ss_conj", "ss_prop31": "ss_prop31", "ss_prop49": "ss_prop49", "bs_thm15": "bs_thm15"}[cid]
        res = run(claim_of(exc[led]["text"], kind, sid, hyps, SRC[key]), SRC[key])
        out["negative"][f"{cid}__ledger_rejoined_excerpt"] = res  # type: ignore[index]
    # neg-2: tamper one word of a real quote
    q = quotes["ss_thm1_3_4"].replace("is achieved and finite", "is achieved and infinite")
    out["negative"]["ss_thm1_3_4__tampered_word"] = run(claim_of(q, "theorem", "arXiv:1011.4617v2 Theorem 1", ["W as in Definition 1.2"], SRC["ss"]), SRC["ss"])  # type: ignore[index]
    q2 = quotes["bs_thm15"].replace("C ≤ CBHS", "C ≥ CBHS") if "C ≤ CBHS" in quotes["bs_thm15"] else quotes["bs_thm15"] + " X"
    out["negative"]["bs_thm15__tampered_inequality"] = run(claim_of(q2, "theorem", "arXiv:1404.4485v5 Theorem 1.5", ["E_log(n) on S^2"], SRC["bs"]), SRC["bs"])  # type: ignore[index]
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: {c: v["verdict"] for c, v in d.items()} for k, d in out.items() if k in ("positive", "negative")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
