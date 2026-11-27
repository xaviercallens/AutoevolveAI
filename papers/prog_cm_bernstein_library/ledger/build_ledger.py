"""Build the Elenchus claim ledger for the P3 preprint (papers/prog_cm_bernstein_library).

Modelled on papers/ar_dipolar_exciton/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim primary-source excerpts
(Tier L, from sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence   (see run_gate.py)
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
P3 = W / "results/programmes/2026-10-25/P3"
LOGS = P3 / "compile_logs"
APP = P3 / "applications"
SRC = W / "formal_cert/Programmes/CompletelyMonotone"
REC = HERE / "recompile"
H1C = W / "results/autoresearch/2026-10-25/H1/contribution"
UP = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy")
MATHLIB = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/.lake/packages/mathlib")
TOOLCHAIN = ("Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, "
             "openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (pinned copy)")
BASE = "9d245742c1655852103abb28f585e21af54851e6"
OLD_EXC = json.loads((W / "papers/ar_dipolar_exciton/ledger/sources/excerpts.json").read_text())

AM = MATHLIB / "Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean"
AM_LINES = AM.read_text().splitlines()
AM_DEF = "\n".join(AM_LINES[56:60])
if not AM_DEF.startswith("def AbsolutelyMonotoneOn"):
    raise SystemExit("AbsolutelyMonotone.lean line 57 moved; update the excerpt")

EXC = {
    "ps_conjecture": OLD_EXC["ps_conjecture"],
    "ck_cm_def": {
        "source": "H. Cohn, A. Kumar, Universally optimal distribution of points on spheres, J. Amer. Math. Soc. 20 (2007), 99-148",
        "durable_reference": "arXiv:math/0607446v2", "page": "journal p. 101 (alphaXiv page 3)",
        "text": "Recall that a C^infinity function f : I -> R on an interval I is completely monotonic if (-1)^k f^(k)(x) >= 0 for all x in I and all k >= 0 (see [Wid, p. 145]) ... It might seem preferable to use completely monotonic functions of distance, rather than squared distance, but squared distance is in fact more natural than it first appears ... it is more general than using distance: it is not hard to prove that if r -> f(r^2) is completely monotonic on a subinterval (a,b) of (0,infinity), then f is completely monotonic on (a^2,b^2), but not vice versa."},
    "sal_defs": {
        "source": "D. S. Salazar, Bernstein Functions at Work: Coalescents, Copulas, and Subordination",
        "durable_reference": "arXiv:2607.04467v1", "page": 4,
        "text": "Definition 2.1 (Completely monotone, Bernstein, and Stieltjes classes). Let all functions below be defined on (0, infinity) and take values in [0, infinity). (i) A function f is completely monotone, written f in CM, if f in C^infinity and (-1)^n f^(n)(x) >= 0 for every n >= 0 and x > 0. ... (ii) A function g is a Bernstein function, written g in BF, if g in C^infinity and g' in CM."},
    "sal_bw": {
        "source": "Salazar, arXiv:2607.04467v1", "durable_reference": "arXiv:2607.04467v1", "page": 5,
        "text": "Theorem 2.3 (Bernstein-Widder). f in CM if and only if there is a unique positive Radon measure mu on [0, infinity) such that f(x) = integral over [0,infinity) of e^(-xt) dmu(t)."},
    "sal_subord": {
        "source": "Salazar, arXiv:2607.04467v1", "durable_reference": "arXiv:2607.04467v1", "page": 2,
        "text": "This dictionary - Bernstein-Widder for CM functions, Levy-Khintchine for Bernstein functions, and Bochner subordination for their composition - turns many analytic questions into statements about a representing measure that one can often write down explicitly [31, 19]. (Reference [31] there is R. L. Schilling, R. Song, Z. Vondracek, Bernstein Functions: Theory and Applications, 2nd ed., de Gruyter, 2012; the statement that a completely monotone function composed with a Bernstein function is completely monotone is NOT quoted there and its theorem number in [31] was not verified by us.)"},
    "mathlib_am_def": {
        "source": "Mathlib, Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean (Michael R. Douglas, 2025), pinned Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612",
        "durable_reference": "Mathlib d13f23b7, file line 57", "page": None,
        "text": AM_DEF,
        "other": "The file proves, as its module docstring lists: contDiffOn, of_contDiff, iff_iteratedDerivWithin_nonneg, add, smul "
                 "(six theorem/lemma declarations in total); it cites D. V. Widder, The Laplace Transform, Princeton University Press, 1941 "
                 "(docs/references.bib key widder1941). It has no product, composition, translation, Bernstein-function or Laplace-transform lemma."},
    "mathlib_ai_policy": {
        "source": "Lean community, 'How to contribute', section 'Use of AI' (leanprover-community.github.io/contribute/index.html), fetched 2026-10-25 through a fetch tool that returns only short quotations (<= 125 characters each)",
        "durable_reference": "https://leanprover-community.github.io/contribute/index.html", "page": None,
        "text": "\"Using an LLM when writing comments on GitHub or Zulip is not allowed: use your own words.\" ... \"you must explain this in the PR description.\" ... \"code written by an AI without the supervision of a Lean subject expert fails to meet that bar by a large margin.\" ... \"It is essential that you understand all the content written by an AI.\" (The page also asks for the LLM-generated label on pull requests with a substantial amount of LLM-generated code; that sentence was returned as a paraphrase, not a verbatim quote.)"},
}
(HERE / "sources").mkdir(exist_ok=True)
(HERE / "sources/excerpts.json").write_text(json.dumps(
    {"_note": "Excerpts read on 2026-10-25 by the paper-stage agent. alphaXiv page text is a PDF extraction (mathematics transcribed "
              "linearly, infinity and arrows written out); durable references are the arXiv version identifiers given. These are definitions "
              "and prose, not theorem statements to be re-checked with tools/citation_check.py.", **EXC}, indent=1, ensure_ascii=False))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    return {"path": str(p), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def axiom_lines(log: Path, names: list[str]) -> list[str]:
    out = json.loads(log.read_text())["output"].replace("\n ", " ")
    lines = []
    for n in names:
        ls = [l.strip() for l in out.split("\n") if l.startswith(f"'{n}' depends")]
        if len(ls) != 1:
            raise SystemExit(f"axiom line for {n} in {log.name}: {ls}")
        lines.append(ls[0])
    return lines


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


STATUS = ("producer-only: compiled and axiom-checked by the producing AI agent under the pinned stack and gated by "
          "results/programmes/2026-10-25/P3/gate.py (OVERALL PASS); an independent AI audit (papers/prog_cm_bernstein_library/AUDIT.md) rebuilt all 11 files "
          "and 5 prerequisites from source and re-ran collectAxioms over 167 constants (0 off the allowlist); NO human audit (audit field null); "
          "AutoevolveAI files are uncommitted on base " + BASE)


def lean_ev(mod: str, names: list[str], status: str = STATUS, extra_src: list[Path] | None = None) -> dict:
    log = LOGS / f"{mod}.json"
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(log, names),
            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "compile_transcript": file_ref(log),
            "sources": [file_ref(SRC / f"{mod}.lean")] + [file_ref(p) for p in (extra_src or [])], "status": status,
            "statement_adequacy": "not audited by a human"}


def cite(keys: list[str], **kw: object) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys},
            "excerpt_file": file_ref(HERE / "sources/excerpts.json"), **kw}


def num(files: list[Path], instrument: str, **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "instrument": instrument,
            "files": [file_ref(p) for p in files], **kw}


def arg(text: str, section: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, "paper_section": section, **kw}


P = "ProgCM."
PA = "ProgCM.Applications."
PC = "ProgCMCore."


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    up_log = H1C / "compile_controls.json"
    claims = [
        # ---------------- Tier A ----------------
        rec("CM-A-0001", "A", "lean_axioms",
            "Upstream OAI.AtomicTriangular.universal_energy_minimum (openai/math, AI-generated, not peer reviewed): for every g with AdmissiblePotential g and every C with LocallyFinite C and DensityOne C, latticeEnergy g <= energy g C and latticeEnergy g = energy g A. Certifies the statement about upstream's definitions only.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(up_log, ["OAI.AtomicTriangular.universal_energy_minimum"]),
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "compile_transcript": file_ref(up_log),
                 "sources": [file_ref(UP / "Universal.lean"), file_ref(UP / "Basic.lean")],
                 "status": "upstream theorem, AI-generated, not peer reviewed",
                 "statement_adequacy": "AI-audited only (results/discovery/statement_fidelity.md); no human audit"}),
        rec("CM-A-0002", "A", "lean_axioms",
            "Bridge: ProgCM.isCompletelyMonotoneOn_iff_admissible: IsCompletelyMonotoneOn f <-> OAI.AtomicTriangular.AdmissiblePotential f, where IsCompletelyMonotoneOn f := ContDiffOn R top f (Ioi 0) /\\ forall n t, 0 < t -> 0 <= (-1)^n * iteratedDeriv n f t. The definition is exactly upstream's admissibility (its second clause g >= 0 is the n = 0 case). Wrappers of_admissible, admissible give the two directions.",
            [], lean_ev("Basic", [P + "isCompletelyMonotoneOn_iff_admissible", P + "IsCompletelyMonotoneOn.of_admissible", P + "IsCompletelyMonotoneOn.admissible"])),
        rec("CM-A-0003", "A", "lean_axioms",
            "Closure lemmas (domain (0, infinity)): congr/congr' (only values on (0, infinity) matter), const_mul (c >= 0), add, mul (Leibniz sign lemma), comp_add_const (f(t + c), c >= 0), neg_deriv (-f' is CM), antitoneOn_sign (each (-1)^n f^(n) is antitone), antitoneOn (CM => antitone), sub_comp_add_const (f(t) - f(t + c) is CM for c >= 0, by a mean-value argument), const, zero, sum (finite nonnegative combinations).",
            ["CM-A-0002"], lean_ev("Basic", [P + "IsCompletelyMonotoneOn." + n for n in ["congr", "congr'", "const_mul", "add", "mul", "comp_add_const", "neg_deriv", "antitoneOn_sign", "antitoneOn", "sub_comp_add_const"]] + [P + "const", P + "zero", P + "sum"])),
        rec("CM-A-0004", "A", "lean_axioms",
            "Basic examples: exp_neg_mul (e^(-a t) is CM for a >= 0) and rpow_neg (t^(-s) is CM for s >= 0). Both are obtained through repository modules (AutoresearchKeldysh.expNeg_admissible, TriangularRiesz.riesz_admissible) that import upstream openai/math, not through the Mathlib-only core.",
            ["CM-A-0002"], lean_ev("Basic", [P + "exp_neg_mul", P + "rpow_neg"])),
        rec("CM-A-0005", "A", "lean_axioms",
            "Subordination (general): IsBernsteinOn.comp_sign and IsCompletelyMonotoneOn.comp_bernstein: if f is completely monotone and psi is a Bernstein function (C^infinity, nonnegative, psi' completely monotone) with psi > 0 on (0, infinity), then t |-> f (psi t) is completely monotone. Proved by strong induction on the order over all CM f, using (f o psi)' = -((-f') o psi) psi', the induction hypothesis for -f', and the Leibniz sign lemma; no Faa di Bruno formula.",
            ["CM-A-0003"], lean_ev("Bernstein", [P + "IsBernsteinOn.comp_sign", P + "IsCompletelyMonotoneOn.comp_bernstein"])),
        rec("CM-A-0006", "A", "lean_axioms",
            "Bernstein-function instances and closure: affine (a t + b, a, b >= 0), rpow (t^alpha, 0 <= alpha <= 1), sqrt, add, const_mul, comp (Bernstein o positive Bernstein is Bernstein), monotoneOn; consequences exp_neg_comp (e^(-a psi) CM), comp_affine (f(a t + b)), comp_sqrt (f(sqrt t)), phi_cm (e^(-kappa sqrt t) is CM for kappa >= 0, a one-line re-derivation of the earlier phi_admissible, which needed kappa > 0).",
            ["CM-A-0005", "CM-A-0004"], lean_ev("Bernstein", [P + "IsBernsteinOn." + n for n in ["monotoneOn", "affine", "rpow", "sqrt", "add", "const_mul", "comp"]] + [P + "exp_neg_comp", P + "IsCompletelyMonotoneOn.comp_affine", P + "IsCompletelyMonotoneOn.comp_sqrt", P + "phi_cm"])),
        rec("CM-A-0007", "A", "lean_axioms",
            "Laplace mixtures: integrable_pow_mul (exponential integrability of e^(-ck) m for every c > 0 implies integrability of k^n e^(-ck) m for every n), laplace (k, m measurable, >= 0 a.e., e^(-ck) m integrable for all c > 0 => t |-> integral of e^(-t k) m dmu is CM; this weakens the hypothesis of the earlier laplace_admissible, which assumed all moments), laplace_iteratedDeriv, and laplace_measure (measure on R concentrated on [0, infinity) with finite exponential moments => its Laplace transform is CM; the easy direction of Bernstein-Widder). The analytic core is still the earlier KeldyshCM proof, reused through the bridge. The hard direction of Bernstein-Widder is not proved.",
            ["CM-A-0002"], lean_ev("Laplace", [P + n for n in ["integrable_pow_mul", "laplace", "laplace_iteratedDeriv", "laplace_measure"]])),
        rec("CM-A-0008", "A", "lean_axioms",
            "Limits: of_tendstoLocallyUniformlyOn (F_k CM, every derivative F_k^(n) -> G n locally uniformly on (0, infinity), f = G 0 there => f is CM and f^(n) = G n; smoothness of the limit is derived, not assumed) and of_tendsto_iteratedDeriv (smooth limit assumed, pointwise convergence of every derivative). A merely pointwise limit without smoothness is not proved.",
            ["CM-A-0003"], lean_ev("Limits", [P + "of_tendsto_iteratedDeriv", P + "of_tendstoLocallyUniformlyOn"])),
        rec("CM-A-0009", "A", "lean_axioms",
            "Examples: inv_cm (1/t), inv_affine_cm (1/(a t + b)), one_add_rpow_neg_cm ((t+1)^(-s)), IsBernsteinOn.one_sub_exp (1 - e^(-a t)), IsBernsteinOn.log_one_add (log(1+t)), exp_neg_log_one_add_cm (e^(-a log(1+t)), subordination by log(1+t)).",
            ["CM-A-0005", "CM-A-0006"], lean_ev("Examples", [P + n for n in ["inv_cm", "inv_affine_cm", "one_add_rpow_neg_cm", "IsBernsteinOn.one_sub_exp", "IsBernsteinOn.log_one_add", "exp_neg_log_one_add_cm"]])),
        rec("CM-A-0010", "A", "lean_axioms",
            "H1-H3 as corollaries, complete monotonicity in t = r^2: riesz_cm, yukawa_cm (planar Yukawa e^(-kappa r)/r, kappa >= 0), dipolar_cm (bilayer dipolar exciton 2(1/r - 1/sqrt(r^2+d^2)), every real d, as the difference of a translate), shiftDiff_cm, keldysh_cm (Rytova-Keldysh, mixture-defined, via the weakened Laplace lemma), keldyshReg_cm, and the consistency statements yukawa_admissible', dipolar_admissible' through the bridge.",
            ["CM-A-0003", "CM-A-0006", "CM-A-0007"], lean_ev("Corollaries", [P + n for n in ["riesz_cm", "yukawa_cm", "dipolar_cm", "shiftDiff_cm", "keldysh_cm", "keldyshReg_cm", "yukawa_admissible'", "dipolar_admissible'"]])),
        rec("CM-A-0011", "A", "lean_axioms",
            "New elementary consequences: yukawa_softcore_cm (soft-core Yukawa g_kappa(t + b^2), kappa >= 0, translation closure) and stretchedExp_cm (e^(-a t^alpha), a >= 0, 0 <= alpha <= 1, subordination by t^alpha).",
            ["CM-A-0006", "CM-A-0010"], lean_ev("Corollaries", [P + "yukawa_softcore_cm", P + "stretchedExp_cm"])),
        rec("CM-A-0012", "A", "lean_axioms",
            "Triangular-optimality restatements, CONDITIONAL on upstream CM-A-0001: triangular_optimal (CM g => latticeEnergy g <= energy g C for locally finite density-one C), triangular_yukawa_softcore_optimal, triangular_stretchedExp_optimal. Keldysh-type potentials have infinite lattice energy, where the optimality statement reads top <= top.",
            ["CM-A-0001", "CM-A-0002", "CM-A-0011"], {**lean_ev("Basic", [P + "triangular_optimal"]),
             "axiom_output": axiom_lines(LOGS / "Basic.json", [P + "triangular_optimal"]) + axiom_lines(LOGS / "Corollaries.json", [P + "triangular_yukawa_softcore_optimal", P + "triangular_stretchedExp_optimal"]),
             "sources": [file_ref(SRC / "Basic.lean"), file_ref(SRC / "Corollaries.lean")]}),
        rec("CM-A-0013", "A", "lean_axioms",
            "Negative controls: cos_not_cm (definition not vacuous); sqrt_not_cm and expNeg_not_bernstein (sqrt is Bernstein but not CM; e^(-t) is CM but not Bernstein, so the classes differ); inv_not_bernstein and expNegInv_not_cm (1/t is CM but not Bernstein, and e^(-1/t) is not CM: the inner function must be Bernstein); junk_cm, zero_bernstein, junk_comp_zero_not_cm (the hypothesis psi > 0 of the composition theorem cannot be dropped in this formalisation); signedMix_not_cm (e^(-t) - 2 e^(-2t) is not CM: mixture weights must be nonnegative).",
            ["CM-A-0002", "CM-A-0005"], lean_ev("NegativeControls", [P + n for n in ["cos_not_cm", "sqrt_not_cm", "expNeg_not_bernstein", "inv_not_bernstein", "expNegInv_not_cm", "junk_cm", "zero_bernstein", "junk_comp_zero_not_cm", "signedMix_not_cm"]])),
        rec("CM-A-0014", "A", "lean_axioms",
            "H1, H2, H3 re-derived with their original statements from the library only: H2_yukawa_admissible (0 < kappa), H1_dipolar_admissible (every d; the original dipolar_admissible needed 0 < d), H3_keldysh_admissible (0 < r0). Each is a 2-3 line corollary of the library.",
            ["CM-A-0010"], lean_ev("Applications", [PA + "H2_yukawa_admissible", PA + "H1_dipolar_admissible", PA + "H3_keldysh_admissible"])),
        rec("CM-A-0015", "A", "lean_axioms",
            "New potentials: screenedDipolar_cm (2 (g_kappa(t) - g_kappa(t + d^2)), kappa >= 0, every d), yukawaSpectrum_cm (t |-> integral over kappa > 0 of m(kappa) g_kappa(t) dkappa is CM for measurable m >= 0 with e^(-c kappa) m integrable for every c > 0), the instance yukawaExpSpectrum_cm (m(kappa) = e^(-kappa); the equality of this potential with 1/(r(1+r)) is by hand, not in Lean), secondDiff_cm (f(t) - 2 f(t+c) + f(t+2c)).",
            ["CM-A-0010", "CM-A-0007"], lean_ev("Applications", [PA + n for n in ["screenedDipolar_cm", "yukawaSpectrum_cm", "yukawaExpSpectrum_cm", "secondDiff_cm"]])),
        rec("CM-A-0016", "A", "lean_axioms",
            "quadrupolarPair_cm: for f CM and c >= 0, quadrupolarPair f c t = 2 (3 f(t) - 4 f(t + c) + f(t + 4c)) is CM; proof: it equals Delta_c g + Delta_2c g + Delta_3c g with g = f - f(. + c) and Delta_a h = h - h(. + a), four uses of sub_comp_add_const. Instances quadrupolarCoulomb_cm (f = t^(-1/2), every d) and quadrupolarYukawa_cm (f = g_kappa, kappa >= 0). That this combination is the interaction of two aligned +1,-2,+1 quadrupoles is a Tier C pair counting (CM-C-0002).",
            ["CM-A-0003", "CM-A-0010"], lean_ev("Applications", [PA + n for n in ["quadrupolarPair_cm", "quadrupolarCoulomb_cm", "quadrupolarYukawa_cm"]])),
        rec("CM-A-0017", "A", "lean_axioms",
            "Negative result: quadrupole_neg_at_three (1/sqrt 3 - 2/2 + 1/sqrt 7 < 0, using sqrt 3 > 1.7 and sqrt 7 > 2.6), quadrupole_not_cm (the unit combination t^(-1/2) - 2(t+1)^(-1/2) + (t+4)^(-1/2) is not CM), and quadrupoleC_not_cm (the same combination with shifts 0, c, 4c is not CM for every c > 0, by the scaling t |-> c t via comp_affine). This combination is the field of ONE +1,-2,+1 quadrupole on a test charge, not the interaction of two quadrupoles.",
            ["CM-A-0003"], lean_ev("Applications", [PA + n for n in ["quadrupole_neg_at_three", "quadrupole_not_cm", "quadrupoleC_not_cm"]])),
        rec("CM-A-0018", "A", "lean_axioms",
            "Triangular-optimality restatements for the new potentials, CONDITIONAL on upstream CM-A-0001: triangular_screenedDipolar_optimal, triangular_yukawaSpectrum_optimal, triangular_quadrupolarCoulomb_optimal.",
            ["CM-A-0001", "CM-A-0012", "CM-A-0015", "CM-A-0016"], lean_ev("Applications", [PA + n for n in ["triangular_screenedDipolar_optimal", "triangular_yukawaSpectrum_optimal", "triangular_quadrupolarCoulomb_optimal"]])),
        rec("CM-A-0019", "A", "lean_axioms",
            "Mathlib-only core (MathlibOnly.lean, namespace ProgCMCore, 8 Mathlib.* imports, no openai/math and no repository module): re-proves mul_sign, exp_neg_mul, rpow_neg, the Laplace analytic core (G, G_sign, laplace with a LaplaceData structure carrying only the weakened integrability hypothesis), the closure lemmas, Bernstein affine/rpow/sqrt and comp_bernstein. MathlibOnlyBridge.lean proves ProgCMCore.IsCompletelyMonotoneOn f <-> ProgCM.IsCompletelyMonotoneOn f and the Bernstein analogue, both by Iff.rfl (the definitions are literally identical), and the equivalence with upstream's AdmissiblePotential. It does not contain limits, examples, the Bernstein closure lemmas, laplace_measure, comp_affine, comp_sqrt or the corollaries.",
            ["CM-A-0002"], {**lean_ev("MathlibOnly", [PC + n for n in ["mul_sign", "IsCompletelyMonotoneOn.mul", "IsCompletelyMonotoneOn.sub_comp_add_const", "exp_neg_mul", "rpow_neg", "IsBernsteinOn.comp_sign", "IsCompletelyMonotoneOn.comp_bernstein", "G_sign", "laplace"]]),
             "axiom_output": axiom_lines(LOGS / "MathlibOnly.json", [PC + n for n in ["mul_sign", "IsCompletelyMonotoneOn.mul", "IsCompletelyMonotoneOn.sub_comp_add_const", "exp_neg_mul", "rpow_neg", "IsBernsteinOn.comp_sign", "IsCompletelyMonotoneOn.comp_bernstein", "G_sign", "laplace"]])
             + axiom_lines(LOGS / "MathlibOnlyBridge.json", [PC + n for n in ["isCompletelyMonotoneOn_iff_progCM", "isBernsteinOn_iff_progCM", "isCompletelyMonotoneOn_iff_admissible", "comp_bernstein_progCM"]]),
             "sources": [file_ref(SRC / "MathlibOnly.lean"), file_ref(SRC / "MathlibOnlyBridge.lean")]}),
        rec("CM-A-0020", "A", "lean_axioms",
            "Planted controls (separate file Controls.lean, imported by nothing) are caught by #print axioms: ProgCM.ctl_sorry depends on sorryAx and ProgCM.ctl_axiom on the planted axiom ProgCM.ctl_cheat, although the file compiles with rc 0 (so the exit status is not the gate); both 'prove' the false statement that cos is completely monotone, which cos_not_cm (CM-A-0013) refutes. A paper-stage recompile of Controls.lean gives the identical axiom output (CM-X-0003).",
            ["CM-A-0013"], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                            "axiom_output": axiom_lines(LOGS / "Controls.json", [P + "ctl_sorry", P + "ctl_axiom"]),
                            "raw_output": json.loads((LOGS / "Controls.json").read_text())["output"],
                            "rc": json.loads((LOGS / "Controls.json").read_text())["rc"],
                            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "both controls OUTSIDE the allowlist",
                            "sources": [file_ref(SRC / "Controls.lean"), file_ref(LOGS / "Controls.json")],
                            "statement_adequacy": "control rows; not audited by a human"}),
        # ---------------- Tier L ----------------
        rec("CM-L-0001", "L", "citation",
            "Mathlib at the pin d13f23b7 already contains Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean: def AbsolutelyMonotoneOn (f : R -> R) (s : Set R) via a Taylor series with nonnegative terms, (f^(n) >= 0 for all n: the sign-free mirror of complete monotonicity, CM on (0, infinity) corresponding to absolute monotonicity of f(-x) on (-infinity, 0)); the file proves six theorems: contDiffOn, of_contDiff, iff_iteratedDerivWithin_nonneg, iteratedDerivWithin_nonneg, add and smul; it has no product, composition, translation, Bernstein-function or Laplace-transform lemma. A Mathlib contribution would have to be built on it.",
            [], cite(["mathlib_am_def"], file=file_ref(AM))),
        rec("CM-L-0002", "L", "citation",
            "Cohn-Kumar (J. Amer. Math. Soc. 20 (2007), 99-148, arXiv:math/0607446v2), p. 101: the standard definition of a completely monotonic function ((-1)^k f^(k) >= 0 for all k >= 0, citing Widder p. 145), the convention of potentials as functions of SQUARED distance, and the remark that complete monotonicity of r |-> f(r^2) implies that of f on the squared interval but not conversely.",
            [], cite(["ck_cm_def"])),
        rec("CM-L-0003", "L", "citation",
            "Petrache-Serfaty (arXiv:1908.09714v3): the Cohn-Kumar conjecture (universal minimality of the triangular lattice in dimension 2 among density-1 configurations for completely monotone functions of squared distance) 'remains open in dimension 2' as of 2019; we did not re-check its later status.",
            [], cite(["ps_conjecture"])),
        rec("CM-L-0004", "L", "citation",
            "Salazar (arXiv:2607.04467v1) uses the same definitions on (0, infinity): completely monotone = C^infinity with (-1)^n f^(n) >= 0 for all n >= 0, Bernstein function = C^infinity with g' completely monotone (values in [0, infinity)); and states the Bernstein-Widder theorem (CM iff the Laplace transform of a unique positive Radon measure on [0, infinity)) as standard. The same paper's introduction names 'Bochner subordination' as the composition operation of the CM and Bernstein classes; it does not state or number the composition theorem.",
            [], cite(["sal_defs", "sal_bw", "sal_subord"])),
        rec("CM-L-0005", "L", "citation",
            "Mathlib contribution policy (Lean community 'How to contribute', section 'Use of AI', read 2026-10-25): LLM-written comments on GitHub or Zulip are not allowed; LLM use must be explained in the PR description; AI-written code without the supervision of a Lean subject expert is judged to fall short by a large margin. The fetch tool returned only short verbatim quotations, so the full section was not obtained word for word.",
            [], cite(["mathlib_ai_policy"])),
        # ---------------- Tier C ----------------
        rec("CM-C-0001", "C", "argument",
            "Human proofs of the library's steps (Section 'Step-by-step human demonstration'): closure under sums, positive multiples, products (Leibniz), translation; the mean-value argument that f(t) - f(t+c) is CM; the derivative formulas for e^(-at) and t^(-s); the proof of subordination by strong induction (no Faa di Bruno); the Laplace-mixture argument (differentiation under the integral, u^n e^(-(c/2)u) <= n!/(c/2)^n); and the local uniform limit argument. Each step is mirrored by a Lean statement (Tier A rows CM-A-0002 to CM-A-0008) but the prose proof is not machine-checked.",
            ["CM-A-0003", "CM-A-0005", "CM-A-0007", "CM-A-0008"], arg("See paper Section 3; the Lean proofs are the checked versions.", "Step-by-step human demonstration")),
        rec("CM-C-0002", "C", "argument",
            "Quadrupole pair counting: charges +1, -2, +1 in layers z = 0, d, 2d with pair interaction f(r^2 + dz^2) interact, for two aligned quadrupoles at in-plane distance r, by sum_{i,j} q_i q_j f(t + (z_i - z_j)^2); dz = 0 contributes 1 + 4 + 1 = 6, |dz| = d contributes 4(-2) = -8, |dz| = 2d contributes 2(1) = 2, so 6 f(t) - 8 f(t+c) + 2 f(t+4c) = 2(3 f(t) - 4 f(t+c) + f(t+4c)) with c = d^2. The field of ONE quadrupole on a single test charge is the different combination f(t) - 2 f(t+c) + f(t+4c) (weights 1,-2,1, shifts 0,c,4c). Laplace symbols in x = e^(-uc): 3 - 4x + x^4 = (1-x)^2 (x^2 + 2x + 3) >= 0 on [0,1], while 1 - 2x + x^4 < 0 near x = 0.79. Rigid, aligned, classical point charges.",
            ["CM-A-0016", "CM-A-0017"], arg("Hand derivation, checked by expansion; see paper Section 'Applications'.", "Applications")),
        rec("CM-C-0003", "C", "argument",
            "Gloss of CM-A-0012 and CM-A-0018: for the listed potentials (soft-core Yukawa, stretched exponential, Yukawa-screened bilayer exciton, Yukawa mixtures with nonnegative spectral density, Coulomb quadrupolar interaction) no locally finite configuration of density one has lower (liminf) energy than the triangular lattice, CONDITIONAL on the upstream theorem CM-A-0001 (AI-generated, not peer reviewed) and on the fidelity of its definitions. It says nothing about uniqueness, quantum effects, or the models' physical validity. Finiteness of the optimal energy is not proved for these potentials, so for Coulomb-like tails the statement can read top <= top.",
            ["CM-A-0012", "CM-A-0018", "CM-L-0003"], arg("Tier A attaches to the Lean statement; this is its physical gloss.", "Applications and limitations")),
        rec("CM-C-0004", "C", "argument",
            "By hand: for m(kappa) = e^(-kappa) the Yukawa spectrum potential is 1/(r(1+r)), since the integral over kappa > 0 of e^(-kappa) e^(-kappa r)/r dkappa = 1/(r (1 + r)). The Lean theorem yukawaExpSpectrum_cm is about the integral form; the closed form was checked only by the Tier X screen and is not machine-checked.",
            ["CM-A-0015"], arg("Elementary integral.", "Applications")),
        rec("CM-C-0005", "C", "argument",
            "Classical context, stated without a verified pin: that every completely monotone function is a Laplace transform of a positive measure (the hard direction of Bernstein-Widder; its statement is quoted in CM-L-0004 and it is NOT proved here), and that the composition of a completely monotone function with a Bernstein function is completely monotone (named 'Bochner subordination' in CM-L-0004; the theorem number in Schilling-Song-Vondracek was not verified). Our Lean theorem comp_bernstein is a machine-checked proof of the latter on (0, infinity) with the extra hypothesis psi > 0, not a citation of it. No literature search was made for novelty of any result in this paper, and none is claimed.",
            ["CM-L-0004", "CM-A-0005"], arg("Attribution only.", "Introduction and limitations")),
        rec("CM-C-0006", "C", "argument",
            "Mathlib readiness (not a Mathlib claim): a pull request would have to rebase the definition on the existing AbsolutelyMonotoneOn (CM-L-0001), make it set-parametric, rename IsBernsteinOn (the name bernstein is already used for Bernstein polynomials), drop the duplication between Basic/Bernstein and MathlibOnly, adopt the module system, shorten lines over 100 characters (22 in MathlibOnly.lean, 24 in Basic.lean at the time of counting) and run the Mathlib linters, which have NOT been run. Human review by a Lean expert is required by the policy in CM-L-0005. No pull request or Zulip post has been made.",
            ["CM-L-0001", "CM-L-0005", "CM-A-0019"], arg("Assessment from results/programmes/2026-10-25/P3/MATHLIB_READINESS.md.", "Mathlib readiness", note_file=file_ref(P3 / "MATHLIB_READINESS.md"))),
        # ---------------- Tier X ----------------
        rec("CM-X-0001", "X", "numeric",
            "Tier X screen of 14 candidate potentials for complete monotonicity (mpmath, 60 digits, derivatives n = 0..7, 15 values of t from 1e-3 to 1e4): the positive controls t^(-1/2) and e^(-sqrt t)/sqrt t show no negative value; the four negative controls (cos t, t^(-1/2) - 2(t+1)^(-1/2), g_1 - 2 g_2, and the wrong-weights 2 f(t) - 3 f(t+1) + f(t+4)) all show a negative value (minimum -0.0048 for the last one, at n = 0, t = 10); the candidate charge-quadrupole combination shows its minimum -0.0443 at n = 0, t = 3.16 (the Lean theorem CM-A-0017 gives the sign at t = 3); the seven other candidates show no negative value, which is consistent with, and never a proof of, their CM status (the proofs are the Lean theorems).",
            ["CM-A-0017"], num([APP / "numeric_check.json", APP / "cm_numeric_check.py"], "mpmath 60-digit numerical differentiation, script cm_numeric_check.py (stage WORK2, same AI pipeline)")),
        rec("CM-X-0002", "X", "numeric",
            "Proof-length measurement (deterministic counts, filed Tier X because they are tool measurements and not Lean statements): the dependency closure of each root theorem is computed by Lean over the kernel terms, restricted to repository declarations (Mathlib and upstream excluded on both sides) and counted in non-blank non-comment source lines. Headline lines original -> library: H2 2 -> 2, H1 (d > 0) 23 -> 3, H1 (every d) 3 -> 3, H3 8 -> 2. Closure lines (declarations): H2 84 (13) -> 274 (50), H1 every d 72 (12) -> 95 (17), H3 250 (34) -> 304 (43); union of the three 406 (59) -> 505 (77); plus screened dipolar and Yukawa spectrum 527 (82); plus the two quadrupolar interactions 548 (87). Scope of the method: the closure keeps only Programmes.* and Autoresearch.* declarations, so Mathlib, upstream OAI.* and the repository's Triangular.* modules are excluded on both sides; overlapping structure/field line ranges are counted twice on both sides. Reading of the counts (an explanation of the measurement, kept at Tier X): the library shortens the headline proofs only against the earliest versions of H1 (23 -> 3 lines) and H3 (8 -> 2); end to end it is LONGER for the three existing results (406 lines in 59 declarations before, 505 in 77 through the library), because Basic.exp_neg_mul routes through the KeldyshCM Laplace core, which then appears in the closure of every exponential-based result (the Mathlib-only core would avoid it but was not used); the library pays off at the margin, since adding the screened-dipolar and Yukawa-spectrum results costs 22 lines and the two quadrupolar interactions 21 more.",
            [], num([APP / "proof_length.json", APP / "proof_length_union.json", APP / "closure_raw.json", APP / "Closure.lean.txt", APP / "proof_length.py"], "Lean closure script Closure.lean.txt run under the pinned stack + proof_length.py (stage WORK2, same AI pipeline)")),
        rec("CM-X-0003", "X", "numeric",
            "Paper-stage recompiles by the same AI pipeline (NOT producer != verifier, and covering 3 of the 11 Lean files only): Bernstein.lean (rc 0, 15.2 s), Controls.lean (rc 0, 13.2 s) and Applications.lean (rc 0, 12.6 s) were elaborated again under the pinned stack WITHOUT writing oleans; they import the producer's oleans for Basic, Laplace, Corollaries and the rest, so those modules were not re-elaborated. The printed axiom output of each is byte-identical to the producer-stage log. The gate gate.py was re-run unchanged on the stored logs (OVERALL PASS, gate.json identical).",
            ["CM-A-0005", "CM-A-0014", "CM-A-0020"], num([REC / "Bernstein.json", REC / "Controls.json", REC / "Applications.json", P3 / "gate.json", P3 / "gate.py"], "lean_pinned.py compile (Lean 4.34.1) and gate.py")),
        rec("CM-X-0004", "X", "numeric",
            "Figures: fig_symbols shows the polynomial Laplace symbols p(x), x = e^(-uc) in [0,1], of the dipolar, second-difference and quadrupolar combinations (the charge quadrupole 1 - 2x + x^4 has minimum -0.1905 at x = 0.79; the wrong-weights control 2 - 3x + x^4 has minimum -0.0443 at x = 0.91; the pair 2(3 - 4x + x^4) is nonnegative); fig_profiles shows t^(3/2) F(t) on a numpy grid (the charge quadrupole is negative from about t = 3 and tends to -1, the pair is positive); fig_prooflen plots CM-X-0002. All are produced by gen_inputs.py.",
            ["CM-X-0001", "CM-X-0002", "CM-C-0002"], num([HERE.parent / "gen_inputs.py", HERE.parent / "data/gen_summary.json"], "numpy/matplotlib in gen_inputs.py")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
