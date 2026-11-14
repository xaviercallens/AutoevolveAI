"""Build the Elenchus claim ledger for the E2 paper (papers/p4_battery_saturation_time).

Modelled on papers/p5_cubic_bipartite_cb68/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on, and the kind caps the tier (citation L, argument C, numeric X). There is NO Lean in this paper, so there is no
Tier A row. An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person).
Run:  python3 -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
D = PAPER / "data"
DD = D / "data"
SRC_COMMIT = "cf7610a"  # producer commit of the E2 lane records (audit, rounding fix and this paper are uncommitted)


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


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    c = [
        rec("E2S-L-0001", "L", "citation",
            "Closed form and parameters, taken as stated: constant-flux diffusion in a sphere, surface value x_s = x0 + beta F(tau), F(tau) = 3 tau + 1/5 - 2 sum exp(-a_n^2 tau)/a_n^2, tan a_n = a_n "
            "(classical, Crank; derived independently by the producer and by the auditor, Crank read by neither); parameters D, R, cmax, L, eps_s, electrode height and width, 5 A nominal current, "
            "initial negative concentration 29866 mol/m3 and the Faraday constant printed from the Chen2020 set in PyBaMM 26.10.1.1 (BSD-3-Clause). Chen et al. 2020 itself was not read by anyone.",
            [], cite("Crank, The Mathematics of Diffusion (constant surface flux, sphere); PyBaMM 26.10.1.1 Chen2020 parameter set", "closed form; data/data/params_chen2020.json",
                     "Parameters printed by data/code/dump_params.py from the installed PyBaMM; derivation by producer and auditor (AUDIT.md section 1)",
                     "taken as stated; neither Crank nor Chen et al. 2020 was read; the set's 100 % stoichiometry 29866/33133 = 0.9014 is a balancing limit")),
        rec("E2S-L-0002", "L", "citation",
            "Context taken as stated, not read: Marquis et al. 2019, arXiv 1905.12553 (SPM and SPMe, known to be inaccurate at high C-rate); secondary quotation of Chen et al. 2020 for the negative stoichiometry window 0.0279-0.9014 (arXiv 2311.05482, "
            "as found by the auditor); Subramanian, Diwakar, Tapriyal 2005, J. Electrochem. Soc. 152 A2002 for the constant 1/5 of parabolic-profile reductions (believed by the auditor, not read); Li et al. 2025, ACS Energy Lett. (analytic plating onset, related work).",
            ["E2S-L-0001"], cite("Marquis et al. arXiv:1905.12553; arXiv:2311.05482; Subramanian et al. 2005; Li et al. 2025", "context only",
                                 "none of these was read in full by producer or auditor", "no claim of this paper rests on them")),
        rec("E2S-C-0001", "C", "argument",
            "Certified enclosures (python-flint Arb, 300 bits) of t*(C, x0, x*) for C in {1,2,3,4}, x0 in {0.05,0.25,0.5}, x* in {1, 29866/33133}, 24 cases: roots of tan a = a bracketed in (n pi, n pi + pi/2) by a rigorous sign change of "
            "g(a) = sin a - a cos a (g' = a sin a has constant sign there, so exactly one root; it is the n-th positive root), tail bounded using a_n >= n pi by a geometric series below 2^-100, tau* bracketed by interval bisection deciding a side only when the F ball lies strictly on one side. "
            "The rigorous enclosures are the exact rational tau bounds; relative width of every t* interval at most 9.8e-14. NOT formalised in Lean.",
            ["E2S-L-0001"],
            arg("C-exact-integer", "data/data/certified_t_star.json (rational tau bounds, outward-rounded seconds), code/spm_cert.py, code/run_cert.py, logs/run_cert.log.txt.",
                [DD / "certified_t_star.json", D / "code" / "spm_cert.py", D / "code" / "run_cert.py", D / "logs" / "run_cert.log.txt", D / "prereg_E2.json"], "python-flint Arb")),
        rec("E2S-C-0002", "C", "argument",
            "Controls run before the numbers were reported: P1 short-time ratio 0.098; P2 sum rule sum 1/a_n^2 = 1/10 with deficit 2.527e-4 inside the two-sided bracket [2.5236e-4, 2.5330e-4], F(2)-6-1/5 equal to the first exponential term to 5e-54; "
            "N1 D x 1.1 gives disjoint intervals in 24/24 cases; N2 shifted bracket and wrong interval not certified, alpha_1 + 0.01 shifts F(1e-5) by 4.4e-4; N3 reversed flux sign unreachable, factor 2 tau gives 4616 s against 3078 s (disjoint). "
            "NOT run: the preregistered second half of N3 (the P2 long-time check with 2 tau must fail). The P2 check is weaker than preregistered (2.5e-4 instead of 1e-12).",
            ["E2S-C-0001"],
            arg("C-exact-integer", "data/data/cert_controls.json; pre-fix controls data/data/cert_controls_prefix.json.",
                [DD / "cert_controls.json", DD / "cert_controls_prefix.json", D / "code" / "run_cert.py"], "python-flint Arb")),
        rec("E2S-C-0003", "C", "argument",
            "Outward rounding and independent confirmation: the first run converted the Arb second endpoints with round-to-nearest float(), after which (exact Fraction arithmetic) the seconds interval contained the rational tau interval times R^2/D in only 2/24 cases "
            "and the auditor's enclosure in 21/24; after math.nextafter outward rounding both hold in 24/24 (code/check_exact_rational.py). The auditor's independent mpmath.iv enclosure (interval Newton for roots, integral tail bound, interval Newton for tau; widths about 1e-56 s; "
            "no shared code) lies inside the producer's rational tau interval in 24/24 cases; the auditor's beta equals the producer's.",
            ["E2S-C-0001"],
            arg("C-audit-report", "data/code/check_exact_rational.py and its log; data/data/auditor_mpmath_iv_enclosure.json; pre-fix output data/data/certified_t_star_prefix_roundtonearest.json; AUDIT.md section 2.",
                [D / "code" / "check_exact_rational.py", D / "logs" / "check_exact_rational.log.txt", DD / "auditor_mpmath_iv_enclosure.json", DD / "certified_t_star_prefix_roundtonearest.json",
                 D / "code" / "auditor_mpmath_iv.py", PAPER / "AUDIT.md"], "fractions.Fraction, mpmath.iv, python-flint")),
        rec("E2S-C-0004", "C", "argument",
            "HEADLINE. Rigorous enclosures of the first surface-saturation (x* = 1) or balancing-limit (x* = 0.9014) time in the constant-flux sphere model with the printed Chen2020 negative-particle parameters, for the 24 stated cases (e.g. C = 1, x0 = 0.05, x* = 1: t* about 3916.716 s), "
            "confirmed by an independent AI auditor's solver. For all 24 cases t* equals the long-time formula (R^2/3D)[(x*-x0)/(C beta) - 1/5] up to a relative correction between 8.5e-36 and 8.9e-5 (below 1e-12 in 11/24), so the certificate adds little beyond that formula: "
            "its value is the rigorous enclosure. A model computation; no claim about cells, faster charging, safety or plating. Filed C: rigorous computation plus written argument, no kernel check.",
            ["E2S-C-0001", "E2S-C-0002", "E2S-C-0003", "E2S-L-0001"],
            arg("C-assembly", "Assembly of the enclosures, the controls, the audit and the long-time table as in Sections 2-3 and 6 of the paper; ledger/tables_check.json recomputes the correction range.",
                [DD / "certified_t_star.json", HERE / "tables_check.json", D / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        rec("E2S-X-0001", "X", "numeric",
            "Float cross-checks, not a licence: a finite-volume method of lines (400 cells, scipy BDF, rtol 1e-10) agrees with the series to a maximum relative error 7.7e-6 at 20 points; PyBaMM SPM first-crossing times agree with the certified intervals to 4.2e-4 (20 radial points) and 1.7e-5 (100), "
            "all 24 cases, error shrinking with the mesh (the auditor's r_n = 200 reruns on four cases give 3.7e-7 to 4.3e-6); PyBaMM SPMe equals SPM on the negative-particle surface concentration by construction (same x-uniform current).",
            [], num([DD / "p3_checks.json", DD / "pybamm_compare.json", D / "audit" / "pb_audit.json", D / "audit" / "pb_audit.log.txt"], "mpmath, finite volume, PyBaMM 26.10.1.1 SPM/SPMe; floats")),
        rec("E2S-X-0002", "X", "numeric",
            "DFN observation, exploratory, mesh dependent, not a licence: in PyBaMM DFN (x* = 0.9014 only, positive start 0.99) the x-averaged negative surface concentration crosses at the certified SPM time to 1e-4 at 1C, but the maximum over x crosses earlier (24 / 30 / 37 % at 1C for x0 = 0.05 / 0.25 / 0.5; "
            "891.6, 574.9, 301.7 s against 1716.8, 1297.2, 772.7 s at 2C), with x_n = 20 nodes; x_n = 40 moves 1870.8 s to 1843.5 s (1C, x0 = 0.25) and 206.0 s to 194.2 s (3C), so the percentages carry about 1.5-6 % mesh uncertainty. "
            "DFN fails to integrate for C >= 3 (and for 2C beyond 1.05 t*): auditor diagnosis at 3C, x0 = 0.25: electrolyte concentration below 1 mol/m3 at 368 s, local surface at 0.9999 cmax at about 400 s, IDA fails at 400.5-401.2 s with c_e < 0 and c_s > cmax so the exchange current is NaN; 4C, x0 = 0.05 the same at 193.6 s; "
            "the model state leaves its valid range; 2C failures not diagnosed. One parameter set; says nothing about cells.",
            [], num([DD / "pybamm_dfn.json", DD / "pybamm_dfn_early.json", D / "logs" / "run_dfn.log.txt", D / "logs" / "diag_dfn.log.txt", D / "audit" / "pb_audit2.json", D / "audit" / "pb_audit2.log.txt"], "PyBaMM 26.10.1.1 DFN, producer and auditor scripts")),
        rec("E2S-X-0003", "X", "numeric",
            "Absences, recorded so they are explicit: no earlier certified-interval treatment of this saturation time was found by the auditor's quick search (2 queries, not exhaustive; the producer made no search); NOT run or not complete: Lean/kernel formalisation (Tier C is the ceiling); "
            "the second half of preregistered N3; a human audit; any reading of Crank or Chen et al. 2020; the auditor's rerun of the finite-volume check, the SPMe identity and N4; a diagnosis of the 2C DFN failures; pytest tests/ and the repository guards for this paper.",
            [], num([PAPER / "AUDIT.md", D / "prereg_E2.json"], "audit sections 4 and 7; no claim of this paper rests on this row")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
