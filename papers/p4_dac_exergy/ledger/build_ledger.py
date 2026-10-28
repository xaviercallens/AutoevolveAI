"""Build the Elenchus claim ledger for the K1 paper (papers/p4_dac_exergy).

Modelled on papers/p4_amplifier_census/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be
filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
The Tier C claims are statements about the stylised surrogate AT STATED NUMERIC PARAMETER VALUES, so they do not
depend on the Tier X claims that say how those values were extracted from the published model.
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
TOOLCHAIN = ("Lean 4.34.1 through scripts/certified_numerics/lean_pinned.py (module imports Mathlib.Tactic and "
             "Mathlib.Analysis.SpecialFunctions.Log.Basic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer compile rc 0; independent AI audit 2026-10-27 (papers/p4_dac_exergy/AUDIT.md, ACCEPT_WITH_CORRECTIONS): "
          "auditor recompile rc 0 (12 theorems on exactly propext, Classical.choice, Quot.sound), leanchecker replay of "
          "Programmes.DacExergy.Core rc 0 (118 s, data/leanchecker_replay_audit.json), hypothesis sets shown satisfiable; "
          "three of the twelve theorems are bare identities (ring, ring, norm_num); no human audit of statement adequacy; "
          "no statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (producer != verifier), 2026-10-27", "human": False,
            "report": "papers/p4_dac_exergy/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "kernel_replay": "papers/p4_dac_exergy/data/leanchecker_replay_audit.json (Programmes.DacExergy.Core: rc 0, "
                             "118.3 s; Controls compiled rc 0, plants exposed)",
            "revision": "papers/p4_dac_exergy/REVISION.md (producer's v2; the new feed-air scenario family is not "
                        "independently re-checked)",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no "
                    "statement lock"}
# HEAD when the v2 revision was written; the revision itself is an UNCOMMITTED working-tree change on top of it.
SRC_COMMIT = "754df91f5694d7001517083d97247b23214a67bd (+ uncommitted v2 revision working tree)"


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
    r = {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
         "depends_on": depends, "evidence": blob(ev), "audit": None}
    if tier == "A":
        r["ai_audit"] = AI_AUDIT
    return r


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
            "leanchecker_replay_audit": fref(DATA / "leanchecker_replay_audit.json"),
            "status": STATUS, "statement_adequacy": "not audited by a human; the independent AI audit (AUDIT.md N8) read "
                                                    "the statements and found them faithful to their glosses"}


def cite(source: str, where: str, text: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text,
            "note": "taken as stated; not re-proved here; the primary text was read by the producer in the K1 session"}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    L = LOGS
    core_names = ["DacExergy.carnot_in_mem_unit", "DacExergy.refrig_weight_lt_one", "DacExergy.numerator_factor",
                  "DacExergy.co2_term_penalises_cold", "DacExergy.co2_term_facevalue_favours_cold",
                  "DacExergy.instance_r1", "DacExergy.benefit_affine_in_r", "DacExergy.worst_case_full_recovery",
                  "DacExergy.lambda_threshold_iff", "DacExergy.threshold_iff", "DacExergy.wmin_pure_pos",
                  "DacExergy.wmin_pure_strictAnti"]
    n = core_names
    c = [
        rec("DAC-A-0001", "A", "lean_axioms",
            "DacExergy.carnot_in_mem_unit: for 0 < T0 < T, 0 < 1 - T0/T < 1 (heat supplied above ambient has an exergy "
            "weight in (0,1)); DacExergy.refrig_weight_lt_one: for 0 < T0 and T0/2 < T < T0, 0 < T0/T - 1 < 1 "
            "(rejecting heat just below ambient costs between 0 and 1 joule of work per joule). Real-number algebra; "
            "no thermodynamic content beyond the definitions of the two weights.",
            [], lean_ev(n[0:2], "lean_core.json", ["Core.lean"])),
        rec("DAC-A-0002", "A", "lean_axioms",
            "DacExergy.numerator_factor: q(T0/Tc - 1) - R(T0 - Tc) = (T0 - Tc)(q/Tc - R) for Tc != 0; "
            "co2_term_penalises_cold: if 0 < Tc < T0 and R Tc < q then -q(T0/Tc - 1) + R(T0 - Tc) < 0 (the CO2-only "
            "term of the exergy benefit is negative; NOT the sign of the whole benefit); "
            "co2_term_facevalue_favours_cold: 0 < R(T0 - Tc) for R > 0, Tc < T0; instance_r1: the displayed "
            "rational instance (R = 8.314, q = 40 kJ/mol, Tc = 200 K, T0 = 298.15 K) is negative (norm_num).",
            [], lean_ev(n[2:6], "lean_core.json", ["Core.lean"])),
        rec("DAC-A-0003", "A", "lean_axioms",
            "DacExergy.benefit_affine_in_r (a ring identity); worst_case_full_recovery: if 0 <= gam*D and r <= 1 then "
            "A + lam B <= A + lam B + (1-r) gam D (r = 1 is the worst case for a cold start when gam D >= 0); "
            "lambda_threshold_iff: for B > 0, 0 < A + lam B <-> -A/B < lam; threshold_iff: for 0 < R D, "
            "0 < -N + gam (R D) <-> N/(R D) < gam. Pure algebra on real numbers.",
            [], lean_ev(n[6:10], "lean_core.json", ["Core.lean"])),
        rec("DAC-A-0004", "A", "lean_axioms",
            "DacExergy.wmin_pure_pos: R T0 log(1/x) > 0 for R, T0 > 0 and 0 < x < 1; wmin_pure_strictAnti: it is strictly "
            "decreasing in x on x > 0. These are statements about the function R T0 log(1/x), the minimum work to "
            "extract a pure component from an ideal mixture at mole fraction x; the identification with the physical "
            "minimum work is a (textbook) gloss, not a Lean statement.",
            [], lean_ev(n[10:12], "lean_core.json", ["Core.lean"])),
        rec("DAC-A-0005", "A", "lean_axioms",
            "Planted controls (formal_cert/Programmes/DacExergy/Controls.lean, never imported): ctl_sorry reports "
            "sorryAx and ctl_axiom reports DacExergy.ctl_cheat in #print axioms, although the file compiles with rc 0 "
            "(a compile exit code alone accepts both). The claim recorded is that the audit catches them. "
            "Filed A because it is a kernel-side fact about two named declarations.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(L / "lean_controls.json", ["DacExergy.ctl_sorry", "DacExergy.ctl_axiom"]),
                 "allowlist": ALLOW, "compile_transcript": fref(L / "lean_controls.json"),
                 "sources": [fref(LEAN / "Controls.lean")], "status": STATUS,
                 "leanchecker_replay_audit": fref(DATA / "leanchecker_replay_audit.json"),
                 "statement_adequacy": "not audited by a human; the independent AI audit compiled Controls.lean "
                                       "(rc 0) and found both plants exposed"}),
        # ------------------------------------------------------------------ L
        rec("DAC-L-0001", "L", "citation",
            "McDannald, Siderius, DeCost, Choudhary, Ortiz-Montalvo, Intrinsic Direct Air Capture, arXiv:2501.04825v1 "
            "(8 Jan 2025): idealised piston with three steps; E1 = Q_ads - W1 (eq. 1), E2 = integral over a path s in "
            "(T,P) space (eqs. 2-4), E3 = 0 'no energy recovery' (eq. 5), E_total = E1 + E2 + E3 (eq. 6), purity "
            "(eq. 7), xi = dn_CO2/E_total (eq. 8), C = 1/xi (eq. 9), optimisation prior (eq. 10: T1 >= 200 K, "
            "dT ~ U(0,200), P1 ~ U(101325, 1.1*101325), dP ~ U(-101225, 0)); Table 2 (14 Pareto rows, xi in umol/J, "
            "printed values 6.12 to 11.259); statements on pp. 14-15 (heat recovery 'could therefore exceed our stated "
            "upper limit') and p. 22 (T1 lower limit 200 K). The supplement was NOT read.",
            [], cite("arXiv:2501.04825v1", "pp. 10-15, 19-23, Table 2 (p. 21)",
                     "read in full via alphaXiv text; page 20 re-queried on the PDF for the unit sentence")),
        rec("DAC-L-0002", "L", "citation",
            "Dataset Zenodo 10.5281/zenodo.14452152 (NIST Data Publication 10.18434/mds2-3687, version 1.0; authors "
            "McDannald and Siderius; licence CC-BY-4.0) and code NIST IntrinsicDACCycle v0.0.2 (Julia, NIST software "
            "licence: use, copy, distribute and modify with the notice kept; modified works carry a change notice; NIST "
            "must be acknowledged as source). DAC_data.tar.gz md5 a2520f520140c60f8a4663d5b403966c equals the Zenodo "
            "value; sha256 75a73c75a376a4611511af4a9e99b15af10096fa1886e5d969e4a1d8268df3fa.",
            [], cite("Zenodo 10.5281/zenodo.14452152; github.com/usnistgov/IntrinsicDACCycle v0.0.2",
                     "README.txt, LICENSE.md in the code tarball", "licence terms transcribed from the files in the K1 bundle")),
        rec("DAC-L-0003", "L", "citation",
            "The sentence on p. 20 of arXiv:2501.04825v1 as extracted from the PDF text reads 'There are a few sorbents with "
            "intrinsic capture efficiencies above 1.0 x 10^5 mol/J for their Pareto optimal paths' (the exponent is "
            "printed without a minus sign in the extraction, while the next sentence's 2.46 x 10^-6 keeps its minus). "
            "The independent AI auditor rendered p. 20 at 150 dpi: the typeset PDF prints 1.0 x 10^5 mol/J with a positive "
            "exponent, so the positive exponent is in the typeset source; no person inspected the page.",
            [], cite("arXiv:2501.04825v1", "p. 20", "two independent text extractions (alphaXiv full text, alphaXiv PDF "
                     "query); page image checked by the AI auditor (AUDIT.md N1)")),
        # ------------------------------------------------------------------ C
        rec("DAC-C-0001", "C", "argument",
            "Stylised two-component surrogate (van 't Hoff Henry loadings for CO2 and N2, sensible heat c = gamma R n0, "
            "heat-recovery fraction r on the sensible heat; code/cert_sign.py docstring): the benefit of starting at "
            "Tc < T0 instead of T0, beta = C(T0) - C(Tc), equals A + lam B + (1-r) gamma R D with "
            "A_ex = -(T0-Tc)(q_C/Tc - R) and A_fv = R(T0-Tc). Consequences by the Lean algebra: A_ex < 0 whenever "
            "q_C > R Tc; beta is affine in r, so r = 1 is the worst case for cold when D >= 0; at r = 1 cold wins iff "
            "lam B > -A_ex, i.e. (B > 0 and) lam > lam* = (T0-Tc)(q_C/Tc - R)/B; for r < 1 the heat-capacity threshold "
            "gamma > N/((1-r) R D) with N = -(A + lam B). The derivation of the decomposition from the surrogate's "
            "definition is a hand argument; only the algebraic steps are in Lean.",
            ["DAC-A-0002", "DAC-A-0003"],
            arg("C-hand", "decomposition of C(T0) - C(Tc) and the thresholds, then the Lean steps",
                [DATA / "code" / "k1" / "cert_sign.py", LEAN / "Core.lean"], "none (hand algebra) plus Lean Core.lean")),
        rec("DAC-C-0002", "C", "argument",
            "In the surrogate, A_ex < 0 over the whole parameter box Tc in [200,272] K, T0 in [273,313] K, "
            "Th in [315,400] K, q_C in [12,67] kJ/mol (certified; trivially, since q_C >= 12000 J/mol exceeds R*272 K "
            "= 2261 J/mol).",
            ["DAC-A-0002"],
            arg("C-interval", "A_ex_negative record in cert_sign.json: pos fraction 1.0 over the box",
                [L / "cert_sign.json", L / "cert_sign.log"], "mpmath iv, 80-bit, outward rounding")),
        rec("DAC-C-0003", "C", "argument",
            "Certified signs of the surrogate benefit beta at the stated numeric parameters of 164 parameter sets "
            "(data/logs/surrogate_params.json) x 3 ambient temperatures x 3 recovery fractions (those with Tc < T0 "
            "only: 155, 159, 162 sets at T0 = 273.15, 298.15, 313.15 K): at T0 = 298.15 K and r = 0, 151 positive (cold "
            "wins), 8 negative, 0 undecided (159 sets); at T0 = 298.15 K and r = 1, 131 positive, 28 negative. Outward-"
            "rounded mpmath interval arithmetic; the statement is about the surrogate evaluated at those numbers.",
            ["DAC-C-0001"],
            arg("C-interval", "classification field of cert_sign.json (1428 entries); summary lines in cert_sign.log",
                [L / "cert_sign.json", L / "cert_sign.log", L / "surrogate_params.json"],
                "code/k1/cert_sign.py, mpmath iv at 80 bits (python-flint not installed)")),
        rec("DAC-C-0004", "C", "argument",
            "An independent plain-float implementation of the surrogate lies inside the interval enclosures for 2854 of "
            "2856 points; the other 2 differ by 3e-8 relative from float cancellation, with the same sign. The first run "
            "of the surrogate lacked the factor R on the sensible term (1904 of 2856 mismatches), was found by this "
            "check, fixed and rerun.",
            ["DAC-C-0003"],
            arg("C-interval", "independent_float_check_failures = 2 of 2856", [L / "cert_sign.json", L / "cert_sign.log"],
                "code/k1/cert_sign.py (float_inside_enclosure fields)")),
        # ------------------------------------------------------------------ X
        rec("DAC-X-0001", "X", "numeric",
            "Positive control: the Python re-implementation of the published energy balance (code/k1/dac_model.py) with "
            "the dataset reproduces Table 2 in 14 of 14 rows, 8 of 8 printed fields each, from the stored posterior "
            "statistics (PC-a); recomputes every stored nominal array and E_total with maximum normalised deviation "
            "3.755e-11 (PC-b; one density per material back-solved from one stored number); nominal versus "
            "posterior-mean xi differs by -2.3 % to +1.3 % (PC-c, unseeded 100-draw posterior); re-fitted Cv within "
            "4.0e-6 relative (PC-d).",
            [], num([L / "positive_control.json"], "PC-a..d in positive_control.json; summary in result.json")),
        rec("DAC-X-0002", "X", "numeric",
            "Exergy re-accounting of the 14 stored Table 2 paths at T0 = 298.15 K (heats weighted by Carnot factors, "
            "works kept at face value, Step 3 priced with the right-point rule of the published Step 2 (v2; v1 used a "
            "trapezoid; drift <= 2.4e-4 relative, no printed digit changes)): no-credit xi_NC (r = 0) 25.4 to 36.8 "
            "umol/J, against the face-value nominal recompute 5.98 to 11.26 umol/J (printed posterior means 6.12 to "
            "11.259); reversible floor B_rev 25.0 to 27.0 kJ/mol against ideal-mixture W_min(P0, y) 18.8 to 19.4 kJ/mol "
            "(xi_rev 37.0 to 40.0 umol/J < 1/W_min); refrigeration is 47 to 80 % of the no-credit exergy cost. Sorbent "
            "heating is 1 to 45 % of the face-value E_total; the heats of adsorption plus desorption are 48 to 89 %.",
            ["DAC-X-0001"], num([L / "rev" / "exergy_table2_right.json", L / "rev" / "table1_compare.json",
                                 L / "exergy_table2.json"],
                                "v2: rev/exergy_table2_right.json (eval fields), rev/table1_compare.json (drift, shares); "
                                "v1 exergy_table2.json kept for the drift")),
        rec("DAC-X-0003", "X", "numeric",
            "Base accounting (feed air not priced, ideal machines), v2 joint grid plus refinement (T1 200 to 400 K incl. "
            "2 K steps 270 to 298 K, T_end <= 400 K, P_end in [100, P1], 4,720 to 5,902 paths per row) of the 14 Table 2 "
            "rows: the exergy-optimal T1 lies in 200 to 236.75 K in 14 of 14 rows for every T0 in {273.15, 298.15, "
            "313.15} K and r in {0, 0.5, 1}; 0 of 14 rows have T1* >= T0 in any variant; the face-value control puts all "
            "14 optima below 273 K (maximum 232.1 K). Vacuity (all 14 rows): with the purity constraint on, no warm path "
            "(T1 >= T0) on the grid reaches the stored purity for any row at any T0, so the 9 constrained variants are "
            "vacuous for every row: 126 of 252 row-variants are informative (all unconstrained), not 252.",
            ["DAC-X-0001"], num([L / "rev" / "analysis.json", L / "rev" / "scenario_summary.json", L / "rev" / "scan.log"],
                                "rev/analysis.json base_T1star and vacuity fields; aggregate informative_variants")),
        rec("DAC-X-0004", "X", "numeric",
            "Base accounting, cold-start benefit ratio (best xi with T1 < 298.15 K / best xi with T1 >= 298.15 K, "
            "T0 = 298.15 K), 14 rows, v2 grid: face value 10.2 to 818; exergy r = 0: 3.5 to 129; r = 0.5: 2.6 to 79; "
            "r = 1: 1.29 to 6.6. Unconstrained optimal T_end: face value 230 to 400 K; exergy r = 0 301 to 340 K.",
            ["DAC-X-0003"], num([L / "rev" / "analysis.json", L / "rev" / "scenario_summary.json"],
                                "rev/analysis.json base_ratio fields (split v1)")),
        rec("DAC-X-0005", "X", "numeric",
            "H2: over 8,765 materials with valid paths (15,161 paths; 11,656 optimised files in the public record), the "
            "published face-value xi never exceeds 1/W_min (dataset maximum 11.259 umol/J, VANNIK, against 51.6 "
            "umol/J). RETRACTION (v2): the v1 claim that five dataset entries (CSMNOX, GUSNEN, PACYIE, SABWAU01, "
            "UJOKIP05) have heat flows inconsistent with the second law is withdrawn. Rerun over all 15,161 paths, all "
            "three T0 and both W_min floors: with the v1 Step-3 trapezoid the G3 floor check flags 14/18/21 pairs "
            "(lowest-pressure floor; 3/5/7 materials) and 16/22/25 pairs (P0 floor; 63 in ten materials), reproducing v1 "
            "exactly; with the right-point rule of the published Step 2 it flags 0 at every T0 against both floors, and "
            "the G2 sensible closure holds to 4.4e-16. All flagged paths have dn_CO2 3e-9 to 3.4e-4 mol/kg and xi_fv "
            "6e-8 to 2.9e-3 umol/J: the flags were a quadrature artefact amplified by tiny working capacities, not "
            "evidence about the entries. v1 also misprinted SABWAU01's B_rev (-41.9 kJ/mol, not J/mol) and called "
            "SABWAU01 and UJOKIP05 not degenerate (dn_CO2 4.2e-5 and 1.4e-4 mol/kg).",
            ["DAC-X-0002"], num([L / "rev" / "h2_rules.json", L / "rev" / "h2_rules.log", L / "h2_violators.json",
                                 L / "h2_all.log"],
                                "rev/h2_rules.json summary.violations (both rules); v1 files kept for the retracted counts")),
        rec("DAC-X-0006", "X", "numeric",
            "Slice scan on a seeded random sample of 150 materials (seed 20261027; best stored Pareto path of each; "
            "T_end, P1, P_end held): at T0 = 298.15 K and r = 0 the exergy optimum has T1* >= T0 in 3 of 150 "
            "(unconstrained). Re-selecting among all 15,161 stored Pareto paths of 8,765 materials, the no-credit-exergy-"
            "best path starts below 298.15 K for 8,420 of 8,765 materials (face value: 8,416). Conditional, not a "
            "re-optimisation.",
            ["DAC-X-0003"], num([L / "scan_T1_summary.txt", L / "scan_T1.log", L / "h2_all.log", L / "rev" / "h2_rules.json"],
                                "scan_T1_summary.txt (sample), h2_all.log reselect_* fields; the v2 right-rule rerun "
                                "(rev/h2_rules.json reselect_right_rule) gives the same 8,420 / 8,416")),
        rec("DAC-X-0007", "X", "numeric",
            "Agreement of the surrogate sign (DAC-C-0003) with the full-model slice scan on the seeded 150-material "
            "sample at T0 = 298.15 K: 149/150 (r = 0), 146/150 (r = 0.5), 128/150 (r = 1). On the 14 Table 2 rows "
            "(paper-side recount, per path): r = 1 disagrees on 11 of 14 rows at T0 = 273.15 K, 10 of 13 scorable rows at "
            "298.15 K and 5 of 8 at 313.15 K (the surrogate predicts cold loses; the full model says cold wins); at r = 0 "
            "all scorable rows agree. The interval statements are therefore about the surrogate only.",
            ["DAC-C-0003"], num([L / "surrogate_agreement.json", DATA / "table2_surrogate_check.json"],
                                "surrogate_agreement.json (first path per material), table2_surrogate_check.json (per row)")),
        rec("DAC-X-0008", "X", "numeric",
            "Controls: positive and negative. Positive: real BEVQID ledger passes the gate G1-G4; an all-T >= T0 path "
            "(min 300 K) has heat-in weights in (0,1), no refrigeration term, heat-out free; joint-scan face-value "
            "optimum reproduces 'start cold' (14/14 below 273 K); scan self-check <= 4.2e-7 relative. Negative, all "
            "rejected by the gate: double-counted sorbent heat (G2), planted x10^6 unit error (G4), the text's 1.0e5 "
            "mol/J taken literally (G4), heats of adsorption removed (G3: B_rev 8.73 kJ/mol < W_min 13.52 kJ/mol). All "
            "rerun under the v2 right-point Step-3 rule with the same outcomes. These plants test the gate, not the H1 "
            "conclusion; the H1 negative control is DAC-X-0014.",
            ["DAC-X-0001"], num([L / "rev" / "exergy_table2_right.json", L / "exergy_table2.json", DATA / "result.json"],
                                "controls block of rev/exergy_table2_right.json (v2) and exergy_table2.json (v1)")),
        rec("DAC-X-0009", "X", "numeric",
            "Unit observation: the dataset field Intrinsic_capture_efficiency carries the units string 'mol/J'; its "
            "maximum posterior value is 1.1259e-5 mol/J; 60 of the 8,765 materials have at least one path above 1.0e-5 "
            "mol/J; Table 2 prints xi in umol/J (maximum 11.259). The printed sentence (DAC-L-0003) is consistent with "
            "1.0 x 10^-5 mol/J.",
            ["DAC-L-0003"], num([L / "h2_all.log", DATA / "result.json"], "h2_all.log n_materials_xi_post_gt_10 (60 names)")),
        rec("DAC-X-0010", "X", "numeric",
            "Neutral observations on the published code and data: unseeded 100-draw posterior; Cv drawn once per call "
            "so printed uncertainties omit Cv variability; Captured_CO2 is a posterior mean while E_Balance is nominal; "
            "three descriptions of the single path (text 250 to 350 K then 40,530 Pa; stored files and README 250 to 375 K "
            "and 42,844.84 Pa; code default 300 to 350 K); eight Table 2 rows with P1 in 82,466 to 101,126 Pa although "
            "eq. 10 and the v0.0.2 optimiser bound P1 to >= 101,325 Pa; nominal paths found by our grid with the "
            "published evaluator that exceed several Table 2 rows in both xi and purity (PARFOF 8.42 vs 5.98 umol/J at "
            "purity 0.99999; MAXHEA 8.62 vs 6.77; IFUDAO 8.60 vs 7.27), so the published front may not be fully converged "
            "(an observation to check, not a claim).",
            ["DAC-X-0001"], num([L / "warm_best.json", L / "scan_joint.json", DATA / "recount_ranges.json", DATA / "RESULT.md"],
                                "RESULT.md observations; recount_ranges.json rows_P1_below_101325")),
        rec("DAC-X-0011", "X", "numeric",
            "HEADLINE (v2, narrowed after the independent AI audit). In the published simplified model, for the 14 Table 2 "
            "rows: (a) with every heat of the sorbent and adsorbate Carnot-weighted at an explicit T0, Step 3 priced, "
            "works at face value, ideal machines and the feed air NOT priced, the exergy-optimal start stays at 200 to "
            "236.75 K in 14/14 rows in all 9 informative variants (the 9 purity-constrained variants are vacuous), and "
            "the cold-start benefit shrinks (face value 10 to 818 -> r = 0 3.5 to 129 -> r = 1 1.29 to 6.6) but stays "
            "above 1; (b) with the chilling of the feed air priced (eps = 0, capture fraction 1, T0 = 298.15 K) a cold "
            "start still wins in 14/14 rows at r = 0 but at 254 to 288 K (ratio 1.46 to 8.0), and at r = 1 the optimum "
            "moves to ambient (297.25 to 297.75 K on a 0.25 K grid, advantage 0.07 to 0.35 %) in 11/14 rows; a start "
            ">= 10 K below ambient then loses unless eps > 0.91 to 0.96. H1 as preregistered (T1* >= T0 in > 50 % of rows "
            "at T0 = 298.15 K, r = 0) is refuted in both accountings (0/14); outside that setting the priced scenarios do "
            "not refute it for 11/14 rows at r = 1. The cold start's size, and at full recovery its existence, depend on "
            "how the feed-air chilling is priced. Thermodynamic limits of the published model only; the new scenario "
            "family is producer-computed, agrees with the auditor's numbers on 3 overlapping rows within stated "
            "tolerances, and awaits an independent re-check.",
            ["DAC-X-0001", "DAC-X-0003", "DAC-X-0004", "DAC-X-0008", "DAC-X-0013", "DAC-X-0014", "DAC-L-0001"],
            num([L / "rev" / "analysis.json", L / "rev" / "scenario_summary.json", L / "rev" / "refine_ambient.json",
                 DATA / "RESULT.md"], "v2 joint grid and scenario families, Tier X by construction")),
        rec("DAC-X-0012", "X", "numeric",
            "Absences recorded so they are explicit: the supplement of arXiv:2501.04825 was not obtained and not read; no "
            "human audit of this paper, code or Lean statements exists (the independent audit was by an AI agent; its "
            "report is AUDIT.md); the v2 feed-air scenario family, the H1 negative control and the full-record H2 rerun "
            "are not independently re-checked; the advisor review of the original K1 lane timed out; the repository "
            "guards (antigravity_guard.py, test_rigor_guard.py, pytest tests/) were not run; GATE-1 statement-adequacy "
            "checks were not run; no statement lock; no author contact was made. No output of any of these exists and "
            "none is claimed.",
            [], num([DATA / "RESULT.md", PAPER / "AUDIT.md", PAPER / "REVISION.md"],
                    "RESULT.md Deviations and Limits; AUDIT.md; REVISION.md; no guard output exists")),
        rec("DAC-X-0013", "X", "numeric",
            "Feed-air scenario family (new in v2): n_air = dn_CO2 / x with x = 400e-6 (run_optimize_intrinsic_dac.jl:15; "
            "2,500 mol air per mol CO2 at capture fraction f = 1, the case most favourable to a cold start), ideal "
            "chilling exergy n_air c_p [T0 ln(T0/T1) - (T0 - T1)] with c_p = 7/2 R, unrecovered share (1 - eps)/f added "
            "to B(r). At T0 = 298.15 K, eps = 0, ideal machines: r = 0 T1* 254 to 288 K, cold in 14/14; r = 0.5 T1* 268 "
            "to 290 K; r = 1 T1* at ambient (coarse grid: the 298.0 K cell; refined: 297.25 to 297.75 K, advantage over "
            "T1 >= T0 0.07 to 0.35 %) in 11/14 rows, VANNIK x2 (288 K) and LETQAE01 (284 K) cold for every eps. Recuperator "
            "threshold at r = 1 (cold = T1 <= T0 - 10 K): 0.91 to 0.96 in the 11 rows; auditor's split (T1 <= 290 K vs "
            ">= 298.15 K): 0.77 to 0.90. Machine sensitivity: refrigerator-only degradation without air flips r = 1 below "
            "eta_R 0.10 to 0.75; symmetric degradation without air strengthens the cold start in 14/14 rows. Agreement "
            "with the auditor (FASJAL 8.186, BEVQID 9.186, VANNIK 11.259): T1* within one grid cell, eta_R* at r = 1 "
            "within 0.015, eps* +0.04 and +0.09.",
            ["DAC-X-0003"], num([L / "rev" / "analysis.json", L / "rev" / "scenario_summary.json",
                                 L / "rev" / "refine_ambient.json", L / "rev" / "SHA256SUMS.json"],
                                "rev/analysis.json air, eps_star, eta fields; rev/refine_ambient.json")),
        rec("DAC-X-0014", "X", "numeric",
            "H1 negative control (new in v2): refrigeration costs (sorbent and feed air, eps = 0) multiplied by M, which "
            "cannot affect paths with T1 >= T0 and penalises every colder path. Through the same selection code, M = 1e4 "
            "is detected (T1* >= T0, ratio < 1) in 14/14 rows at r = 0, 0.5 and 1; M = 100 is detected in 7/14, 8/14 and "
            "14/14 rows, the misses being the 298.0 K cell (refrigeration weight 5e-4). Sanity control: refrigeration "
            "and air free never make a cold start worse than in the base accounting (14/14 rows, all r).",
            ["DAC-X-0003"], num([L / "rev" / "analysis.json"], "rev/analysis.json neg_control and free_refrigeration_sanity")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
