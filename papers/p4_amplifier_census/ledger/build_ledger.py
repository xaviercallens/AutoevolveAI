"""Build the Elenchus claim ledger for the C1 paper (papers/p4_amplifier_census).

Modelled on papers/p3_zero_point_physical/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
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
LEAN = DATA / "lean"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (modules import "
             "Mathlib.Tactic and Mathlib.Algebra.BigOperators.Fin; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the C1 lane; leanchecker replay rc 0 for Richter11 and Controls "
          "(data/logs/leanchecker_replay.json); NO independent audit exists at writing (producer != verifier recompile "
          "pending); no human audit of statement adequacy; no statement lock")
SRC_COMMIT = "25eacb7c37b7ebb54b53792cae13283a493e7bdf"


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


def axioms_from(path: Path, names: list[str]) -> list[str]:
    out = json.loads(path.read_text())["output"]
    flat = out.replace("\n", " ")
    lines: list[str] = []
    for n in names:
        i = flat.find(f"'{n}'")
        if i < 0:
            raise SystemExit(f"axiom line missing for {n}")
        j = flat.find("]", i)
        lines.append(" ".join(flat[i:j + 1].split()))
    return lines


def lean_ev(names: list[str], transcript: str, srcs: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
            "axiom_output": axioms_from(DATA / "logs" / transcript, names), "allowlist": ALLOW,
            "compile_transcript": fref(DATA / "logs" / transcript), "sources": [fref(LEAN / s) for s in srcs],
            "leanchecker_replay": fref(DATA / "logs" / "leanchecker_replay.json"), "status": STATUS,
            "statement_adequacy": "not audited by a human; no independent AI audit at writing"}


def cite(source: str, where: str, text: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text,
            "note": "taken as stated; not re-proved here; the primary PDF was opened by the producer in the C1 session"}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    d = DATA
    census_files = [d / f"census_n{n}_enclosure_final.json" for n in range(3, 11)]
    exact_files = [d / f"census_n{n}_exact.json" for n in range(3, 9)]
    c = [
        rec("AMC-A-0001", "A", "lean_axioms",
            "AmplifierCensus.eq5_unique: for any adjacency A on Fin n, if v solves Allen eq. (5) (zero diagonal, "
            "tau_ij = 1 + 1/2 sum_k (p_ik tau_jk + p_jk tau_ik)) and v_ij > 0 for i != j, then every rational solution "
            "tau of eq. (5) equals v. Proof by a maximum principle (diff_nonpos).",
            [], lean_ev(["AmplifierCensus.eq5_unique"], "lean_richter11.json", ["Core.lean", "Richter11.lean"])),
        rec("AMC-A-0002", "A", "lean_axioms",
            "AmplifierCensus.R11_amplifier: on the 11-vertex graph GR11 (graph6 J?ouPjI[@i?, degrees 3,4,...,4,3, "
            "symmetric and loopless as checked by GR11_symm, GR11_loopless, GR11_deg), every rational solution tau of "
            "Allen eq. (5) satisfies neff GR11 tau = 2668552698098/242579025123 and 11 < neff GR11 tau. The statement is "
            "about the linear system (eqs. 5, 6, 9) over Q; it does not formalise the Markov chain or eq. (8).",
            ["AMC-A-0001"], lean_ev(["AmplifierCensus.R11_amplifier"], "lean_richter11.json",
                                    ["Core.lean", "DataR11.lean", "Richter11.lean"])),
        rec("AMC-A-0003", "A", "lean_axioms",
            "AmplifierCensus.P11_isothermal (positive control): on the 4-regular parent GP11 (graph6 J?ouPjI{@i?) "
            "every solution of eq. (5) has neff = 11 exactly.",
            ["AMC-A-0001"], lean_ev(["AmplifierCensus.P11_isothermal"], "lean_richter11.json",
                                    ["Core.lean", "DataP11.lean", "Richter11.lean"])),
        rec("AMC-A-0004", "A", "lean_axioms",
            "Lean controls: ctl_perturbed_vector_rejected (one tau entry changed by 1/D is not a solution of eq. (5) on "
            "GR11), ctl_perturbed_graph_rejected (the R11 certificate is not a solution on the parent GP11), "
            "ctl_parent_not_amplifier (no solution on GP11 has 11 < neff) are kernel-checked with axioms within the "
            "allowlist; the planted ctl_sorry reports sorryAx and the planted ctl_axiom reports "
            "AmplifierCensusControls.ctl_cheat; ControlsMustFail.lean (asks the kernel to accept the perturbed vector) "
            "fails to compile with rc 1.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(DATA / "logs" / "lean_controls.json",
                                             ["AmplifierCensusControls.ctl_perturbed_vector_rejected",
                                              "AmplifierCensusControls.ctl_perturbed_graph_rejected",
                                              "AmplifierCensusControls.ctl_parent_not_amplifier",
                                              "AmplifierCensusControls.ctl_sorry",
                                              "AmplifierCensusControls.ctl_axiom"]),
                 "allowlist": ALLOW, "compile_transcript": fref(DATA / "logs" / "lean_controls.json"),
                 "rejections": [fref(DATA / "logs" / "lean_controls_mustfail.json")],
                 "sources": [fref(LEAN / "Controls.lean"), fref(LEAN / "ControlsMustFail.lean")],
                 "status": STATUS, "statement_adequacy": "not audited by a human; no independent AI audit at writing"}),
        # ------------------------------------------------------------------ L
        rec("AMC-L-0001", "L", "citation",
            "Allen et al. (arXiv 1906.01036v1 = PLoS Comput. Biol. 16(1):e1007529): model (connected undirected "
            "unweighted graph without loops, death-Birth updating, one mutant at a uniformly random vertex, fitness "
            "r = 1 + delta), coalescence-time equations (5), remeeting times (6), identity (7), N_eff = sum pi_i tau_i "
            "(9), and the definition: G is an amplifier of weak selection iff N_eff > N, a suppressor iff N_eff < N.",
            [], cite("arXiv:1906.01036v1", "pp. 5, 7-8",
                     "Criterion pinned from the primary source in the C1 session (RESULT.md, Method)")),
        rec("AMC-L-0002", "L", "citation",
            "Allen et al. eq. (8): rho_G(1+delta) = 1/N + delta (N_eff - 2)/(2N) + O(delta^2); hence N_eff > N implies "
            "rho_G(r) > rho_{K_N}(r) for r in (1, b) for some b > 1 and rho_G < rho_K on (a, 1); N_eff = N decides "
            "nothing at first order.",
            ["AMC-L-0001"], cite("arXiv:1906.01036v1", "pp. 8-9, Appendix B pp. 32-34, eq. (45)",
                                 "Expansion and its proof as printed; not formalised here")),
        # ------------------------------------------------------------------ C
        rec("AMC-C-0001", "C", "argument",
            "Enumeration: nauty geng 2.7r3 (geng -c N) yields 2, 6, 21, 112, 853, 11117, 261080, 11716571 connected "
            "graphs for N = 3..10, equal to OEIS A001349 read on 2026-10-27. Completeness rests on geng and on this "
            "count check; it is not kernel-checked.",
            [], arg("C-enumeration", "Counts per N recorded in each census file (graphs, oeis_A001349, count_matches_oeis); "
                    "sha256 of the graph6 files in result.json (files themselves kept outside the bundle).",
                    census_files + [d / "result.json"], "nauty geng; Python census_enclosure.py")),
        rec("AMC-C-0002", "C", "argument",
            "Census: among all connected simple graphs with 3 <= N <= 10, none has N_eff > N and every regular one has "
            "N_eff = N exactly; N_eff < N for all others (counts 1/1, 2/4, 2/19, 5/107, 4/849, 17/11100, 22/261058, "
            "167/11716404 for eq/lt at N = 3..10). Method: float64 LAPACK proposal; exact int64 residual of the "
            "integer system 2 k_i k_j * eq. (5); inverse of I - M is non-negative so the residual bounds the error "
            "(|tau - t/2^30| <= eps tau_max); exclusion only if N_eff_hat + eps tau_max < N in exact integers; every "
            "non-excluded graph (exactly the regular graphs) solved with Fractions. Largest eps 5.9e-8; smallest "
            "certified gap among non-regular graphs 0.0174 (N = 9). NOT kernel-checked.",
            ["AMC-C-0001", "AMC-L-0001"],
            arg("C-exact-integer", "Enclosure argument is a hand proof implemented in Python (code/census_enclosure.py, "
                "code/finish_candidates.py).", census_files, "Python 3.11 integer/Fraction arithmetic, numpy LAPACK as proposer")),
        rec("AMC-C-0003", "C", "argument",
            "Independent implementation (code/exact_census.py, pure-Fraction Gauss-Jordan on eqs. (5), (6), (9), no "
            "identity and no enclosure) on all 12,111 connected graphs with N <= 8 agrees with the enclosure census on "
            "every count and every classification.",
            ["AMC-C-0002"], arg("C-exact-fraction", "Per-N agreement fields in result.json census.*.independent_exact_fraction_census.",
                                exact_files + [d / "result.json"], "Python Fractions")),
        rec("AMC-C-0004", "C", "argument",
            "Regular graphs: counts 1, 2, 2, 5, 4, 17, 22, 167 for N = 3..10 equal OEIS A005177 (connected regular "
            "graphs), so none is missing; each has N_eff = N exactly (Fraction solve). Complete graphs and cycles "
            "N = 3..10 have N_eff = N.",
            ["AMC-C-0002"], arg("C-exact-fraction", "census files, field N_eff_eq_N / candidates_exact; controls.json",
                                census_files + [d / "controls.json"], "Python Fractions")),
        rec("AMC-C-0005", "C", "argument",
            "Nearest non-regular graphs: for N = 4..10 the non-regular graph with the smallest certified gap N - N_eff "
            "is nearly complete (even N: K_N minus one edge; odd N: K_N minus a maximum matching; e.g. 173/45 at N = 4, "
            "291/49 at N = 6, 2653/333 at N = 8, 719/146 at N = 5, 5038/723 at N = 7); the certified lower bounds on "
            "the gap are 0.1556, 0.0753, 0.0612, 0.0318, 0.0330, 0.0174, 0.0207. Observation for N <= 10; no proof "
            "for general N. The N_eff values of the odd/even cases at N = 9, 10 are floating-point readings "
            "(8.98262, 9.97927).",
            ["AMC-C-0002"], arg("C-exact-integer", "nonregular_nearest_to_N in each census file (field gap_upper is a lower "
                                "bound on N - N_eff; the name is a misnomer).", census_files, "Python census_enclosure.py")),
        rec("AMC-C-0006", "C", "argument",
            "Exact-chain slope control: d rho/dr at r = 1 of the exact 2^N-2 state death-Birth chain equals "
            "(N_eff - 2)/(2N) on every connected graph with N = 3..6 and on every 40th graph with N = 7 (163 graphs); "
            "the edge identity N_eff = 1 + (1/m) sum_{ij in E} tau_ij and Allen eq. (7) hold on all 994 connected graphs "
            "with 3 <= N <= 7. This checks the transcription of the criterion, not eq. (8) itself for larger N.",
            ["AMC-L-0002"], arg("C-exact-fraction", "controls.json entries", [d / "controls.json"], "code/dbcore.py, code/controls.py")),
        rec("AMC-C-0007", "C", "argument",
            "Allen eq. (3) as printed in arXiv v1 (cycle fixation probability with r^{-(N-1)}) disagrees with the exact "
            "chain in 25 of 25 cases; three other sources (Kaveh et al. eq. (20) at d = 1, Hindersin-Traulsen SI eq. "
            "(18), Richter eq. (12): 2(r-1)/(3r-1+(r-3)r^{2-N})) agree with the chain. Presented neutrally; not "
            "confirmed with the authors; the criterion eq. (9) used here does not depend on eq. (3).",
            [], arg("C-exact-fraction", "controls.json: cycle formula entries", [d / "controls.json"], "code/dbcore.py, code/controls.py")),
        rec("AMC-C-0008", "C", "argument",
            "Other controls (positive): K_N and C_N have N_eff = N; star S_n has N_eff = 4n/(n+1) for n = 2..9; dB and Bd "
            "closed forms on K_N, the dB cycle and the dB star agree with the exact chain at r in {3/4, 5/4, 3/2, 7/4, "
            "1001/1000}, N = 3..7; Hindersin-Traulsen N = 4 classification reproduced; stars S_4..S_6 are Bd amplifiers "
            "and dB suppressors on the r grid. (Negative): p_ij = 1/k_j breaks the star value 10/3; K_N never passes "
            "N_eff > N; the Antal approximation N mu_1^2/mu_2 <= N on every connected graph with N <= 7 and so cannot "
            "detect an amplifier; edges removed away from the argmax vertex of Richter's parents give N_eff <= 10.8805 "
            "(N = 11) and <= 11.9337 (N = 12).",
            [], arg("C-exact-fraction", "controls.json, richter_reproduction.json", [d / "controls.json", d / "richter_reproduction.json"],
                    "code/controls.py, code/richter.py")),
        rec("AMC-C-0009", "C", "argument",
            "Richter reproduction: among the 265 connected quartic graphs on 11 vertices exactly one parent "
            "(J?ouPjI{@i?) is an amplifier constructor; all four edge removals at its argmax vertex give N_eff = "
            "2668552698098/242579025123 = 11.000756 (printed 11.0008). Cubic N = 12 (85 graphs): one constructor, two "
            "removals give 12.026644 (printed 12.0266).",
            ["AMC-A-0002"], arg("C-exact-fraction", "richter_reproduction.json", [d / "richter_reproduction.json"],
                                "code/richter.py, nauty geng -c -d4 -D4 11 and -d3 -D3 12")),
        rec("AMC-C-0010", "C", "argument",
            "Unexplained discrepancy: Richter prints tau_max = 17.6997 for the N = 11 parent and 18.2911 for the N = 12 "
            "cubic example; the exact values here are 10066/569 = 17.69069 and 23648139127685/1292664631282 = 18.29410. "
            "The N_eff values agree to the printed digits. Could be a typo or a convention difference; not raised with "
            "the author; no second independent check.",
            ["AMC-C-0009"], arg("C-exact-fraction", "richter_reproduction.json (tau_max fields)", [d / "richter_reproduction.json"],
                                "code/richter.py")),
        rec("AMC-C-0011", "C", "argument",
            "Finite-r signs on the N = 11 graph (J?ouPjI[@i?) against K_11 via exact-rational a-posteriori residual "
            "bounds on the 2046-state chain: rho_G - rho_K > 0 at r = 10001/10000 and 2501/2500; < 0 at 2499/2500 and "
            "1001/1000; error bound <= 3.3e-14 against differences of 3e-9 to 2e-8; T_max <= 242.43. The method was "
            "validated on the star S_5 at r = 5/4 and 1001/1000. Python Fractions, not kernel-checked.",
            ["AMC-A-0002"], arg("C-exact-rational", "fixation_cert_richter_n11.json", [d / "fixation_cert_richter_n11.json"],
                                "code/fixation_cert.py (Python Fractions; python-flint not installed)")),
        rec("AMC-C-0012", "C", "argument",
            "Bisection of the sign of rho_G - rho_K between r = 1.0007 (positive) and r = 1.00085 (negative) gives a "
            "certified sign change in [10248431/10240000, 4099373/4096000] = [1.00082334, 1.00082349]; the signs along "
            "the bisection are alternately positive and negative, each certified. Existence of at least one change in "
            "the bracket is certified; uniqueness of the crossing is not shown.",
            ["AMC-C-0011"], arg("C-exact-rational", "window_richter_n11.json", [d / "window_richter_n11.json"], "code/window_bisect.py")),
        rec("AMC-C-0013", "C", "argument",
            "For all 212 connected non-complete regular graphs with 4 <= N <= 10, rho_G(r) < rho_{K_N}(r) is certified "
            "at both r = 999/1000 and r = 1001/1000 (none above K_N, none undecided). This is not a proof for all r "
            "near 1: Allen et al. p. 21 list it as an open question.",
            ["AMC-C-0004"], arg("C-exact-rational", "regular_graphs_finite_r.json", [d / "regular_graphs_finite_r.json"],
                                "code/regular_check.py")),
        rec("AMC-C-0014", "C", "argument",
            "HEADLINE. No connected simple unweighted graph with at most ten vertices is an amplifier of weak selection "
            "for death-Birth updating (N_eff > N, Allen et al.); the 11-vertex graph of Richter is one, with exact "
            "N_eff = 2668552698098/242579025123 > 11 for every solution of eq. (5); hence the smallest connected "
            "unweighted dB amplifier of weak selection has exactly 11 vertices. Filed C because the census half is C; "
            "N = 1, 2 are trivial (K_2 regular). The step from N_eff > N to amplification at finite r near 1 is "
            "AMC-L-0002 (literature).",
            ["AMC-C-0002", "AMC-A-0002", "AMC-L-0001", "AMC-L-0002"],
            arg("C-assembly", "Assembly of the census (C), the Lean theorem (A) and the criterion (L) as in Section 6 of the paper.",
                [d / "result.json", d / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("AMC-X-0001", "X", "numeric",
            "Floating-point ratios rho_G/rho_K - 1 of order 1e-8 to 1e-10 at the evaluated r, and the reading that G is "
            "above K on (1, about 1.0008) and below it for r slightly larger; Richter reads r_max about 1.00075 off a "
            "figure. Extrapolation between certified points; supports nothing by itself.",
            [], num([d / "window_richter_n11.json"], "ratio_hat fields of the bisection steps; not a certificate")),
        rec("AMC-X-0002", "X", "numeric",
            "Repository guards were NOT run for this paper (antigravity_guard.py, test_rigor_guard.py, pytest tests/): "
            "no output exists, and none is claimed. Recorded so the absence is explicit.",
            [], num([d / "results.tsv"], "gate table of the C1 run (results.tsv); contains no guard output")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
