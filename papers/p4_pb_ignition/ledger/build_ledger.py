"""Build the Elenchus claim ledger for the E1 paper (papers/p4_pb_ignition).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person): Tier A rows carry an ai_audit field and
the gate field audit stays null, so LEDGER_UNAUDITED_TIER_A remains open (exit 1 is the honest state).
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
CODE = DATA / "code"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (module imports "
             "Mathlib.Tactic and Mathlib.Analysis.SpecialFunctions.Pow.Real; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("Tier A pending a statement lock (none exists). Producer: lean_pinned.py compile rc 0 and the binding anse/formal/lean_runner.py verify_file gate "
          "(logs/lean_core.json, logs/lean_runner_core.json). Independent AI auditor (AUDIT.md section 5, a separate agent instance, not a person): recompiled a "
          "byte-identical copy rc 0, built its own olean and ran leanchecker PbIgnition.Core rc 0 (negative control: a nonexistent module rc 1); "
          "that leanchecker transcript is in the auditor's scratch and is NOT shipped, it is reported in AUDIT.md only. NO human audit of statement adequacy, NO statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-28", "human": False,
            "report": "papers/p4_pb_ignition/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own recompilation of Core.lean with lean_pinned.py compile, own olean + leanchecker replay (rc 0), escape-hatch grep, check that the planted "
                     "statements of Controls.lean are actually false, comparison of the 4.375 coefficient with the exact derivative of t(1+1.1t+t^2-1.25t^2.5)",
            "not_scope": "statement adequacy (that the two inequalities are the facts the physics argument needs) not certified by a person; the binding lean_runner gate was not re-run by the auditor",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "bdd3e02b174fe4a2c1751431e0d5b573a86d3dc9"


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
    thm = ["PbIgnition.optimal_mix", "PbIgnition.optimal_mix_eq", "PbIgnition.rpow_25_le_sq", "PbIgnition.ee_term_deriv_pos"]
    c = [
        rec("PBI-A-0001", "A", "lean_axioms",
            "PbIgnition.Core (Lean 4.34.1, Mathlib): optimal_mix, 20 x (1 - x) <= (1 + 4 x)^2 for all real x; optimal_mix_eq, equality iff x = 1/6; "
            "rpow_25_le_sq, t^2.5 <= t^2 on [0,1]; ee_term_deriv_pos, 0 < 1 + 2.2 t + 3 t^2 - 4.375 t^2.5 on [0,1]. "
            "#print axioms for all four: propext, Classical.choice, Quot.sound only; no sorry. They are statements about two elementary real inequalities "
            "(the optimal boron mix of Wurzel-Hsu footnote 138, and the sign of the derivative of the electron-electron bremsstrahlung term); "
            "the step 'positive derivative implies monotone' and everything about the interval enclosures are NOT in Lean.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(LOGS / "lean_core.json", thm), "allowlist": ALLOW,
                 "compile_transcript": fref(LOGS / "lean_core.json"), "axiom_transcript": fref(LOGS / "lean_core.json"),
                 "runner_gate_transcript": fref(LOGS / "lean_runner_core.json"),
                 "sources": [fref(LEAN / "Core.lean")],
                 "leanchecker_replay": "auditor's own replay, rc 0, reported in AUDIT.md section 5; transcript not shipped (auditor scratch)",
                 "status": STATUS,
                 "statement_adequacy": "not audited by a person; no statement lock"}),
        rec("PBI-A-0002", "A", "lean_axioms",
            "Lean controls: Controls.lean (tampered optimum 1/21 at the same proof script; tampered e-e coefficient 7 instead of 4.375; the derivative bound claimed on [0,2]) "
            "is rejected by the kernel pipeline, rc 1, with errors at lines 23, 28, 32, 33 (logs/lean_controls.json). The auditor checked that each planted statement is actually false "
            "(x = 1/6: 21*5/36 = 2.917 > 25/9; t = 1: 1+2.2+3-7 = -0.8; t = 2: about -7.35), so no proof exists, not only that the script fails.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(LOGS / "lean_core.json", ["PbIgnition.ee_term_deriv_pos"]),
                 "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_controls.json"),
                 "rejections": [fref(LOGS / "lean_controls.json")],
                 "sources": [fref(LEAN / "Controls.lean")],
                 "status": STATUS, "statement_adequacy": "not audited by a person"}),
        # ------------------------------------------------------------------ L
        rec("PBI-L-0001", "L", "citation",
            "Wurzel and Hsu, arXiv 2105.10954 v4: the ideal 0-D power balance P_c >= P_B (eqs 6-8, 16, 22, 41, D1-D5) with P_c = f_c n1 n2 <sigma v> E and "
            "P_B = C_B n_e^2 sqrt(T_e) gamma(Z_eff), C_B = 5.34e-37 W m^3 keV^(-1/2); gamma = Z_eff (1 + 1.78 t^1.34) + 2.12 t (1 + 1.1 t + t^2 - 1.25 t^2.5), t = T_e/(m_e c^2) (eq. D2); "
            "optimal proton-boron mix x = n_B/n_i = 1/6, Z_eff = 3 (eqs D3-D4, footnote 138); Table II/III list '-' for p-11B; Fig. 28 caption 'P_B always exceeds P_c when T_e >~ T_i/3', "
            "using the parameterized Nevins-Swain reactivity.",
            [], cite("arXiv:2105.10954v4", "eqs 6-8, 16, 22, 41, D1-D5; Tables II, III; Fig. 28; footnote 138",
                     "Read by the producer (lines 60-1720, 2640-2760, 3900-4057, 8740-9420 of the full text) and re-derived by the independent AI auditor",
                     "taken as stated; the producer did not read the sections on Q_eng, profiles and the data tables; the full text is not shipped")),
        rec("PBI-L-0002", "L", "citation",
            "Wang, Li, Wu, Cui, arXiv 2601.00241 v1 (Jan 2026), eqs (1)-(6) and Table I: an updated p-11B S-factor (segments E<=0.4, 0.4-0.7, 0.7-10 MeV; the first reprints the Nevins-Swain coefficients) "
            "and the reactivity as the Maxwellian integral; Fig. 8 text 'if electron-ion thermal equilibrium is assumed (T_e = T), the resulting bremsstrahlung loss ... exceeds the fusion power density "
            "over the entire temperature range' (with Rider's bremsstrahlung). Ochs and Fisch, arXiv 2310.18508 v1, eq. (14): the same relativistic bremsstrahlung bracket (prefactor 7.56e-11 eV cm^3/s, x^2 term).",
            ["PBI-L-0001"], cite("arXiv:2601.00241v1; arXiv:2310.18508v1", "Wang eqs (1)-(6), Table I, Fig. 8 text; Ochs-Fisch eq. (14)",
                                 "Read in full by the producer; every coefficient of the Wang S-factor in data/fits.json was matched to Table I by the auditor",
                                 "taken as stated; Wang's fit uncertainties (3-10% on the 0.6 MeV resonance) are not propagated")),
        rec("PBI-L-0003", "L", "citation",
            "The Bosch-Hale (1992) D-T reactivity coefficients and the Nevins-Swain (2000) p-11B high-temperature reactivity coefficients P1-P7 (valid 50-500 keV) are the values transcribed "
            "from the Wurzel-Hsu public code (github.com/swurzel/lawson-criterion-paper, MIT licence, commit 4ae563bf, dated after the 2022 paper), the preregistered fallback. "
            "NEITHER the producer NOR the independent auditor could obtain Bosch-Hale 1992 or Nevins-Swain 2000. These coefficients are NOT verified against the primary papers. "
            "Only indirect checks exist: the NS low-energy S-factor block agrees with Wang Table I; the transcribed NS fit is 0.985-0.996 of the Maxwellian integral of the NS S-factor at 50-200 keV, "
            "0.976 and 0.965 at 250 and 300 keV, 0.940 at 400 keV, 0.917 at 500 keV (reproduced by the auditor, Tier X); the auditor's recollection of Bosch-Hale agrees (memory, not a pinned source).",
            [], cite("Bosch and Hale, Nucl. Fusion 32, 611 (1992); Nevins and Swain, Nucl. Fusion 40, 865 (2000); via Wurzel-Hsu code commit 4ae563bf",
                     "data/fits.json (coefficients with per-block provenance)",
                     "Secondary source only (author code, used as data, never executed); primary papers not obtained by producer or auditor",
                     "this matters most for theta*, which scales roughly with the reactivity (auditor: x1.1/1.2/1.32 moves theta_c to 0.477/0.524/0.579); the T_e = T_i exclusion has a margin of about 2.35x")),
        # ------------------------------------------------------------------ C
        rec("PBI-C-0001", "C", "argument",
            "Method (Arb ball arithmetic, python-flint 0.6.0, 128 bit; every coefficient a decimal string from fits.json): certified Maxwellian reactivity of a cross-section fit by rigorous acb.integral "
            "plus the temperature-interval bound sv(a)(a/b)^(3/2) <= sv(T) <= sv(b)(b/a)^(3/2) (valid because the S-factor is certified >= 0); best-first branch and bound with outward rounding for max P_c/P_B over (T_i, x) boxes; "
            "bisection plus a certified witness for theta*; the reduction from the face theta_hi to every theta in [theta_hi, 1] uses that P_B increases with T_e for T_e <= 500 keV < m_e c^2, "
            "whose electron-electron term derivative is positive by PBI-A-0001 (the step 'positive derivative implies monotone' is not formalised). Not replayed in Lean.",
            ["PBI-A-0001"], arg("C-interval-arithmetic", "code/e1_model.py, code/e1_certify.py, logs/certify.json from the final end-to-end rerun of the hashed code (logs/certify_final_stdout.txt)",
                                [CODE / "e1_model.py", CODE / "e1_certify.py", LOGS / "certify.json", LOGS / "certify_final_stdout.txt"], "e1_model.py, e1_certify.py (python-flint)")),
        rec("PBI-C-0002", "C", "argument",
            "D-T positive control against Wurzel-Hsu, passed for the model the authors' code ran (the gate model was chosen after a float run, Deviation 6): certified ideal-ignition temperature [4.2989514, 4.2989523] keV (printed 4.3); "
            "argmin of n T tau_E at Q = infinity in [14.128, 14.442] keV (printed 14), minimum [2.94410, 2.94502]e21 (printed 2.9e21); argmin of n tau_E in [25.590, 26.212] keV (printed 26), minimum [1.55227, 1.55279]e20 (printed 1.6e20); "
            "constant hull T_ign [4.2608, 4.3468], TP min [2.94400, 2.96351]e21. Other certified readings: parameterized non-relativistic, text C_B/J, f_c = 0.2: T_ign [4.29959, 4.29959], TP min [2.94923, 2.95056]e21 (straddles the 2.95 rounding edge); "
            "parameterized relativistic, code constants: T_ign [4.32619, 4.32620], TP min [2.96275, 2.96409]e21 (prints 3.0); integrated non-relativistic, text C_B/J, f_c = 0.2: TP min [2.93077, 2.93168]e21 (prints 2.9). "
            "These 'text' variants use f_c = 0.2 from the code, not the text's 3.5/17.6 (audit correction C1). Every variant gives 4.3, 14, 26 and 1.6e20; only the second digit of the Table III minimum depends on the reading.",
            ["PBI-C-0001", "PBI-L-0001", "PBI-L-0003"],
            arg("C-interval-arithmetic", "logs/certify.json (gates, dt_variants), logs/certify_gates.json, code/e1_gate.py", [LOGS / "certify.json", LOGS / "certify_gates.json", CODE / "e1_gate.py"], "e1_certify.py, e1_gate.py")),
        rec("PBI-C-0003", "C", "argument",
            "At T_e = T_i, on T_i in [50, 500] keV and boron fraction x in [0.05, 0.5], P_c < P_B everywhere (no ideal-ignition window) for both reactivity fits, in this ideal 0-D model: "
            "certified max P_c/P_B in [0.42139, 0.42556] (Nevins-Swain, argmax about 202 keV, x = 0.100) and [0.42869, 0.43260] (Wang, about 208.5 keV, x = 0.101); at the Wurzel-Hsu mix x = 1/6: "
            "[0.39016, 0.39240] (NS) and [0.39732, 0.40083] (Wang). Certified reactivity multiplier m* in [2.350, 2.373] (NS) and [2.312, 2.333] (Wang): any reactivity at most 2.349 x NS on [50, 500] keV gives P_c < P_B on the whole box. "
            "The maximum is interior; widening the box (x to [0.005, 0.95], T_i to [20, 1000] keV) leaves it unchanged (auditor, float, Tier X). Not replayed in Lean.",
            ["PBI-C-0001", "PBI-L-0001", "PBI-L-0002", "PBI-L-0003"],
            arg("C-interval-arithmetic", "logs/certify.json (E1c), result.json E1c_TeEqTi", [LOGS / "certify.json", d / "result.json"], "e1_certify.py")),
        rec("PBI-C-0004", "C", "argument",
            "A window needs T_e/T_i below a threshold theta*, certified only for theta in [theta_hi, 1]: Nevins-Swain full box [0.4223, 0.4308] (witness at theta = 0.4223: T_i = 243.5 keV, x = 0.0922, R >= 1.0077); "
            "NS x = 1/6 [0.3753, 0.3828] (witness 243.5 keV, R >= 1.0082); Wang full box [0.4381, 0.4470] (witness R >= 1.0082 at 243.5 keV, x = 0.092); "
            "Wang x = 1/6 [0.396, 0.402] (explicit theta scan: at theta = 0.402 certified max R <= 0.99995; at theta = 0.396 a witness at T_i = 261.65 keV, x = 1/6 with R >= 1.00037, a thin margin; audit C8). "
            "Above theta_hi the face argument of PBI-C-0001 applies. These thresholds hold for these two fits and Putvinski's bremsstrahlung only; they scale with the reactivity (PBI-X-0001). "
            "The ideal 0-D model has no synchrotron, no transport, no ion-electron coupling, no alpha heating of electrons, no ash, Maxwellian only; the maximum interior is about 202 keV and x about 0.10 at theta = 1.",
            ["PBI-C-0001", "PBI-L-0001", "PBI-L-0002", "PBI-L-0003"],
            arg("C-interval-arithmetic", "logs/certify_pb_NS.json, logs/certify_pb.json, logs/certify_wang_mix.json (explicit scan, code/e1_wang_mix.py), result.json E1b_theta_star",
                [LOGS / "certify_pb_NS.json", LOGS / "certify_pb.json", LOGS / "certify_wang_mix.json", CODE / "e1_wang_mix.py", d / "result.json"], "e1_certify.py, e1_wang_mix.py")),
        rec("PBI-C-0005", "C", "argument",
            "Controls, run with the gate before the p-11B headline: P1 D-T reproduction passes (G1, G2, G2b, G3, G4 true, for the authors' code model); N1 reactivity x 0.5 FAILS the gate (T_ign 5.3724 keV, TP min 6.285e21, LP min 3.230e20); "
            "N2 bremsstrahlung removed FAILS (no ignition temperature; the p-11B ratio becomes infinite and the 'no window' conclusion flips); N3 Lean controls fail (PBI-A-0002); S-factor positivity certified. "
            "Audit correction C6: the D-T gate G3 does NOT discriminate for the p-11B conclusion (it passes under N1, since halving the reactivity only strengthens an exclusion). "
            "The p-11B pipeline's ability to find a window is shown instead by the theta* witnesses (R > 1 at theta_lo), the theta = 1/3 check (R = 1.113 NS, 1.161 Wang; Tier X) and N2. "
            "The auditor read the recorded check vectors of N1 and N2 in logs/certify.json; the gate code was not re-run by the auditor.",
            ["PBI-C-0002", "PBI-C-0004"],
            arg("C-interval-arithmetic", "logs/certify.json (negative_controls), logs/certify_gates.json, result.json", [LOGS / "certify.json", LOGS / "certify_gates.json", d / "result.json"], "e1_gate.py, e1_certify.py")),
        rec("PBI-C-0006", "C", "argument",
            "Independent AI audit (AUDIT.md, a separate agent instance, ACCEPT_WITH_CORRECTIONS, not a person): with its own mpmath.iv code (different method: 11,513 x 4,500 geometric/uniform cell grid with corner monotonicity bounds) "
            "it reproduced rigorously the D-T T_ign for three readings, the NS max P_c/P_B over the box [0.42140, 0.42470] and at x = 1/6 [0.39016, 0.39311], the NS theta* upper side (U < 1 at 0.43125 and 0.38281), and re-evaluated the producer's NS witnesses "
            "(R in [1.0077322, 1.0077331] and [1.0082393, 1.0082399]). Every producer enclosure contains the auditor's value. The Wang-side numbers and the D-T TP/LP minimisers of the gate model are float only on the auditor's side (Tier X). The auditor did not re-run the producer's Arb integrals.",
            ["PBI-C-0003", "PBI-C-0004"],
            arg("C-audit-report", "AUDIT.md sections 2-5 (auditor's scratch /tmp/e1audit not shipped)", [PAPER / "AUDIT.md"], "aud_model.py and others (auditor)")),
        rec("PBI-C-0007", "C", "argument",
            "HEADLINE. In an ideal 0-D power-balance model (Wurzel-Hsu's, with Putvinski's bremsstrahlung), with two reactivity fits (Nevins-Swain as transcribed from the Wurzel-Hsu code, and Wang et al. 2026), in the box T_i in [50, 500] keV, x in [0.05, 0.5]: "
            "there is no ignition window at T_e = T_i (certified max P_c/P_B [0.4214, 0.4256] NS, [0.4287, 0.4326] Wang), and a window needs T_e/T_i below thresholds theta* of about 0.42-0.45 (full box) or 0.375-0.402 (x = 1/6), certified only for theta <= 1, "
            "for these fits and this bremsstrahlung only. Tier C (Arb ball arithmetic, not replayed in Lean; coefficients not verified against primary papers). Concerns the model and the fits only: nothing about any device, reactor, feasibility or economics.",
            ["PBI-C-0003", "PBI-C-0004", "PBI-C-0005", "PBI-C-0006", "PBI-A-0001", "PBI-L-0001", "PBI-L-0002", "PBI-L-0003"],
            arg("C-assembly", "Assembly of PBI-C-0003 and -0004 with the controls (PBI-C-0005), the audit (PBI-C-0006), the Lean facts (PBI-A-0001) and the literature premises, as in Sections 3 to 6 of the paper.",
                [d / "result.json", d / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("PBI-X-0001", "X", "numeric",
            "Float checks (Tier X, supporting nothing by themselves): the producer's independent float implementation (scipy) is inside every certified enclosure (theta_c,max 0.4286 NS box, 0.3811 NS x = 1/6, 0.4451 Wang box, 0.3988 Wang x = 1/6; max R at theta = 1 0.4232 NS, 0.4309 Wang); "
            "the Wurzel-Hsu Fig. 28 remark: at T_e = T_i/3 and x = 1/6 max P_c/P_B = 1.113 (NS, T_i about 248 keV) and 1.161 (Wang, about 268.5 keV), so the certified threshold 0.375-0.383 lies above 1/3; "
            "the NS fit versus the Maxwellian integral of the NS S-factor (0.985 at 50 keV down to 0.917 at 500 keV); the auditor's float sensitivities: reactivity x1.1/1.2/1.32 moves theta_c to 0.477/0.524/0.579, "
            "Rider's bremsstrahlung moves it by about +1%; the auditor's pure-text D-T row (f_c = 3.5/17.6, parameterized non-relativistic, text C_B and 1.6e-16 J/keV): T_ign in [4.3071225, 4.3071227] keV and n T tau_E >= 2.95e21 with a value 2.96846e21 at 14.2486 keV, "
            "so the minimum lies in [2.95e21, 2.96846e21] and prints 3.0e21 (auditor mpmath.iv, scratch not shipped; the producer has not certified this row with its own pipeline); Wang/NS reactivity ratio 1.016, 1.000, 1.005, 1.016, 1.070, 1.154, 1.262 at 50, 100, 150, 200, 300, 400, 500 keV.",
            [], num([LOGS / "float_indep.json", LOGS / "third_check.txt", LOGS / "ns_consistency.json", PAPER / "AUDIT.md"], "float transcripts of the producer; the auditor's values are reported in AUDIT.md (scratch not shipped)")),
        rec("PBI-X-0002", "X", "numeric",
            "NOT run or not complete: pytest tests/ (not run); the repository guards antigravity_guard.py (38 findings) and test_rigor_guard.py exit 1 on pre-existing files elsewhere in the repository and flag no E1 file (logs/guard_*.txt); "
            "the CVODE (rusty-SUNDIALS) transient; a synchrotron or kinetic-enhancement model (only the multiplier m* is certified); a statement-lock entry for the two Lean lemmas; the primary-paper check of the Bosch-Hale and Nevins-Swain coefficients; "
            "a human audit; the fix of the stopping-order issue of theta_threshold in decide mode (Wang x = 1/6 is certified by the explicit scan instead). Recorded so the absences are explicit.",
            [], num([LOGS / "guard_antigravity.txt", LOGS / "guard_test_rigor.txt"], "guard transcripts of the producer; they contain no claim about this paper")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
