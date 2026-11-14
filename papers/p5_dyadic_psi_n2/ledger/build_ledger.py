"""Build the Elenchus claim ledger for the DH-Psi2 paper (papers/p5_dyadic_psi_n2).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (citation L, argument C, numeric X).
There is NO Lean in this paper, so there are no Tier A rows and no LEDGER_UNAUDITED_TIER_A flag is expected; the
honest expected gate state is exit 0 with no findings (which says only that the bookkeeping holds).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, a separate AI agent instance, not a person).
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
AUD = DATA / "audit"
LOGS = DATA / "logs"
SRC_COMMIT = "1e29c538f2ceacd0e644fc990cfba32ce45fa0d7"
PREPRINT = "doi:10.5281/zenodo.23232389"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def fref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def paper_copy_hash_check() -> dict:
    """Check every files_sha256 entry of the producer's result.json against the copy in this paper's data/.

    The lane layout maps data/X -> data/X (paper) and RESULT.md, code/*, logs/* -> data/RESULT.md etc.; the one entry
    that cannot be checked is code/psi_exhaust, the untracked -march=native binary that is deliberately not shipped
    (auditor correction 4)."""
    r = json.loads((DATA / "result.json").read_text())
    ok, missing, bad = 0, [], []
    for rel, h in r["files_sha256"].items():
        q = DATA / (rel[len("data/"):] if rel.startswith("data/") else rel)
        if not q.exists() and rel.endswith(".sh"):
            q = q.with_name(q.name + ".txt")  # shell scripts travel as .sh.txt (the bundler keeps no .sh suffix)
        if not q.exists():
            missing.append(rel)
        elif sha(q.read_bytes()) != h:
            bad.append(rel)
        else:
            ok += 1
    out = {"entries": len(r["files_sha256"]), "match": ok, "missing": missing, "mismatch": bad}
    text = json.dumps(out, indent=1) + "\n"
    (HERE / "hash_check_paper_copy.txt").write_text(text)
    return out


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    hc = paper_copy_hash_check()
    assert hc["mismatch"] == [] and hc["missing"] == ["code/psi_exhaust"], hc
    d = DATA
    c = [
        rec("DHP-L-0001", "L", "citation",
            "Definitions used, from the dyadic triangular Hilbert preprint (Callens, " + PREPRINT + "): eq. (LI) for L_I; Proposition (finite reduction) "
            "Lambda(F) = |T(F)| + H(F) for step inputs at resolution N, with the trace form (eq. (trace)); Proposition (level) |T| + |L_000| <= 1 and "
            "sum over level-1 triples <= 1 at N = 2, giving Psi <= 4; Conjecture 7.1 (label conj:psi): H(F) + 3|T(F)| <= 3 prod ||F_v||_3 for all real inputs; "
            "for sign inputs every norm is 1 and the claim is Psi := H + 3|T| <= 3. The paper's own earlier exhaustive result: max R = 2 at resolution 2 (night lane 2026-10-07).",
            [], cite(PREPRINT, "eq. (LI), Prop. finite, eq. (trace), Prop. level, Conjecture 7.1",
                     "Our own earlier preprint, read by the producer and by the auditor, who re-derived the definitions as a literal integral",
                     "own work, taken as stated; no erratum is needed or implied")),
        rec("DHP-C-0001", "C", "argument",
            "Definitions at N = 2 (n = 4) in units of 1/64: S_w(F) = w |T| + |L_0| + 2 sum over the 4 admissible level-1 triples |L_1|, with T = sum_ijk F0[i,j]F1[j,k]F2[k,i], "
            "level-0 Haar h = +1 on cells 0,1 and -1 on cells 2,3, level-1 Haar +1 on the left (even) cell, prefactor 2^l, weights 1/1/2 as stated; Psi <= 3 iff S_3 <= 192. "
            "Re-derived by the AI auditor with an evaluator that computes eq. (LI) as a literal integral in exact Fractions on a refined grid (no use of eq. (trace) or producer code): "
            "agrees with the producer's direct_value and with the independently authored h5_exact on 3000/3000 random sign inputs (w_T = 1, 3, 4), 3000/3000 Haar-free, 300/300 integer inputs; "
            "constant input T=1,H=0,R=1,Psi=3; seed g: T=1/2,H=3/2,R=2,Psi=3; N=1 exhaustive (2^12 inputs) max R = 1, max Psi = 3; "
            "mutation power: level-1 weight 1, odd XOR class, coarse Haar at level 1 each disagree with direct_value on 181, 155, 148 of 200 inputs.",
            ["DHP-L-0001"],
            arg("C-exact-rational", "aud_tests_3000.json (auditor), AUDIT.md section 1; producer cross-check data/controls.json (2000/2000 direct_value vs h5_exact).",
                [AUD / "aud_tests_3000.json", AUD / "aud_eval.py", AUD / "aud_tests.py", d / "controls.json"], "aud_eval.py (Fractions); psi_exhaust.py direct_value; h5_exact.py (read-only, not shipped)")),
        rec("DHP-C-0002", "C", "argument",
            "The two reductions used by both producer enumerations are exact identities (proved in AUDIT.md section 3). (i) Sign fix: every term is trilinear in (F0,F1,F2), so F0 -> -F0 and F1 -> -F1 "
            "each negate every term and leave every |term| and every max over F2 unchanged; fixing F0[0,0] = F1[0,0] = +1 loses nothing and leaves 2^15 * 2^15 = 2^30 pairs. "
            "(ii) l1 reduction: for fixed (F0,F1) each term is <c_t,F2> (positive weights absorbed); max over F2 of sum_t |<c_t,F2>| = max over s of max over F2 of <sum_t s_t c_t, F2> (|a| = max_s s.a, swap of finite maxima) "
            "= max over s in {+-1}^6 of ||sum_t s_t c_t||_1, and s -> -s fixes s_0 = +1. Also confirmed empirically without either reduction by the auditor's third enumeration (DHP-C-0004) and by "
            "brute-force checks of (ii) against a literal max over all 2^16 F2 (Python 300 random pairs per mode x 5; C 200 + 100 + 100).",
            [], arg("C-proof", "Short exact proofs (AUDIT.md section 3); brute-force agreement in data/controls.json and data/c_enum/bruteforce_*.json.",
                    [PAPER / "AUDIT.md", d / "controls.json", d / "c_enum" / "bruteforce_PSI_h0.json"], "none (algebraic argument) plus brute-force pairs")),
        rec("DHP-C-0003", "C", "argument",
            "Producer enumerations over all 2^30 reduced (F0,F1) pairs, five modes (PSI, R, PLANT4, HF_R, HF_PSI): Python float32 kernel (psi_exhaust.py; matmul exact under a guard that every partial sum < 2^24; "
            "160 chunks, contiguous F0 coverage [0, 32768)) and integer-only C (psi_exhaust.c, Gray-code order, no floating point). The two are independent implementations that SHARE the sign fix and the l1 reduction. "
            "For Psi: max S = 192 (Psi = 3 exactly), 0 pairs above 192, 4,608 pairs attain 192; the full histograms of max_{F2} S over 2^30 pairs are identical between the two enumerations in all five modes. "
            "Every per-F0 argmax (32,768 per mode) was rechecked by direct_value and by h5_exact (all agree) and the C argmax by a literal triple sum.",
            ["DHP-C-0001", "DHP-C-0002"],
            arg("C-exact-integer", "data/summary.json (hist_identical, max_identical, violations_identical true in all modes); data/c_enum/*.json; data/chunks/*.json (160).",
                [d / "summary.json", d / "c_enum" / "PSI_h0.json", d / "c_enum" / "PSI_h1.json", d / "chunks" / "PSI_00000_01024.json", d / "code" / "psi_exhaust.c", d / "code" / "psi_exhaust.py"],
                "psi_exhaust.py (numpy float32 under 2^24 guard); psi_exhaust.c (gcc -O3 -march=native, integers)")),
        rec("DHP-C-0004", "C", "argument",
            "The auditor's third enumeration (gauge_enum.c, integer only, written independently) uses neither producer reduction: the exact diagonal sign gauge (F0,F1,F2) -> (D0 F0 D1, D1 F1 D2, D2 F2 D0) "
            "(order 2^11 on (F0,F1), free, kernel +-(I,I,I); representatives F0 with row 0 and column 0 all +1, F1 with row 0 all +1: 2^21 pairs) and a literal max over all 2^16 F2. "
            "512 x its histogram equals the producer's C histogram and Python histogram bin by bin in all five modes; Psi: max 192, 0 pairs above 192, 9 canonical pairs at the maximum (x512 = 4,608). "
            "Reduction-free slices: for F0 codes 0,1,7000,12345,21845,30000,32767, all 2^15 F1 and a literal max over 2^16 F2: histograms equal the producer binary's in 35 of 35 (code, mode) cases (reported in AUDIT.md). "
            "Rebuild and rerun of both C halves: all output files byte-identical to data/c_enum/ and to the recorded sha256. Reproduced here: audit/compare.py output in audit/rerun_compare_hashcheck_output.txt.",
            ["DHP-C-0001"],
            arg("C-exact-integer", "audit/gauge_haar.json, audit/gauge_haarfree.json, audit/c_enum/*, AUDIT.md sections 2 and 4; compare.py re-executed on the shipped files.",
                [AUD / "gauge_haar.json", AUD / "gauge_haarfree.json", AUD / "gauge_enum.c", AUD / "compare.py", AUD / "rerun_compare_hashcheck_output.txt", AUD / "c_enum" / "PSI_h0.json"],
                "gauge_enum.c (auditor, gcc -O3 -march=native); compare.py")),
        rec("DHP-C-0005", "C", "argument",
            "Controls, run before the Psi numbers were counted. Positive: exhaustive max R = 2 reproduced (4,096 maximising pairs, auditor 8 x 512); Psi(constant) = 3; seed g gives H = 3/2, T = 1/2, R = 2, Psi = 3. "
            "Negative: Haar-free R reaches N + 1 = 3 (the bound of the level proposition), Haar-free Psi max 5 at the constant input with 7,356,928 pairs above 3 (auditor 14,369 x 512); "
            "planted weight w_T = 4 gives max 4 (S = 256) at the constant and 741,888 violating pairs in 7,360 F0 values, including values strictly between 3 and 4 (49/16 ... 7/2), "
            "so the search detects violations away from the constant input (auditor 1,449 x 512; confirmed at F0 code 1: 344 pairs above 192). A search that silently under-maximised would have been caught.",
            ["DHP-C-0003", "DHP-C-0004"],
            arg("C-exact-integer", "data/controls.json; data/summary.json modes R, PLANT4, HF_R, HF_PSI; audit/gauge_haar.json, audit/gauge_haarfree.json.",
                [d / "controls.json", d / "summary.json", AUD / "gauge_haar.json", AUD / "gauge_haarfree.json"], "psi_exhaust.py; psi_exhaust.c; gauge_enum.c")),
        rec("DHP-C-0006", "C", "argument",
            "Kill criterion and cost: preregistered kill threshold 60 core-hours projected after a 1% sample; sample F0 in [0,328), Psi mode, 40.89 s, projecting 40.89 x 32768/328 / 3600 = 1.135 core-h "
            "(the file says 1.136, rounding) for Psi and about 5.7 core-h for all five Python modes; did not fire. Actual cost about 10 core-h or less (Python 25,964 s summed over 160 chunks on cores 4 and 5 shared with the C run; "
            "C about 80 min wall on the same two cores); the auditor's third enumeration about 0.8 core-h. Preregistration sha256 140a28ad...ae9be unchanged at start and end.",
            [], arg("C-bookkeeping", "logs/kill_criterion_projection.json; logs/prereg_sha_start.txt and prereg_sha_end.txt; result.json.",
                    [LOGS / "kill_criterion_projection.json", LOGS / "prereg_sha_start.txt", LOGS / "prereg_sha_end.txt", d / "result.json"], "none")),
        rec("DHP-C-0007", "C", "argument",
            "By-product found by the auditor, not claimed by the producer: exactly 9 x 2 x 2^11 = 36,864 of the 2^48 sign inputs attain Psi = 3 (18 maximising F2 summed over the 9 canonical pairs, times the orbit size 2^11), "
            "the auditor's count of maximisers (18 summed over 9 canonical pairs) is read off its own enumeration; it is not derived from the producer's 4,608. Computed from gauge_haar.json by compare.py.",
            ["DHP-C-0004"],
            arg("C-exact-integer", "audit/rerun_compare_hashcheck_output.txt line PSI: F2max_sum 18, full_F_at_max 36864.", [AUD / "rerun_compare_hashcheck_output.txt", AUD / "gauge_haar.json"], "compare.py")),
        rec("DHP-C-0008", "C", "argument",
            "HEADLINE. Over all 2^48 sign inputs F in {+-1}^48 at resolution N = 2, Psi = H + 3|T| satisfies Psi <= 3, with max exactly 3 (S = 192 in units 1/64), 0 violations; 4,608 of the 2^30 reduced pairs attain it. "
            "This is the sign-input, resolution-2 case of Conjecture 7.1 (conj:psi) of " + PREPRINT + ": our own conjecture; an exhaustive finite check (two producer enumerations plus an independent auditor enumeration); "
            "NOT progress on C*; nothing for real-valued inputs or N >= 3; no Lean or proof object for the 2^48 statement; compiler and hardware trusted (all runs on one machine). Tier C.",
            ["DHP-C-0003", "DHP-C-0004", "DHP-C-0005", "DHP-C-0001", "DHP-C-0002", "DHP-L-0001"],
            arg("C-assembly", "Assembly of the enumerations, controls and the audit as in Sections 3 to 5 of the paper.", [d / "result.json", d / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        rec("DHP-X-0001", "X", "numeric",
            "NOT done, recorded so the absences are explicit: no Lean or kernel certificate for the 2^48 statement; nothing for real-valued inputs or for N >= 3; the value of C* is untouched; "
            "the Python float32 kernel was not rerun by the auditor (cross-checked only through its histograms in summary.json, which equal 512 x the auditor's); compiler and hardware not checked; "
            "the repository guards and pytest tests/ were not run for this paper; no human audit.",
            [], num([PAPER / "AUDIT.md"], "list of unverified items from AUDIT.md 'What remains unverified'; carries no claim")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}; hash check {hc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
