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
STATUS = ("producer-checked by the K1 lane; compile rc 0; NO independent audit exists at writing (producer != verifier "
          "recompile pending); no leanchecker replay of DacExergy was run; no human audit of statement adequacy; "
          "no statement lock; the GATE-1 vacuity/numeric adequacy checks of the proposal addendum were not run")
SRC_COMMIT = "e29869853ec8056f6b8aaa1c32e09e018b80ae61"


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
            "status": STATUS, "statement_adequacy": "not audited by a human; no independent AI audit at writing"}


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
                 "statement_adequacy": "not audited by a human; no independent AI audit at writing"}),
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
            "Text extraction only; the page image was not inspected by a person.",
            [], cite("arXiv:2501.04825v1", "p. 20", "two independent text extractions (alphaXiv full text, alphaXiv PDF query)")),
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
            "works kept at face value, Step 3 priced): no-credit xi_NC (r = 0) 25.4 to 36.8 umol/J, against the "
            "face-value nominal recompute 5.98 to 11.26 umol/J (printed posterior means 6.12 to 11.259); reversible floor "
            "B_rev 25.0 to 27.0 kJ/mol against ideal-mixture W_min(P0, y) 18.8 to 19.4 kJ/mol (xi_rev 37.0 to 40.0 "
            "umol/J < 1/W_min); refrigeration is 47 to 80 % of the no-credit exergy cost.",
            ["DAC-X-0001"], num([L / "exergy_table2.json"], "eval fields per row in exergy_table2.json")),
        rec("DAC-X-0003", "X", "numeric",
            "Joint re-optimisation (grid plus refinement over T1, dT and P_end >= 100 Pa, P1 as stored) of the 14 Table 2 "
            "rows: the exergy-optimal T1 lies in 200 to 236.54 K in 14 of 14 rows in every one of 18 variants (T0 in "
            "{273.15, 298.15, 313.15} K x r in {0, 0.5, 1} x purity constraint on/off); 0 of 14 rows have T1* >= T0 in any "
            "variant; the face-value control puts all 14 optima below 273 K (maximum 231.98 K).",
            ["DAC-X-0001"], num([L / "scan_joint.json", L / "scan_joint.log", DATA / "recount_ranges.json"],
                                "scan_joint.json, recount_ranges.json (paper-side recount)")),
        rec("DAC-X-0004", "X", "numeric",
            "Cold-start benefit ratio (best xi with joint cold start / best xi with T1 >= 298.15 K, T0 = 298.15 K), "
            "14 rows: face value 10.2 to 819; exergy r = 0: 3.5 to 129; r = 0.5: 2.6 to 80; r = 1: 1.25 to 6.6. "
            "Unconstrained optimal T_end: face value 227 to 400 K; exergy r = 0 301 to 340 K.",
            ["DAC-X-0003"], num([L / "warm_best.json", DATA / "recount_ranges.json"], "warm_best.json, recount_ranges.json")),
        rec("DAC-X-0005", "X", "numeric",
            "H2: over 8,765 materials with valid paths (15,161 paths; 11,656 optimised files in the public record), the "
            "published face-value xi never exceeds 1/W_min (dataset maximum 11.259 umol/J, VANNIK, against 51.6 "
            "umol/J). The reversible exergy floor B_rev falls below the ideal-mixture W_min (lowest-pressure bound) for "
            "18 path/T0 pairs at 298.15 K (14 at 273.15 K, 21 at 313.15 K) in the 5 materials CSMNOX_clean, GUSNEN_SL, "
            "PACYIE_clean, SABWAU01_clean, UJOKIP05_clean at 298.15 K; most are degenerate paths (purity < 4 %, xi ~ 0), "
            "SABWAU01 (purity 0.91, B_rev = -42 J/mol) and UJOKIP05 (purity 0.67) are not. They are inconsistent inputs "
            "in those entries (for example extrapolated heats of adsorption). The h2_all.py counter skipped cases with "
            "W_min(low P) < 0 and reports fewer (2, 5); h2_violators.json is authoritative.",
            ["DAC-X-0002"], num([L / "h2_violators.json", L / "h2_violators.log", L / "h2_all.log"],
                                "h2_violators.log (authoritative), h2_all.log (own-counter, lower)")),
        rec("DAC-X-0006", "X", "numeric",
            "Slice scan on a seeded random sample of 150 materials (seed 20261027; best stored Pareto path of each; "
            "T_end, P1, P_end held): at T0 = 298.15 K and r = 0 the exergy optimum has T1* >= T0 in 3 of 150 "
            "(unconstrained). Re-selecting among all 15,161 stored Pareto paths of 8,765 materials, the no-credit-exergy-"
            "best path starts below 298.15 K for 8,420 of 8,765 materials (face value: 8,416). Conditional, not a "
            "re-optimisation.",
            ["DAC-X-0003"], num([L / "scan_T1_summary.txt", L / "scan_T1.log", L / "h2_all.log"],
                                "scan_T1_summary.txt (sample), h2_all.log reselect_* fields")),
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
            "mol/J taken literally (G4), heats of adsorption removed (G3: B_rev 8.7 kJ/mol < W_min 13.5 kJ/mol).",
            ["DAC-X-0001"], num([L / "exergy_table2.json", DATA / "result.json"], "controls block of exergy_table2.json")),
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
            "HEADLINE (negative result for our hypothesis). In the published simplified model, re-weighting every heat by "
            "its Carnot factor at an explicit ambient T0 and pricing Step 3 does NOT move the optimal start temperature "
            "to ambient or above for any of the 14 Table 2 rows (T1* 200 to 236.54 K in all 18 variants); the cold-start "
            "benefit ratio shrinks (face value 10 to 819 -> exergy r = 0 3.5 to 129 -> r = 1 1.25 to 6.6) but stays above 1. "
            "Our preregistered hypothesis H1 (the optimum moves to T1 >= T0 for most rows) is refuted. Thermodynamic limits "
            "of the published model only.",
            ["DAC-X-0001", "DAC-X-0003", "DAC-X-0004", "DAC-X-0008", "DAC-L-0001"],
            num([L / "scan_joint.json", L / "warm_best.json", DATA / "RESULT.md"], "joint grid, Tier X by construction")),
        rec("DAC-X-0012", "X", "numeric",
            "Absences recorded so they are explicit: the supplement of arXiv:2501.04825 was not obtained and not read; no "
            "independent audit of this paper, code or Lean statements exists; the advisor review of K1 timed out; the "
            "repository guards (antigravity_guard.py, test_rigor_guard.py, pytest tests/) were not run; GATE-1 statement-"
            "adequacy checks were not run; no author contact was made. No output of any of these exists and none is "
            "claimed.",
            [], num([DATA / "RESULT.md"], "RESULT.md Deviations and Limits; no guard output exists")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
