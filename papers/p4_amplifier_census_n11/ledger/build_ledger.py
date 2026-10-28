"""Build the Elenchus claim ledger for the C1b paper (papers/p4_amplifier_census_n11).

Modelled on papers/p4_amplifier_census/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
No audit of any kind exists for this paper (producer only): there is no ai_audit field and the gate field audit is null.
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
LOGS = DATA / "logs"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (modules import "
             "Mathlib.Tactic and Mathlib.Algebra.BigOperators.Fin; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked only (C1b lane); producer leanchecker replay rc 0 on DataA1, DataA2, DataA3, Amplifiers11 and "
          "ControlsC1b (data/logs/leanchecker_replay.json); NO recompile by a different agent, NO independent audit of any kind, "
          "NO human audit of statement adequacy, NO statement lock")
SRC_COMMIT = "583284ffeeee645e3c4e7f9c7afd45ccd5855991"


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
            "axiom_output": axioms_from(LOGS / transcript, names), "allowlist": ALLOW,
            "compile_transcript": fref(LOGS / transcript), "sources": [fref(LEAN / s) for s in srcs],
            "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "status": STATUS,
            "statement_adequacy": "not audited by anyone; the statement is about the linear system (Allen eqs. 5, 6, 9) on one explicit adjacency"}


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
    d = DATA
    fix = [d / f"fixation_cert_amp{i}.json" for i in (1, 2, 3)]
    c = [
        rec("AMN-A-0001", "A", "lean_axioms",
            "AmplifierCensus.A1_amplifier: on the 11-vertex graph GA1 (graph6 J?`@`eoRAW?, 16 edges, degrees 2,3,...,3; symmetric, "
            "loopless and degree-checked in Lean), every rational solution tau of Allen eq. (5) satisfies "
            "neff GA1 tau = 328435957/29601736 and 11 < neff GA1 tau. Uses eq5_unique and neff_of_cert from Core.lean (shared with C1). "
            "The statement is about the linear system over Q; it does not formalise the Markov chain or eq. (8).",
            [], lean_ev(["AmplifierCensus.A1_amplifier"], "lean_Amplifiers11.json",
                        ["Core.lean", "DataA1.lean", "Amplifiers11.lean"])),
        rec("AMN-A-0002", "A", "lean_axioms",
            "AmplifierCensus.A2_amplifier: on GA2 (graph6 J?`CP_p[C[?, 16 edges, degrees 2,2,3x8,4) every rational solution of "
            "Allen eq. (5) has neff = 2890154941667179019/262436329991601232 > 11. Same scope as AMN-A-0001.",
            [], lean_ev(["AmplifierCensus.A2_amplifier"], "lean_Amplifiers11.json",
                        ["Core.lean", "DataA2.lean", "Amplifiers11.lean"])),
        rec("AMN-A-0003", "A", "lean_axioms",
            "AmplifierCensus.A3_amplifier: on GA3 (graph6 J?`@`eoRAW_, 17 edges, degrees 2,3x8,4,4) every rational solution of "
            "Allen eq. (5) has neff = 88175846355074579/8011935789939084 > 11. Same scope as AMN-A-0001.",
            [], lean_ev(["AmplifierCensus.A3_amplifier"], "lean_Amplifiers11.json",
                        ["Core.lean", "DataA3.lean", "Amplifiers11.lean"])),
        rec("AMN-A-0004", "A", "lean_axioms",
            "Lean controls (ControlsC1b.lean, imported by nothing): ctlb_perturbed_vector_rejected (A1's tau with one entry changed "
            "by 1/D is not a solution of eq. (5) on GA1), ctlb_wrong_graph_rejected (A1's certificate is not a solution on GA3, the "
            "graph with one extra edge), ctlb_wrong_value_rejected are kernel-checked with axioms within the allowlist; the planted "
            "ctlb_sorry reports sorryAx and the planted ctlb_axiom reports AmplifierCensusControlsC1b.ctlb_cheat.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(LOGS / "lean_ControlsC1b.json",
                                             ["AmplifierCensusControlsC1b.ctlb_perturbed_vector_rejected",
                                              "AmplifierCensusControlsC1b.ctlb_wrong_graph_rejected",
                                              "AmplifierCensusControlsC1b.ctlb_wrong_value_rejected",
                                              "AmplifierCensusControlsC1b.ctlb_sorry",
                                              "AmplifierCensusControlsC1b.ctlb_axiom"]),
                 "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_ControlsC1b.json"),
                 "rejections": [fref(LOGS / "lean_ControlsC1b.json")],
                 "sources": [fref(LEAN / "ControlsC1b.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "status": STATUS,
                 "statement_adequacy": "not audited by anyone"}),
        # ------------------------------------------------------------------ L
        rec("AMN-L-0001", "L", "citation",
            "Allen et al. (arXiv 1906.01036v1 = PLoS Comput. Biol. 16(1):e1007529): model (connected undirected unweighted graph "
            "without loops, death-Birth updating, one mutant at a uniformly random vertex, fitness r = 1 + delta), coalescence-time "
            "equations (5), remeeting times (6), N_eff = sum pi_i tau_i (9), and the definition: G is an amplifier of weak selection "
            "iff N_eff > N, a suppressor iff N_eff < N.",
            [], cite("arXiv:1906.01036v1", "definitions on v1 pp. 6 and 8; eqs. (5)-(9)",
                     "Criterion as pinned in the C1 session and re-read in the C1b session (RESULT.md, Files)",
                     "taken as stated; not re-proved here; the C1b run note records that Allen et al. was re-read with alphaXiv")),
        rec("AMN-L-0002", "L", "citation",
            "Allen et al. eq. (8): rho_G(1+delta) = 1/N + delta (N_eff - 2)/(2N) + O(delta^2); hence N_eff > N implies "
            "rho_G(r) > rho_{K_N}(r) for r in (1, b) for some b > 1 and rho_G < rho_K on (a, 1).",
            ["AMN-L-0001"], cite("arXiv:1906.01036v1", "pp. 8-9, Appendix B pp. 32-34, eq. (45)",
                                 "Expansion and its proof as printed; not formalised here",
                                 "taken as stated; this is the step from the exact N_eff to amplification")),
        rec("AMN-L-0003", "L", "citation",
            "Richter, arXiv:2204.12861v1, p. 8, Fig. 1: four non-isomorphic N = 11 transient amplifiers (a)-(d) printed with "
            "N_eff 11.0008, 11.0128, 11.0056, 11.0952 and mean degrees 3.8182, 2.9091, 3.0909, 2.9091; the caption states that all four have "
            "maximum degree 4, and the text states that (b), at 11.0128, has the highest N_eff.",
            [], cite("arXiv:2204.12861v1", "p. 8, Fig. 1 and caption",
                     "As recorded in the C1b run note (RESULT.md, section Discrepancies) from a reading with alphaXiv in the C1b session",
                     "second-hand for this writing step: transcribed from the run note, not re-opened when the paper was written")),
        # ------------------------------------------------------------------ C
        rec("AMN-C-0001", "C", "argument",
            "Enumeration: nauty geng 2.7r3, geng -c 11 res/256 for res = 0..255, each part piped into the checker; the per-part "
            "'>Z k graphs generated' lines (logs/parts/) equal the number of graphs decided; the 256 parts sum to 1,006,700,565 "
            "= OEIS A001349(11) (read on oeis.org in the session). Completeness rests on geng and on this count; not kernel-checked.",
            [], arg("C-enumeration", "count_equals_A001349 true, parts_done 256, parts_missing 0, bad_lines 0 in census_n11_final.json "
                    "and result.json; per-part JSON in data/parts/, geng lines in data/logs/parts/.",
                    [d / "census_n11_final.json", d / "result.json", d / "logs" / "driver.log"], "nauty-geng; census_fast (C); run_census.py")),
        rec("AMN-C-0002", "C", "argument",
            "Census: among the 1,006,700,565 connected graphs on 11 vertices, exactly 4 have N_eff > 11, exactly 539 have N_eff = 11 "
            "(all regular), and 1,006,700,022 have N_eff < 11, each certified by an exact integer inequality (float64 Cholesky "
            "proposal rounded to 2^-30, exact __int128 residual, non-negativity of the inverse of I - M turns the residual into "
            "an error bound; guard |x| 2^30 < 2^50). 543 non-excluded graphs (539 regular + 4) were solved exactly with Fractions. "
            "guard_fail 0, chol_fail 0, largest eps 7.45e-8. Smallest certified gap over excluded graphs 0.0020643. "
            "NOT kernel-checked; the decision rule is C1's hand-proved bound (audited there), the C implementation is validated "
            "against the Python code but not independently audited.",
            ["AMN-C-0001", "AMN-L-0001"],
            arg("C-exact-integer", "census_n11_final.json fields count_gt_total 4, count_eq_total 539, count_lt_total 1006700022, "
                "candidates 543, exact_candidates_eq_nonregular 0.",
                [d / "census_n11_final.json", d / "code" / "census_fast.c", d / "code" / "aggregate_census.py"], "census_fast.c (gcc -O3), Python Fractions")),
        rec("AMN-C-0003", "C", "argument",
            "Validation of the C port before any N = 11 use: against C1's data at N = 3..10 (inputs sha256-equal to C1's geng files) "
            "identical graph counts, excluded counts and candidate sets; per-graph comparison with the guarded Python functions on all "
            "graphs at N = 3..9 and a 10^6-graph stride sample at N = 10, 0 verdict mismatches, certified intervals intersect on every graph, "
            "max |dN_eff_hat| 1.1e-10; exact finish reproduces C1 (0 amplifiers, ties 1,2,2,5,4,17,22,167 = A005177); on a 10^7-graph N = 11 sample "
            "the Python and C codes give identical counts (9,999,998 excluded) and candidate sets. A bug was found and fixed "
            "before validation: the first build did not JSON-escape the backslash character that graph6 can contain (characters 63..126); "
            "output formatting only, the 10^7 throughput run used that first build and its decisions are unaffected; validation, controls "
            "and the census used the fixed build (sha256 6f658a78...).",
            ["AMN-C-0002"],
            arg("C-exact-integer", "validation_fast_vs_C1.json, reproduce_c1.json, throughput_sample11_1e7.json, logs/validation.log",
                [d / "validation_fast_vs_C1.json", d / "reproduce_c1.json", d / "throughput_sample11_1e7.json"], "validate_fast.py, py_pergraph.py, reproduce_c1.py")),
        rec("AMN-C-0004", "C", "argument",
            "The 539 ties are exactly the connected regular graphs on 11 vertices: 539 = OEIS A005177(11) (read on oeis.org in the session), "
            "and no non-regular graph has N_eff = 11 (exact_candidates_eq_nonregular = 0).",
            ["AMN-C-0002"],
            arg("C-exact-fraction", "census_n11_final.json fields regular_graphs 539, A005177_11 539, regular_equals_A005177 true.",
                [d / "census_n11_final.json"], "aggregate_census.py (Fractions)")),
        rec("AMN-C-0005", "C", "argument",
            "Exact N_eff of the four amplifiers (Fraction solves with C1's dbcore.neff_exact, and a second pure-Fraction Gauss-Jordan "
            "exact_census.py on eqs. (5), (6), (9) that gives the same four graphs and the same maximum): R11 (JCQRRQodIU? = J?ouPjI[@i?, "
            "21 edges) 2668552698098/242579025123 = 11.000756; A2 (J?`CP_p[C[?, 16 edges) 2890154941667179019/262436329991601232 = 11.012785; "
            "A3 (J?`@`eoRAW_, 17 edges) 88175846355074579/8011935789939084 = 11.005561; A1 (J?`@`eoRAW?, 16 edges) 328435957/29601736 = 11.095159. "
            "The four have distinct nauty labelg canonical forms and are pairwise non-isomorphic by networkx; only JCQRRQodIU? is isomorphic to "
            "J?ouPjI[@i?. For R11 the Tier A statement is C1's R11_amplifier (doi 10.5281/zenodo.23704563), not re-checked in this ledger; for A1-A3 "
            "see AMN-A-0001..0003.",
            ["AMN-C-0002", "AMN-A-0001", "AMN-A-0002", "AMN-A-0003"],
            arg("C-exact-fraction", "amplifiers_n11_described.json, census_n11_final.json (amplifiers), exact_independent_nonregular_candidates.json",
                [d / "amplifiers_n11_described.json", d / "census_n11_final.json", d / "exact_independent_nonregular_candidates.json"],
                "dbcore.py neff_exact; exact_census.py; labelg; networkx")),
        rec("AMN-C-0006", "C", "argument",
            "Nearest non-amplifiers (exact Fractions, the 10 non-regular graphs with the smallest certified gap): the closest is "
            "J?`bJaWeJK? with N_eff = 345273648427163/31394406114960 = 10.997935 (20 edges); no graph had a certified upper bound within 1e-3 "
            "of 11 (near_graphs 0).",
            ["AMN-C-0002"],
            arg("C-exact-fraction", "census_n11_final.json nearest_nonamplifiers_exact; near_graphs 0",
                [d / "census_n11_final.json"], "aggregate_census.py")),
        rec("AMN-C-0007", "C", "argument",
            "Match with Richter 2022 Fig. 1: the four amplifiers correspond to (a)-(d) by printed N_eff (11.0008, 11.0128, 11.0056, 11.0952; "
            "ours 11.000756, 11.012785, 11.005561, 11.095159), mean degree (2m/11 = 3.8182, 2.9091, 3.0909, 2.9091 from edge counts 21, 16, 17, 16) "
            "and minimum degree. Drawings were NOT compared. So the four graphs are not new; the exhaustiveness at N = 11 is what the census adds, to our knowledge.",
            ["AMN-C-0005", "AMN-L-0003"],
            arg("C-observation", "amplifiers_n11_described.json (degrees, edges) against the printed values of AMN-L-0003",
                [d / "amplifiers_n11_described.json"], "describe_amplifiers.py")),
        rec("AMN-C-0008", "C", "argument",
            "Finite-r signs of rho_G - rho_{K11} on the exact 2046-state dB chain (float LU proposal, exact-rational residual bound, "
            "error <= 3.9e-14): A1 +4.2836e-6 at r = 1001/1000, -4.3668e-6 at 999/1000, +4.3212e-7 at 10001/10000; A2 +5.2504e-7, -6.3683e-7, "
            "+5.7556e-8; A3 +2.0120e-7, -3.0395e-7, +2.4762e-8. At r = 1.0001, A1: first-order prediction 4.325e-7, measured 4.321e-7. "
            "Certified at these three r only; no r_max is computed for A1-A3. Python Fractions, not kernel-checked.",
            ["AMN-C-0005"],
            arg("C-exact-rational", "fixation_cert_amp1.json, fixation_cert_amp2.json, fixation_cert_amp3.json",
                fix, "fixation_cert.py (copy of C1's)")),
        rec("AMN-C-0009", "C", "argument",
            "Controls run before the N = 11 census (positive): K11 and C11 not excluded, exact N_eff = 11; Richter's graph not excluded, exact value as above, "
            "its quartic parent exactly 11; enumeration level: all 4,721 connected graphs with degrees in [3,4] and 21 edges (geng -c -d3 -D4 11 21:21) give exactly "
            "one candidate, JCQRRQodIU?, canonical form equal to that of J?ouPjI[@i?; C1's 14 controls re-run from a copy, all met. "
            "(Negative): corrupted criterion pi_i = 1/N through the same certified path gives 9 new candidates at N = 10 (e.g. I?`CP`ce_ with corrupted value 10.0193 > 10 "
            "against the correct 9.6643); the strict test N_eff > N rejects K11, C11 and the parent.",
            ["AMN-C-0002"],
            arg("C-exact-fraction", "controls_c1b.json, controls.json", [d / "controls_c1b.json", d / "controls.json"], "controls_c1b.py, controls_c1.py")),
        rec("AMN-C-0010", "C", "argument",
            "Two internal inconsistencies in Richter 2022 Fig. 1 (observations): (1) the caption says all four graphs have maximum degree 4, but our A1 "
            "(his (d), 11.0952) has maximum degree 3: it is A3 with the edge between A3's two degree-4 vertices removed (the graph6 strings differ in one bit), "
            "which fits his own remark that (d) is (c) minus the red edge; (2) the text says (b), at 11.0128, has the highest N_eff, but (d) has 11.0952. "
            "Neither affects the census; neither has been raised with the author.",
            ["AMN-C-0007"],
            arg("C-observation", "degrees and graph6 strings in amplifiers_n11_described.json", [d / "amplifiers_n11_described.json"], "describe_amplifiers.py")),
        rec("AMN-C-0011", "C", "argument",
            "HEADLINE. Among the 1,006,700,565 connected unweighted simple graphs on 11 vertices there are exactly four with Allen's N_eff > N, "
            "that is, exactly four unweighted death-Birth amplifiers of weak selection at N = 11 (exact rational N_eff); 539 tie (all regular, = A005177(11)); the rest are below. "
            "They are the four N = 11 graphs of Richter 2022 Fig. 1, matched by N_eff, edges and degrees (not by drawings). Filed C because the census half is.",
            ["AMN-C-0002", "AMN-C-0004", "AMN-C-0005", "AMN-C-0007", "AMN-A-0001", "AMN-A-0002", "AMN-A-0003", "AMN-L-0001", "AMN-L-0002"],
            arg("C-assembly", "Assembly of the census (C), the Lean theorems for A1-A3 (A) and the criterion (L) as in Section 3 of the paper.",
                [d / "result.json", d / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("AMN-X-0001", "X", "numeric",
            "Repository guards were NOT run for this paper (antigravity_guard.py, test_rigor_guard.py, pytest tests/): no output exists, and none is claimed. "
            "Recorded so the absence is explicit.",
            [], num([d / "controls_c1b.json"], "controls table of the C1b run; contains no guard output")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
