"""Build the Elenchus claim ledger for the K3 carbon impulse-response paper (papers/p4_carbon_impulse_response).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person): Tier A rows carry an ai_audit field and the gate field audit stays null,
so LEDGER_UNAUDITED_TIER_A remains open (exit 1 is the honest state).
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
RES = DATA / "data"
CODE = DATA / "code"
AUD = DATA / "audit_scripts"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (module imports "
             "Programmes.CompletelyMonotone.Basic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("AI-audited (AUDIT.md, a different AI agent instance, not a person); producer leanchecker replay rc 0 on "
          "Programmes.CarbonK3.Core (data/logs/leanchecker_replay.json); the auditor recompiled Core with the pinned toolchain "
          "(rc 0, 13.6 s) and replayed leanchecker (rc 0, 61.4 s) on its own olean, dependency oleans reused not rebuilt "
          "(data/audit_scripts/lean_audit.json); NO human audit of statement adequacy, NO statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-31", "human": False,
            "report": "papers/p4_carbon_impulse_response/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own compile of Core.lean with #print axioms, own olean + leanchecker replay, escape-hatch grep, Controls caught by the axiom gate, "
                     "check that IsCompletelyMonotoneOn is the genuine definition",
            "not_scope": "statement adequacy (the Lean statements mean what their gloss says) not certified by a person; discrete nonnegative emission measures only; "
                         "dependency oleans reused, not rebuilt",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "d85a839755843982725e3abf4944c939e15390a4"


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


def axiom_lines(path: Path, names: list[str]) -> list[str]:
    lines: list[str] = []
    text = path.read_text()
    for n in names:
        hit = [ln.strip() for ln in text.splitlines() if ln.strip().startswith(f"'{n}'")]
        if len(hit) != 1:
            raise SystemExit(f"axiom line missing or duplicated for {n}")
        lines.append(hit[0])
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
    thm = ["CarbonK3.irf_cm", "CarbonK3.excess_cm_after", "CarbonK3.excess_antitone", "CarbonK3.excess_convexOn",
           "CarbonK3.excess_tendsto", "CarbonK3.neg_ctl_not_cm"]
    c = [
        rec("CK3-A-0001", "A", "lean_axioms",
            "CarbonK3.Core (discrete nonnegative emission measures only): with irf(t) = a0 + sum_i a_i exp(-r_i t) and excess(t) = sum_j w_j irf(t - z_j): "
            "irf_cm (a0, a_i, r_i >= 0 implies the IRF is completely monotone on (0, inf)); excess_cm_after (w_j >= 0, z_j <= T implies s -> excess(s + T) is CM); "
            "excess_antitone; excess_convexOn; excess_tendsto (limit a0 * sum_j w_j when all r_i > 0); neg_ctl_not_cm (1 - exp(-t) is not CM). "
            "These do not formalise continuous emission paths, T2, T3 or the peak enclosures; excess has no Heaviside factor and equals the model excess only for t >= max z_j.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(LOGS / "lean_core_compile.log", thm), "allowlist": ALLOW,
                 "compile_transcript": fref(LOGS / "lean_core_compile.log"),
                 "sources": [fref(LEAN / "Core.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"),
                 "auditor_recompile": fref(AUD / "lean_audit.json"), "status": STATUS,
                 "statement_adequacy": "not audited by a person; Core.lean sha256 00e6ba6c...363a matches result.json"}),
        rec("CK3-A-0002", "A", "lean_axioms",
            "Lean controls: Controls.lean compiles with rc 0 (planted controls) but its axiom audit reports sorryAx for CarbonK3.ctl_sorry and the smuggled "
            "axiom CarbonK3.ctl_cheat for CarbonK3.ctl_axiom, which a compile exit code alone would accept.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(LOGS / "lean_controls_compile.log", ["CarbonK3.ctl_sorry", "CarbonK3.ctl_axiom"]),
                 "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_controls_compile.log"),
                 "sources": [fref(LEAN / "Controls.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "status": STATUS,
                 "statement_adequacy": "not audited by anyone; the controls are meant to fail the gate"}),
        # ------------------------------------------------------------------ L
        rec("CK3-L-0001", "L", "citation",
            "Joos et al. 2013, ACP 13, 2793, doi:10.5194/acp-13-2793-2013 (CC BY 3.0): Table 5, row IRFCO2: a0..a3 = 0.2173, 0.2240, 0.2824, 0.2763 (sum exactly 1) and "
            "tau1..tau3 = 394.4, 36.54, 4.304 yr; eq. (7) and text: the IRF is the fraction of an added pulse still airborne, and the change in the atmospheric inventory is the "
            "convolution of emissions with the IRF; eq. (11): the fit is valid only for 0 <= t <= 1000 yr.",
            [], cite("Joos et al. 2013, ACP 13, 2793", "Table 5 row IRFCO2; eqs. (7), (11); PDF header CC Attribution 3.0",
                     "All nine numbers confirmed by the independent AI auditor (AUDIT.md section 1); a1 <-> 394.4, a2 <-> 36.54, a3 <-> 4.304",
                     "taken as stated; third-party PDF not redistributed")),
        rec("CK3-L-0002", "L", "citation",
            "Seshadri, arXiv:1502.00805v3 (Global and Planetary Change 2017): eq. (2) u = uP + int_0^t m(z) h(t-z) dz with m in concentration units; eq. (1) prints "
            "0.276/0.282/0.224/0.217 (sum 0.999) with tau 4.30/36.5/394 (text uses tau1 = 4.4); emission family m = m0 (1+r)^(min(t,tg)-t0) exp(-(t-t0)/tau_m); "
            "Sect. 3.2 uses (1+r)^t ~ e^{rt} and considers only r > 1/tau_m; Fig. 5 parameters tg-t0 = 60 yr, r = 0.015 %/year, tau_m = 50 yr fall outside that case under "
            "either reading; the printed eq. (4) omits the boundary term involving m(0).",
            ["CK3-L-0001"], cite("Seshadri arXiv:1502.00805v3", "eqs. (1), (2), (4); Sect. 3.2; Figs. 2, 5",
                                 "Read by the producer and the independent AI auditor; wording neutral, no contact with the author",
                                 "taken as stated; PDF not redistributed; the reading of 0.015 %/year is not resolved")),
        rec("CK3-L-0003", "L", "citation",
            "Ibragimov 1956 (Teor. Veroyatn. Primen. 1(2), 283-288; Theory Probab. Appl. 1), 'On the composition of unimodal distributions': convolution with every unimodal "
            "density preserves unimodality iff the kernel is log-concave (strong unimodality). Consequences used only as prior art: the one-sided exponential is log-concave "
            "(T2 is a special case); a CM kernel that is not a single exponential is strictly log-convex, so for integrable kernels some unimodal input gives a non-unimodal output.",
            [], cite("Ibragimov 1956; Encyclopedia of Mathematics 'Unimodal distribution'; Watanabe, Nagoya Math. J. 1991",
                     "strong unimodality",
                     "Stated from SECONDARY sources only; the original was not checked (AUDIT.md section 3)",
                     "taken as stated; used for attribution, not as a premise of any computation")),
        # ------------------------------------------------------------------ C
        rec("CK3-C-0001", "C", "argument",
            "T1 (continuous emissions, paper proof): for m >= 0 supported on [0,T] and t > T, u(t) = a0 W + sum_i b_i exp(-t/tau_i) with W = int m and "
            "b_i = a_i int exp(z/tau_i) m(z) dz >= 0, hence (-1)^n u^(n) >= 0: u is completely monotone on (T, inf), non-increasing, convex, with limit a0 W "
            "(a property of the fitted formula beyond its 0-1000 yr window). Elementary; checked by hand by the auditor; the discrete case is the Tier A row CK3-A-0001. "
            "Numerical support (Tier X): P5, 200/200 random histories antitone and convex; N1, 181/200 violate with a negative coefficient.",
            ["CK3-L-0001"], arg("C-argument", "RESULT.md section (a); AUDIT.md section 3 (hand re-derivation); results_c.json controls P5, N1.",
                                [DATA / "RESULT.md", RES / "results_c.json", PAPER / "AUDIT.md"], "paper proof; run_c.py controls")),
        rec("CK3-C-0002", "C", "argument",
            "T2 (single exponential): for h = exp(-t/tau) and m >= 0 weakly unimodal, u is non-decreasing then non-increasing (quasi-concave); its maximisers form an interval; "
            "it never has two local maxima separated by a strictly lower value. Proof via g = exp(t/tau) u' with dg = exp(t/tau) dm. The wording 'at most one local maximum' is false "
            "for non-strict maxima (impulse c*tau at 0 plus constant emission c gives u constant). A special case of Ibragimov's strong unimodality (Tier L, secondary sources).",
            ["CK3-L-0003", "CK3-L-0001"], arg("C-argument", "AUDIT.md section 3 (re-derivation, counterexample to the literal wording); auditor float test: 400 random weakly unimodal staircases with h = exp(-t/30): at most one +- change of u', no -+ change.",
                                              [PAPER / "AUDIT.md", AUD / "t3_t2.py"], "paper proof; auditor script t3_t2.py")),
        rec("CK3-C-0003", "C", "argument",
            "T3 (staircase window): h CM, h(0) = 1, strictly decreasing, not a single exponential; rho(x) = h(x+d)/h(x) strictly increasing (Cauchy-Schwarz on the Bernstein measure) from h(d) "
            "to L (L = 1 iff a0 > 0). Staircase m = A on [0,d), A-B on [d,z3), 0 after, theta = B/A in (0,1): for theta in (h(d), L) and z3 > d + x*, u has exactly two local maxima "
            "(at d and z3) and one minimum (at d + x*, rho(x*) = theta), using u'(z3+) = -A(1-h(z3)) + B(1-h(z3-d)) < 0; for theta <= h(d) or theta >= L exactly one. "
            "Weakly unimodal (non-increasing) path. Paper proof, checked by hand and in floats by the auditor (Joos d = 5, a0 = 0 two-exponential IRF).",
            ["CK3-C-0001", "CK3-L-0001"], arg("C-argument", "AUDIT.md section 3; float checks t3_t2.py and rho_mp.py (60-digit strict monotonicity of rho for a0 = 0); logs/check_two_term.log.",
                                              [PAPER / "AUDIT.md", AUD / "t3_t2.py", AUD / "rho_mp.py", LOGS / "check_two_term.log"], "paper proof; t3_t2.py; rho_mp.py; check_two_term.py")),
        rec("CK3-C-0004", "C", "argument",
            "(b) Certified peak times and delays for Seshadri's emission family with Joos Table 5: closed-form u' and u'' in mpmath interval arithmetic (60 digits), exact rational "
            "bisection with certified signs u'(lo) > 0 > u'(hi) and u'' < 0 on the 0.01-yr initial bracket (unique local maximum inside the bracket, enclosure width < 1e-19 yr); "
            "t1 certified from the sign of ln(1+r) - 1/tau_m; 63 scenarios (3 IRFs x 3 r x 7 tau_m) all CERTIFIED; origin t0 = 0 (differs from Seshadri's). Global uniqueness is NOT certified (Tier X, CK3-X-0001). "
            "Positive control: closed-form peak 75 ln(5/3) enclosed.",
            ["CK3-L-0001", "CK3-L-0002"], arg("C-interval", "results_b.json: 63 CERTIFIED; control_closed_form.json: 75 ln(5/3) = 38.3119217824493012... inside [38.31192178244930124039, 38.31192178244930124045].",
                                              [RES / "results_b.json", RES / "control_closed_form.json", LOGS / "run_b.log", CODE / "run_b.py", CODE / "k3lib.py"], "run_b.py; k3lib.py; control_closed_form.py")),
        rec("CK3-C-0005", "C", "argument",
            "(c) Certified instances for the Joos IRF (exact rationals, mpmath intervals at 60 digits, half-width < 1e-56): five-point certificates u(s1) < u(s2) > u(s3) < u(s4) > u(s5) for "
            "I1 (continuous piecewise-linear, weakly unimodal; s = 10, 21, 32, 303, 320), I2 (continuous, strictly increasing on [0,10] and strictly decreasing on [10,310]; s = 10, 21, 40, 305, 330; "
            "meets the strict definition) and S1 (non-increasing staircase; s = 1, 5, 11, 200, 500); all four differences positive in each (min 0.278 for I2). Two local maxima separated by a strictly lower value. "
            "A first attempt for S1 with s3 = 100 failed and is recorded.",
            ["CK3-L-0001"], arg("C-interval", "results_c.json certified block: two_local_maxima_certified true for I1, I2, S1; run_c.log.",
                                [RES / "results_c.json", LOGS / "run_c.log", CODE / "run_c.py", CODE / "k3lib.py"], "run_c.py; k3lib.py")),
        rec("CK3-C-0006", "C", "argument",
            "What the independent AI auditor recomputed with its own code: (c) instances with Sage RealBallField at 400 bits (all 15 u values agree to the 20 printed digits, radii <= 5e-116, "
            "lower bounds of the differences I1 3.780/0.3130/7.794/0.5732, I2 3.780/0.2776/4.435/0.5618, S1 3.370/0.3216/6.586/3.349); (b) t2 and t1 for all 21 Joos scenarios with mpmath at 50 digits "
            "and a float scan (agreement <= 6.0e-20 with the enclosures; one +- change each; this is NOT an independent interval certificate of uniqueness); Seshadri variants for 3 cells; "
            "T3/T2 float numerics. NOT done: the other 36 Seshadri-variant cells, the float maps in (c), the 3-maximum cases.",
            ["CK3-C-0004", "CK3-C-0005"], arg("C-audit-report", "AUDIT.md section 2; scripts indep_c.sage, indep_c.sage.py, indep_b_t3.py, t3_t2.py (auditor scratch, small sources only).",
                                              [PAPER / "AUDIT.md", AUD / "indep_c.sage.py", AUD / "indep_b_t3.py"], "indep_c.sage; indep_b_t3.py (auditor)")),
        rec("CK3-C-0007", "C", "argument",
            "Controls, run before the headline: P1 coefficient sums (Joos 1, Seshadri printed 0.999); P2 single exponential never more than 1 maximum in 1500 paths; P3 closed form vs quadrature 50/50; "
            "P4 CARBON-1 arithmetic 5091/6250; P5 post-cessation antitone and convex 200/200; N1 negative coefficient 181/200 violate; N2 wrong sign rejected 50/50; "
            "N3 single exponential vs Joos on the same emission, 1 vs 2 maxima; N4 planted sorry/axiom caught by the axiom gate (CK3-A-0002).",
            ["CK3-C-0005"], arg("C-exact-integer", "results_c.json controls block; result.json controls_pass list.",
                                [RES / "results_c.json", DATA / "result.json"], "run_c.py controls; check_two_term.py")),
        rec("CK3-C-0008", "C", "argument",
            "HEADLINE. In the linear IRF model u = int m h: (a) after emissions cease u is completely monotone with limit a0 W (Lean for discrete emission measures, Tier A pending lock; paper proof otherwise); "
            "(b) certified peak times and delays for 63 Seshadri-family scenarios (global uniqueness Tier X); (c) for every CM, strictly decreasing, non-single-exponential IRF (in particular the Joos IRF) "
            "there are weakly unimodal emission paths with two local maxima separated by a strictly lower value, with the explicit window B/A in (h(d), L) necessary and sufficient within the staircase family, "
            "and three certified Joos instances (one strictly unimodal); for a single exponential u is quasi-concave. The mechanism is classical (Ibragimov, read from secondary sources); "
            "this is a model result, not a statement about the real carbon cycle, tonnes, climate or policy, and not a new phenomenon class. PARTIAL outcome.",
            ["CK3-C-0001", "CK3-C-0003", "CK3-C-0004", "CK3-C-0005", "CK3-C-0006", "CK3-C-0007", "CK3-A-0001", "CK3-L-0001", "CK3-L-0002", "CK3-L-0003"],
            arg("C-assembly", "Assembly of the proofs (C), the interval certificates (C), the discrete Lean lemmas (A) and the literature (L) as in Sections 3-6 of the paper.",
                [DATA / "result.json", DATA / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("CK3-X-0001", "X", "numeric",
            "Float scans, not certificates: the scan of u' on [0,6000] yr (beyond the 1000-yr fit window) shows exactly one +- sign change in all 63 scenarios (global peak uniqueness); "
            "plateau-family table of maxima counts; 1500 random continuous unimodal paths with the Joos IRF (17 / 1364 / 117 / 2 with 0 / 1 / 2 / 3 maxima; the 3-maximum cases are float-grid counts, "
            "uncertified and unchecked by the audit); a0 = 0 and two-term IRF checks; the auditor's own float scans on [0,3000] (21 Joos scenarios, 6 of 42 Seshadri-variant cells).",
            [], num([RES / "results_b.json", RES / "results_c.json", LOGS / "check_two_term.log"], "float outputs of the producer; they support no claim by themselves")),
        rec("CK3-X-0002", "X", "numeric",
            "NOT done or not establishable here, recorded so the absences are explicit: statement lock for the Lean statements; human audit; a systematic literature search (carbon-cycle IRF unimodality, "
            "peak-warming-delay literature); checking Ibragimov's original text; a sufficient condition for 'at most one peak' beyond the single exponential; Lean for continuous emissions, T2, T3, part (b); "
            "ordering of the preregistration against the work (git history does not show it; the hash matches); comparison with Seshadri's figures beyond order of magnitude (Tier X, time origin differs).",
            [], num([DATA / "prereg_K3.json", DATA / "prereg_K3.sha256"], "preregistration file and its hash; they contain no claim about this paper's results")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
