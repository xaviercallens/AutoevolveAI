"""Build the Elenchus claim ledger for the GE-2 three-species bistability census paper (papers/ge2_three_species_bistability_census).

Modelled on papers/p5_shifted_lonely_runner/ledger/build_ledger.py. Tier discipline: a claim may not be filed above anything in
its depends_on; the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
No Tier A row: there is no Lean in this paper. Gate field audit stays null.
Run:  python3 -I build_ledger.py     (standard library only)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
SRC_COMMIT = "(HEAD 1063788 at writing; paper and data uncommitted)"


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
    return {"kind": "numeric", "files": [fref(f) for f in files], "note": note, "source_commit": SRC_COMMIT}




def main() -> int:
    cen = DATA / "census.jsonl"
    c = [
        rec("GE2-L-0001", "L", "citation",
            "Control source, taken as stated: Peng, arXiv:2610.32739 (23 Oct 2026, unrefereed): two-species networks with at most three internal reactions on {X,Y,2X,X+Y,2Y}, positive inflows and linear removal, "
            "681 networks up to species swap, 27 bistable (Table 1), 245 excluded by the Jacobian rule. The two-species classification is Peng's.",
            [], cite("arXiv:2610.32739", "Table 1 and abstract", "681 networks up to symmetry; 27 bistable",
                     "read in full by the producer (PRIOR_ART.md) and used as the control list; not re-derived by hand")),
        rec("GE2-L-0002", "L", "citation",
            "Inheritance and related small-network results, taken as stated: Joshi-Shiu, Atoms of multistationarity, arXiv:1108.5238, Thm 3.1 (subnetwork N of G with equal stoichiometric subspace: "
            "multiple nondegenerate / exponentially stable positive steady states of N lift to G) and Sec. 6-7 (386 reversible bimolecular two-non-flow-reaction fully open networks, 35 multistationary, 11 atoms; multistationarity, not stability); "
            "Joshi-Shiu arXiv:1603.06441 (Cor. 5.5: at-most-bimolecular networks with exactly two reactions are not multistable; flows counted as reactions); "
            "Tang-Xu arXiv:2008.03846 (multistability of two-reaction networks).",
            [], cite("arXiv:1108.5238; arXiv:1603.06441; arXiv:2008.03846", "Thm 3.1 and Sec 6-7 of 1108.5238; Cor 5.5 of 1603.06441; abstract and intro of 2008.03846",
                     "see statement", "read on alphaXiv 2026-11-11 (PRIOR_ART_ADDENDUM.md); Section 7 tables of 1108.5238 and proofs not read; not re-derived")),
        rec("GE2-L-0003", "L", "citation",
            "Determinant-sign exclusion tradition, taken as stated: Craciun-Feinberg injectivity criterion for fully open networks (SIAM J. Appl. Math. 65 (2005) 1526-1546; part II 66 (2006) 1321-1338) and the Jacobian criterion in Joshi-Shiu "
            "(arXiv:1106.1578, SIAM J. Appl. Math. 72 (2012) 857-876). Our JAC rule is a self-contained midpoint argument of the same type, proved in Section 4 of the paper and checked by the auditor; it is not claimed to be a new criterion.",
            [], cite("Craciun-Feinberg 2005/2006; arXiv:1106.1578", "bibliographic reference only", "see statement",
                     "cited from memory of the literature and from arXiv:1108.5238's reference list; the cited papers' texts were not read in this session")),
        rec("GE2-C-0001", "C", "argument",
            "Enumeration. Class: 3 species X,Y,Z, 9 nonzero complexes of molecularity <= 2, 72 directed internal edges, at most 3 internal edges, inflow 0->S and linear removal S->0 for every species. Labelled networks 1+72+2556+59640 = 62269; "
            "orbits under S3: 10523 (producer enumeration and Burnside agree; independent auditor enumeration and Burnside both give 10523; orbit sizes sum to 62269); 2-species control 1351 labelled, 681 orbits.",
            [], arg("C-enumeration", "Exhaustive enumeration with canonical form = lexicographic minimum over the 6 species permutations; orbit count cross-checked by Burnside; auditor wrote its own enumerator without importing producer code.",
                    [DATA / "logs" / "enum_n3.json", DATA / "logs" / "enum_n2.json", DATA / "code_auditor" / "enum.py", DATA / "code_producer" / "ge2lib.py", cen],
                    "Python itertools, fractions; Burnside")),
        rec("GE2-C-0002", "C", "argument",
            "754 networks (orbits) carry an exact rational bistability witness (BISTABLE_CERT): rational parameters (a, rho, k) > 0 and two distinct positive rational equilibria p, q with f(p)=f(q)=0 verified by exact Fraction substitution and exact Routh-Hurwitz at both points. "
            "The auditor re-verified all 781 witness files (754 three-species + 27 two-species control) with a verifier written from scratch: 781/781 pass; no BISTABLE_CERT row lacks a witness and no witness lacks a row.",
            ["GE2-C-0001"],
            arg("C-exact", "Exact rational arithmetic; the witness files are self-contained certificates (parameters, p, q) that any CAS can re-check.",
                [cen, DATA / "code_auditor" / "verify.py", DATA / "code_producer" / "ge2lib.py", DATA / "AUDIT.md", DATA / "witnesses" / "G01312.json"],
                "Python fractions; verifier independent of producer code")),
        rec("GE2-C-0003", "C", "argument",
            "5071 networks (orbits) are certified to have at most one positive equilibrium for all positive parameters (MONOSTATIONARY_JAC): all coefficients of det(-J) as a polynomial in (x, rho, k) are nonnegative and the rho1*rho2*rho3 coefficient is 1; "
            "since the field f is quadratic, f(x)-f(y) = J((x+y)/2)(x-y), the midpoint is positive, so a second positive equilibrium is impossible. The auditor judged the argument sound, re-derived 60/60 random JAC rows with sympy "
            "(all coefficients nonnegative), 40/40 random non-JAC rows (a negative coefficient), and found no second positive root in a numerical search on 30 JAC rows. The full 5071 were computed by the producer only; the auditor sampled.",
            [], arg("C-jacobian", "Symbolic determinant coefficients plus the midpoint identity for quadratic fields (proof in the paper, Section 4).",
                    [cen, DATA / "code_producer" / "ge2lib.py", DATA / "code_auditor" / "jac.py", DATA / "AUDIT.md"], "sympy polynomial coefficients")),
        rec("GE2-C-0004", "C", "argument",
            "Controls. Positive: the identical pipeline on the 2-species class gives exactly 27 BISTABLE_CERT among 681 orbits, the same set (up to S2) as Peng's Table 1, and 245 JAC exclusions (Peng 245); the 3-species bucket A reproduces the same counts 245/27/102/307. "
            "Negative: the empty network, X->Y and the cycle X<->Y<->Z (deficiency-zero weakly reversible, external control) never give BISTABLE_CERT; a corrupted witness (p perturbed by 1/1000, or rho multiplied by 1.1) fails the exact checker while the uncorrupted one passes; "
            "the auditor's verifier rejects the same corruptions and rejects +I as not Hurwitz.",
            ["GE2-L-0001", "GE2-C-0002"],
            arg("C-controls", "Controls executed with the producer pipeline and, for the corrupted witnesses, with the auditor's independent verifier.",
                [DATA / "controls" / "controls.json", DATA / "code_auditor" / "negctl.py", DATA / "code_auditor" / "pc.py", DATA / "code_producer" / "controls.py"],
                "same checkers as GE2-C-0002")),
        rec("GE2-C-0005", "C", "argument",
            "Structure of the bistable set. Bucket C (connected support 3): 727 bistable orbits, 9 with two internal reactions and 718 with three; 175 are minimal (no proper edge subset is BISTABLE_CERT), of which 79 contain a species that is never a reactant "
            "(the other two species then form an autonomous 2-species subsystem: a cascade) and 96 are irreducible by this screen. The 9 two-reaction networks are listed in the paper with one exact witness each. "
            "Of the 718 three-reaction networks, 552 contain a BISTABLE_CERT two-reaction subnetwork and 166 do not. Counts reproduced by a third script (writer) and by the producer aggregator (202 minimal in all, 175 in bucket C).",
            ["GE2-C-0002"],
            arg("C-structure", "Subset lookup through canonical forms in census.jsonl, recomputed by two scripts.",
                [cen, DATA / "code_writer" / "inherit_check.py", DATA / "logs" / "inherit_check_output.txt", DATA / "logs" / "minimal_crosscheck_output.txt", DATA / "controls" / "aggregate_out.txt"],
                "Python itertools; producer aggregator and writer script agree")),
        rec("GE2-C-0006", "C", "argument",
            "Inheritance consistency check. 609 three-reaction orbits (any bucket) contain a BISTABLE_CERT two-reaction subnetwork: the census certifies 552 of them, has 38 as MULTISTATIONARY_CERT and 19 as UNDECIDED; none is JAC-excluded (0 contradictions). "
            "Given the Tier L inheritance theorem (Atoms Thm 3.1; same stoichiometric subspace because all flows are present), those 57 networks are bistable although the census does not certify them; they are NOT added to the headline counts, and they show that the UNDECIDED and MULTISTATIONARY_CERT classes contain bistable networks.",
            ["GE2-L-0002", "GE2-C-0005"],
            arg("C-inheritance", "Lookup of canonical subsets plus a cited theorem; the 57 are implied, not witnessed.",
                [cen, DATA / "code_writer" / "inherit_check.py", DATA / "logs" / "inherit_check_output.txt"], "Python itertools")),
        rec("GE2-C-0007", "C", "argument",
            "HEADLINE. Partial certified census of bistability for 3-species at-most-bimolecular open mass-action networks with at most three internal reactions: 10523 orbits; 754 BISTABLE_CERT (exact witnesses, independently re-verified), "
            "5071 certified single-equilibrium (JAC), 807 MULTISTATIONARY_CERT (two equilibria certified exactly, no stable pair found; NOT independently verified), 3891 UNDECIDED (37.0%). The census is PARTIAL: "
            "UNDECIDED is search evidence only. Within bucket C, 727 bistable, 175 minimal (79 effectively two-species cascades, 96 irreducible by this screen). No claim of new mechanisms; no biological claim. "
            "Producer and one independent audit are AI agents; no human audit; the preregistration hash is self-attested.",
            ["GE2-C-0001", "GE2-C-0002", "GE2-C-0003", "GE2-C-0004", "GE2-C-0005", "GE2-C-0006"],
            arg("C-assembly", "Assembly of the enumeration, witnesses, exclusion rule, controls and structure counts (all C) as in Sections 2 to 6.",
                [DATA / "RESULT.md", DATA / "result.json", DATA / "AUDIT.md"], "none")),
        rec("GE2-X-0001", "X", "numeric",
            "3891 orbits (37.0%) are UNDECIDED: no exclusion certificate and no witness within 2e5 sampled equilibrium pairs per network (1e6 for none: preregistered stage 2 not run). Search evidence only; never counted as absence of bistability. "
            "Also unaudited: the 807 MULTISTATIONARY_CERT rows (no witness files audited), and whether the search missed bistable networks in that class (the 57 implied by inheritance show it did miss some).",
            [], num([cen, DATA / "controls" / "aggregate_out.txt"], "census.jsonl verdict UNDECIDED / MULTISTATIONARY_CERT; search budget in PREREG_ITEM.md")),
        rec("GE2-X-0002", "X", "numeric",
            "Completeness is NOT claimed: the census is not a classification; no statement is made about the 3891 UNDECIDED networks. Novelty is NOT a certified fact: 'to our knowledge' no published census of exact-witness bistability for this class; "
            "read in full or in part: Peng 2610.32739, Joshi-Shiu 1603.06441 and 1108.5238, Tang-Xu 2008.03846 (PRIOR_ART.md, PRIOR_ART_ADDENDUM.md); not read: Siegal-Gaskins et al. 2009, Banaji-Pantea, the Lixiviant manuscript, Section 7 of 1108.5238. "
            "A recorded search is not proof of absence; authors not contacted.",
            [], num([DATA / "PRIOR_ART.md", DATA / "PRIOR_ART_ADDENDUM.md"], "alphaXiv searches 2026-11-11 (producer prereg re-query and writer addendum)")),
        rec("GE2-X-0003", "X", "numeric",
            "NOT done: Lean formalisation; human audit; independent audit of the 807 multistationary rows and of every JAC exclusion (auditor sampled 60 + 40 + 30); preregistered stage 2 (1e6 pairs); DIV/ROOT/FLUX rules; "
            "edge-by-edge comparison with Section 7 of Joshi-Shiu 1108.5238; a timestamp for the preregistration other than its self-attested hash; interpretation of any mechanism as biological.",
            [], num([DATA / "RESULT.md", DATA / "AUDIT.md", DATA / "PREREG_ITEM.md"], "RESULT.md deviations; AUDIT.md sections 1, 4, 6")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
