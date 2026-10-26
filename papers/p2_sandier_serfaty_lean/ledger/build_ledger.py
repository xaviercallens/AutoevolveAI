"""Build the Elenchus claim ledger for the A1 paper (papers/p2_sandier_serfaty_lean). Prefix P2SS.

Same conventions as papers/prog_sandier_serfaty_audit/ledger/build_ledger.py: every claim has a content-addressed evidence blob
(evidence/<sha256>.json). A rows (lean_axioms) carry VERBATIM `#print axioms` lines taken from the saved compile transcripts and
rest on nothing; L rows carry a transcribed excerpt; C rows (argument) rest only on A/L/C rows; X rows (numeric) may rest on anything and
are never depended on by a higher-tier row. Gate: tools/ledger.py ledger.json --evidence-dir evidence (see run_gate.py).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
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
DATA = PAPER / "data"
LEAN = W / "formal_cert/Programmes/SandierSerfaty"
A1 = W / "results/proposal2/2026-10-26/A1"
TOOLCHAIN = ("Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, pinned openai/math stack "
             "(scripts/certified_numerics/lean_pinned.py)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
PRODUCER = ("producer run (one AI agent wrote the generators and the Lean files); 13 modules rebuilt byte-identically and the must-fail files re-run by a separate AI agent "
            "(AUDIT.md, STATEMENT_LOCK.json); the other 28 chunk files, CalcK.lean and CalcLam.lean not rebuilt independently; no human audit of the statements")
EXC = json.loads((HERE / "sources/excerpts.json").read_text())


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    rel = str(p.relative_to(W)) if str(p).startswith(str(W)) else str(p)
    return {"path": rel, "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


# ---- verbatim axiom lines from the saved transcripts -------------------------------------------------------------------------
TRANSCRIPTS = ["AxiomsAll", "Axioms", "AxiomsCalcK", "Controls", "CalcControls", "Bridge", "SignedEndpoints", "ChainLink"]
_LINES: list[tuple[str, str]] = []
for _t in TRANSCRIPTS:
    _o = json.loads((DATA / f"compile_{_t}.json").read_text())["output"].replace("\n ", " ")
    for _ln in _o.split("\n"):
        if _ln.startswith("'"):
            _LINES.append((_t, _ln.strip()))


def axl(names: list[str]) -> tuple[list[str], list[str]]:
    """Return (verbatim lines, transcripts used). Each short name must resolve to exactly one distinct line."""
    out, used = [], []
    for n in names:
        hits = sorted({(t, ln) for t, ln in _LINES if re.match(rf"'[A-Za-z0-9_.]*\.{re.escape(n)}'", ln)})
        lines = {ln for _, ln in hits}
        if len(lines) != 1:
            raise SystemExit(f"axiom line for {n}: {len(lines)} distinct hits {hits}")
        out.append(next(iter(lines)))
        used.append(hits[0][0])
    return out, sorted(set(used))


def lean_ev(names: list[str], sources: list[str], status: str, expected: str | None = None) -> dict:
    lines, used = axl(names)
    ev = {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines, "allowlist": ALLOW,
          "compile_transcripts": [file_ref(DATA / f"compile_{t}.json") for t in used],
          "sources": [file_ref(LEAN / s) for s in sources], "status": status,
          "statement_adequacy": "not audited by a human; the gloss of each statement is a Tier C claim"}
    if expected:
        ev["expected"] = expected
    return ev


def num(files: list[Path], instrument: str, **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "instrument": instrument,
            "files": [file_ref(p) for p in files], **kw}


def arg(files: list[Path], text: str) -> dict:
    return {"kind": "argument", "text": text, "text_files": [file_ref(p) for p in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    nums = json.loads((DATA / "cost_numbers.json").read_text())
    rej = json.loads((DATA / "reject_map.json").read_text())
    res = json.loads((DATA / "result.json").read_text())
    lfx = json.loads((DATA / "leanflow_result_exact.json").read_text())
    lfp = json.loads((DATA / "leanflow_result_planted.json").read_text())
    lf_lines = [ln for ln in lfx["output_excerpt"].split("\n") if ln.startswith("'cert_")]
    assert len(lf_lines) == 12 and all("does not depend on any axioms" in ln for ln in lf_lines)
    S = "A1 run 2026-10-26 (Proposal 2); " + PRODUCER
    CP, RL = DATA / "CERTIFICATE_PORT.md", DATA / "REDUCTION_LEMMA.md"

    claims = [
        # ---------------------------------------------------------------- Tier A
        rec("P2SS-A-0001", "A", "lean_axioms",
            "Level L2 for stage init_constants (Constants.lean): the real numbers log 2, pi, p = sqrt(2/sqrt 3)/2, R0 = 2p/sqrt 3 and a = 2p lie in the interval enclosures [u/Q, v/Q], Q = 2^144, whose integer endpoints are the literals ln2C, piC, pC, RC, aC of the file (log_two_mem, pi_mem, p_mem, R_mem, a_mem). Proved from Mathlib (log series bound, Machin's formula, Real.hasSum_arctan) plus kernel-decided rational comparisons. A statement about real numbers and those literals; that the literals are what the C++ printed is a separate observation (P2SS-X-0001).",
            [], lean_ev(["log_two_mem", "pi_mem", "p_mem", "R_mem", "a_mem"], ["Constants.lean", "IV.lean"], S)),
        rec("P2SS-A-0002", "A", "lean_axioms",
            "Level L1 for stage init_constants: the Lean transcription of the C++ loops (200-term atanh series for log 2, Machin with 150 terms per arctangent for pi, sqrt chain for p, R0, a) over the Lean interval operations, evaluated by the kernel (decide +kernel), equals the integer endpoint literals ln2C, piC, pC, RC, aC (ln2_comp_eq, pi_comp_eq, p_comp_eq, R_comp_eq, a_comp_eq).",
            [], lean_ev(["ln2_comp_eq", "pi_comp_eq", "p_comp_eq", "R_comp_eq", "a_comp_eq"], ["Constants.lean", "IV.lean"], S)),
        rec("P2SS-A-0003", "A", "lean_axioms",
            "Level L1 for stage bcons/eps: bcons_comp_eq, the kernel evaluation of the transcribed interval log (range reduction + 200-term atanh), pow, the combinatorial factors, Horner evaluation, the 38 edge values VR_m and bcons = -log R + (pi/2) R^2 + sum VR_m + eps equals the literal bconsC. Inputs co[1..38] (stage cs) are premises written into the file.",
            [], lean_ev(["bcons_comp_eq"], ["Bcons.lean", "IV.lean"], S)),
        rec("P2SS-A-0004", "A", "lean_axioms",
            "Level L1 for stage calcLam: calcLam_chunk_sums (the exact sums of the 300 + 300 chunk values), calcLam_eq (the scalar part of calcLam gives exactly the C++ lambda and mu), and calcLam_stage in Chain.lean (conjunction of all 600 chunk theorems chunkEacc/chunkFacc over midpoint steps 150c..150c+149 and calcLam_eq). Conditional on the table enclosures (nodes and cells, stage 3, written into the files as literals) and on l.",
            [], lean_ev(["calcLam_chunk_sums", "calcLam_eq", "calcLam_stage"], ["CalcLam.lean", "CalcLamCore.lean", "Chain.lean", "IV.lean"], S)),
        rec("P2SS-A-0005", "A", "lean_axioms",
            "Level L1 for stage calcK: calcK_mesh (the sample counts are 3103 and 1552), calcK_K_eq (K = 2(kc + [-er, er]), er = h^2 (R/2) |ss|/24, equals the C++ K) and calcK_stage in Chain.lean (conjunction of the 97 midpoint-sum chunk theorems chunkS, the 194 G_ss-hull chunk theorems chunkF, calcK_mesh and calcK_K_eq). Conditional on the table enclosures (stage 3) and on l.",
            [], lean_ev(["calcK_mesh", "calcK_K_eq", "calcK_stage"], ["CalcK.lean", "CalcKCore.lean", "Chain.lean", "IV.lean"], S)),
        rec("P2SS-A-0006", "A", "lean_axioms",
            "premises_chain (Chain.lean): the premises written into the calcK file (kp, kR, klam, kmu) equal the Constants outputs (pC, RC) and the calcLam outputs (lambdaC, muC); the K literal of Asserts equals the calcK output; bconsC = bconC; eps = [-rat(1e-11).v, rat(1e-11).v]; the bcons eps equals the calcK eps. This links the stage outputs to the premises of the next stage.",
            [], lean_ev(["premises_chain"], ["Chain.lean"], S)),
        rec("P2SS-A-0007", "A", "lean_axioms",
            "Level E (endpoint arithmetic) on the exact C++ endpoints (Asserts.lean): printed_pairs (each of the 22 pairs of certificate-record.txt equals (floor(1e7 u/Q), ceil(1e7 v/Q)) of the exact interval), rat_consts_eq, cpp_asserts (every assertion that the C++ makes after calcK (lambda range, K<0, f(l)>0, slope, the two global_grid assertions, the inside_hess minima) plus the |c_1| < 1 check, evaluated on the exact endpoints; the core_test bound check of stage 4 (core.hpp:274) is NOT covered, and the table separation check (core.hpp:251) is checked only window by window) and grid_margins. Arithmetic about the stated integers only; it does not show the C++ computed them (stages 3, 4, 9-12 are not ported).",
            [], lean_ev(["printed_pairs", "rat_consts_eq", "cpp_asserts", "grid_margins"], ["Asserts.lean", "IV.lean"], S)),
        rec("P2SS-A-0008", "A", "lean_axioms",
            "Conditional level L2 for the assertions (Asserts.lean): lambda_real, K_real, fl_real, slope_real, gmf_real, neglhs_real state the real meaning of the assertions (-6.731 < lambda < -6.729, K < 0, f(l) > 0, -pi B(l) - lambda/2 > 0, gmin - factor > 0, negative-part left-hand side < 0) conditional on the real quantity lying in its interval. That the intervals enclose the manuscript's quantities is not part of these theorems.",
            [], lean_ev(["lambda_real", "K_real", "fl_real", "slope_real", "gmf_real", "neglhs_real"], ["Asserts.lean", "IV.lean"], S)),
        rec("P2SS-A-0009", "A", "lean_axioms",
            "Soundness of the Lean interval operations over the reals (IV.lean): if reals lie in the input intervals the real result lies in the output interval, for +, -, negation, x, inv, /, rat, ofInt, and hull (add_sound, neg_sound, sub_sound, mul_sound, inv_sound, div_sound, rat_sound, ofInt_sound, hull_sound_left).",
            [], lean_ev(["add_sound", "neg_sound", "sub_sound", "mul_sound", "inv_sound", "div_sound", "rat_sound", "ofInt_sound", "hull_sound_left"], ["IV.lean"], S)),
        rec("P2SS-A-0010", "A", "lean_axioms",
            "ProgSandierSerfaty.Reduction.signed_endpoints (SignedEndpoints.lean) and its helper lemmas gPrim_neg and integral_ge_of_negPart: for an even, interval-integrable G(d,.) with K < 0, 2 g_d(x) >= K for x >= 0 and the lintegral of ofReal(-G) over (0,infinity) at most ofReal(-K), one has K <= g_d(d tan a) + g_d(d tan b) for |a|,|b| < pi/2, a + b > 0 (g_d = interval integral of G(d,.) from 0 to x). Abstract G; no use of the concrete radial data of the manuscript.",
            [], lean_ev(["signed_endpoints", "gPrim_neg", "integral_ge_of_negPart"], ["SignedEndpoints.lean"], S)),
        rec("P2SS-A-0011", "A", "lean_axioms",
            "assembly_algebra (the final algebraic step of the manuscript's Proposition dual:assembly: sector bounds J(S) >= K + lambda A(S) + mu theta(S), total area N, total angle 2 pi N, at most 6N sectors, K <= 0 give sum J >= N(6K + lambda + 2 pi mu); the geometric inputs are hypotheses) and b_lt_dstar (0.28209 < 1/(2 sqrt pi)).",
            [], lean_ev(["assembly_algebra", "b_lt_dstar"], ["SignedEndpoints.lean"], S)),
        rec("P2SS-A-0012", "A", "lean_axioms",
            "Constant bridge to the P1 statement file (Bridge.lean): tri_eq_triScale (the certificate's tri equals ProgSandierSerfaty.triScale), a_mem_triScale (aC contains triScale) and p_mem_triScale (pC contains triScale/2).",
            [], lean_ev(["tri_eq_triScale", "a_mem_triScale", "p_mem_triScale"], ["Bridge.lean", "Constants.lean"], S)),
        rec("P2SS-A-0013", "A", "lean_axioms",
            "Honest refutations of the planted claims (Controls.lean, CalcControls.lean): the Lean kernel proves ctl_ln2_199_ne (199-term log 2 differs from the C++ endpoints), ctl_pi_noslack_ne, ctl_pi_shift_false (pi lower endpoint + 2^100 ulps is not below the Machin enclosure), ctl_pair_false ((121,162) is not the pair of gmf), ctl_gmf_121_false, ctl_erdrop_x2_false, ctl_det_false, ctl_G_eight_to_four (H^2/8 -> H^2/4 in the lookup) and, at stage level, ctl_calcK_er12_ne (K with /24 -> /12) and ctl_calcLam_evipp12_ne (calcLam with the /24 -> /12 allowance). These are proofs that the perturbed claims are false, i.e. the stage statements are not vacuous.",
            [], lean_ev(["ctl_ln2_199_ne", "ctl_pi_noslack_ne", "ctl_pi_shift_false", "ctl_pair_false", "ctl_gmf_121_false", "ctl_erdrop_x2_false", "ctl_det_false", "ctl_G_eight_to_four", "ctl_calcK_er12_ne", "ctl_calcLam_evipp12_ne"],
                        ["Controls.lean", "CalcControls.lean"], S)),
        rec("P2SS-A-0014", "A", "lean_axioms",
            "Controls for signed_endpoints (Controls.lean): ctl_signed_without_sum_false (for G = 1, K = -1, d = 1, a = b = -pi/4 the conclusion fails, so the hypothesis a + b > 0 is load-bearing) and ctl_signed_hyps (the same G = 1 satisfies every other hypothesis, so the theorem applies to it: non-vacuity).",
            [], lean_ev(["ctl_signed_without_sum_false", "ctl_signed_hyps"], ["Controls.lean", "SignedEndpoints.lean"], S)),
        rec("P2SS-A-0016", "A", "lean_axioms",
            "LeanFlow tactic decide_kernel (commit 06084ef5c40057c66c476feba18ea3da8fb150ba): the 12 assertions about the exact endpoints (lambda in (-6.731,-6.729), K < 0, f(l) > 0, slope > 0, gmin - factor >= 1.20e-5, drneg + er_drop + K <= -4.585e-4, g_dd, g_xx, det > 0, |c_1| < 1 both sides) are each accepted by the Lean kernel; every theorem 'does not depend on any axioms'. Arithmetic about the stated integers only (level E).",
            [], {"kind": "lean_axioms", "toolchain": "core Lean 4.34.1 (decide +kernel via LeanFlow 'decide_kernel'); LeanFlow commit 06084ef5c40057c66c476feba18ea3da8fb150ba",
                 "axiom_output": lf_lines, "allowlist": ALLOW, "n_assertions": len(lfx["assertions"]), "tier_scope": lfx["tier_scope"],
                 "claim_sha256": lfx["claim_sha256"], "statement_sha256": lfx["statement_sha256"],
                 "compile_transcripts": [file_ref(DATA / "leanflow_result_exact.json"), file_ref(DATA / "leanflow_claim_exact.json")],
                 "sources": [file_ref(DATA / "leanflow_claim_exact.json")], "status": S,
                 "statement_adequacy": "not audited by a human"}),
        rec("P2SS-A-0017", "A", "lean_axioms",
            "ChainLink.lean (new file added after the audit; the 52 locked files are unchanged): slope_eq (the slope literal slopeC of Asserts equals -pi*bconsC - lambdaC/2 recomputed with the Lean interval operations) and fl_eq (the f(l) literal flC equals f0lC - lambdaC*kl*kl/2 - muC; conditional on f0lC, a table value of the unported stage 3). Links the stage-8 literals to the L1 outputs.",
            [], lean_ev(["slope_eq", "fl_eq"], ["ChainLink.lean", "Asserts.lean", "Bcons.lean", "CalcKCore.lean", "IV.lean"], S)),
        # ---------------------------------------------------------------- Tier L
        rec("P2SS-L-0001", "L", "citation",
            "Sandier-Serfaty 2012 (arXiv:1011.4617v2): the triangular lattice is the unique minimizer among lattices (Theorem 2, p.5) and its minimality among all configurations is Conjecture 1 (p.5); 'its minimization in general remains open' (abstract). Transcription of the P1 excerpt; the cited page was read by the P1 paper-stage agent, the passage was not re-read here and citation_check.py was not run in this paper.",
            [], {"kind": "citation", "excerpts": {k: EXC[k] for k in ["ss_open", "ss_conj"]}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"),
                 "citation_check_run": False,
                 "citation_check": {"note": "not run for this paper; P1 (doi:10.5281/zenodo.23653827) ran it on the Theorem 2 passage, the Conjecture 1 sentence being outside the tool's kinds"}}),
        # ---------------------------------------------------------------- Tier C
        rec("P2SS-C-0001", "C", "argument",
            "Scope: the Sandier-Serfaty conjecture is NOT formally proved by this work, nor is any claim of the openai/math manuscript (AI-generated, not peer reviewed) beyond the items listed. Kernel-checked: 4 of 12 certificate stages re-executed (level L1: init_constants, bcons/eps, calcLam, calcK, the last two conditional on the table enclosures, which are premises), 1 of 12 with a real-number statement (level L2: init_constants), the executable assertions on the exact C++ endpoints (level E), one reduction lemma (signed_endpoints), one algebraic step and one numeric fact. Nothing joins the certificate to the reduction in Lean. The conjecture was open in the human literature (L-0001); we did not search for later resolutions.",
            ["P2SS-A-0002", "P2SS-A-0003", "P2SS-A-0004", "P2SS-A-0005", "P2SS-A-0006", "P2SS-A-0007", "P2SS-A-0001", "P2SS-A-0010", "P2SS-L-0001"],
            arg([CP, RL], "Counting convention: a stage counts as L1 complete only if its full computation (every chunk) is re-executed with the premises of earlier stages as explicit hypotheses; stage rows of CERTIFICATE_PORT.md.")),
        rec("P2SS-C-0002", "C", "argument",
            "Classification of the 12 stage rows by checking level (CERTIFICATE_PORT.md): L1 complete: init_constants, bcons/eps, calcLam, calcK (4/12). L2 complete: init_constants (1/12). Level E only (assertions on the exact endpoints): the assertions after calcK, global_grid outer, global_grid negative, inside_hess, the lattice-sum bound |c_1| < 1 and the 22 printed pairs. Not ported: cs, table, core_test, bdsup, and the computations of global_grid and inside_hess. The classification is an argument from the theorem statements of A-0001..A-0008 and A-0016; the choice of row granularity (12 rows) is ours.",
            ["P2SS-A-0001", "P2SS-A-0002", "P2SS-A-0003", "P2SS-A-0004", "P2SS-A-0005", "P2SS-A-0007", "P2SS-A-0008", "P2SS-A-0016"],
            arg([CP, DATA / "result.json"], "Stage map in CERTIFICATE_PORT.md; the 'stages' list of result.json.")),
        rec("P2SS-C-0003", "C", "argument",
            "Fidelity of the transcription C++ -> Lean for the ported stages: argued from bit equality of the Lean kernel evaluation with the integer endpoints printed by the C++ (A-0002..A-0005 are equalities to those literals) and from reading the transcribed code (IV.mul uses the min/max of the four endpoint products where the C++ uses a nine-way sign split; the argument is that both choose the same two products). Not proved: a transcription that differs from the C++ on inputs not exercised would not be caught. L1 does not relate the numbers to the manuscript's real quantities (that is level L2).",
            ["P2SS-A-0002", "P2SS-A-0003", "P2SS-A-0004", "P2SS-A-0005", "P2SS-A-0009"],
            arg([CP], "Section 'Levels' of CERTIFICATE_PORT.md; the equality theorems are the evidence of agreement on the exercised inputs.")),
        rec("P2SS-C-0004", "C", "argument",
            "What the chain does not check: (i) the tiling of the index sets by the chunk ranges (97 chunks of 32 for 3103 midpoint indices, 194 chunks of 8 for 1552 hull indices, 300 + 300 chunks of 150 for 45000 steps) is guaranteed by the generator, not by Lean; the ranges are visible in the statements and were checked contiguously by a script (X-0007); (ii) the inputs taken as given: the table enclosures (nodes and cells), co[m] (lattice coefficients), l, and the display of the 22 pairs; (iii) that the intervals contain the manuscript's real quantities for any stage other than init_constants; (iv) the stages not ported.",
            ["P2SS-A-0004", "P2SS-A-0005", "P2SS-A-0006", "P2SS-A-0008"],
            arg([CP], "Premises of the chain are the explicit hypotheses of the chunk theorems; Chain.lean docstring and CERTIFICATE_PORT.md 'Details of the ported stages'.")),
        rec("P2SS-C-0005", "C", "argument",
            "Fidelity of signed_endpoints to the manuscript's Lemma dual:signed-endpoints (03-geometry.tex lines 567-611, SHA-256 1b8446c6849e...): K < 0, d0 > 0, G even and locally integrable for d >= d0, g_d(x) = int_0^x G(d,s) ds, 2 g_d(x) >= K for x >= 0, int_0^infinity max{0,-G} <= -K imply the conclusion for |a|,|b| < pi/2, a + b > 0; the negative-part hypothesis is a lintegral valued in [0,infinity] so that an infinite integral violates it instead of producing the Bochner junk value 0. Item-by-item comparison by an AI agent; no human has compared the Lean statement with the TeX. Prior fixed deviation: the lemma is stated for an abstract G and uses neither SandierSerfatyStatement.lean nor the P3 library.",
            ["P2SS-A-0010", "P2SS-A-0014"],
            arg([RL], "Fidelity table in REDUCTION_LEMMA.md.")),
        rec("P2SS-C-0006", "C", "argument",
            "Trust base of level L1: the checks use decide +kernel, i.e. the Lean kernel evaluates the transcribed computation (including the arbitrary-precision integer literal arithmetic that the kernel implements natively, which stays in the trusted base), whereas native_decide would trust the compiled evaluator and add an axiom. #print axioms of the L1 theorems shows none or only propext. This removes the C++ compiler, Boost, OpenMP and the hardware that ran the C++ from the trust base of the ported stages; it does not remove the transcription fidelity (C-0003).",
            ["P2SS-A-0002", "P2SS-A-0004", "P2SS-A-0005"],
            arg([CP], "The statement 'native_decide adds an axiom' is from P1's finding for Lean 4.34.1 (t._native.native_decide.ax_1_1 instead of Lean.ofReduceBool); it is not re-tested here.")),
        rec("P2SS-C-0007", "C", "argument",
            "What remains of the analytic reduction: of the 31 numbered steps audited in P1 (R1-R10, G1-G7, K1-K8, T1-T6), only G6 is complete in Lean and only the algebraic part of G7; the other 29 steps and the geometric part of G7 are untouched (30 items). The assessment of what Mathlib lacks (weak div/curl equations with point charges, torus Green function, Voronoi tessellation of periodic point sets, midpoint-rule remainder; present: the Weierstrass function file, a trapezoidal-rule file) is an estimate; the pinned-Mathlib scan (X-0008) is a string search, not a proof of absence.",
            ["P2SS-A-0010", "P2SS-A-0011"],
            arg([RL], "Table 'What remains of the reduction' in REDUCTION_LEMMA.md; the count 31 and the step names come from the P1 REDUCTION_AUDIT.")),
        rec("P2SS-C-0008", "C", "argument",
            "Limitations: one AI agent wrote the generators and the Lean files and ran the original checks. A separate AI agent instance (not a person) audited the paper (AUDIT.md, verdict ACCEPT_WITH_CORRECTIONS; STATEMENT_LOCK.json): it rebuilt 13 modules from source in its own olean directory with byte-identical oleans, re-ran the three must-fail files (7 + 2 + 2 errors, rc 1) and the axiom aggregates (615, 294, 44 reports), and type-checked Chain.lean; the other 28 chunk files, CalcK.lean and CalcLam.lean were NOT rebuilt independently; LeanFlow was not re-run. No human audit of any statement (an agent audit is not the certification the LEDGER_UNAUDITED_TIER_A flag asks for); the gmin, drneg, factor, er_drop and Hessian endpoints come from an instrumented copy of the C++ (counters and endpoint prints only; its log reproduces all 22 record pairs), the others from a dump driver over the unmodified headers; CalcKCore.lean was rewritten byte-identically by its generator after its olean was built; compile times were measured at machine load average 12-16.",
            ["P2SS-A-0002"], arg([CP, DATA / "result.json", PAPER / "AUDIT.md", A1 / "STATEMENT_LOCK.json"], "Caveats section of CERTIFICATE_PORT.md; 'stale_oleans' in result.json; the independent AI audit in AUDIT.md and the file hashes in STATEMENT_LOCK.json.")),
        # ---------------------------------------------------------------- Tier X
        rec("P2SS-X-0001", "X", "numeric",
            "Origin of the endpoint literals: the integer endpoints and the per-stage operation counts come from the C++ certificate. A dump driver (cpp/dump_driver.cpp) was compiled against the unmodified corpus headers (core.hpp c7f76596..., grids.hpp 4640e0a3...) and run once (user time 500.75 s, wall 8:37); the endpoints of gmin, drneg, factor, er_drop and the Hessian hulls and all operation counts come from an instrumented copy (counters and endpoint prints only; single thread, wall 19:00) whose log reproduces all 22 pairs of certificate-record.txt. Totals: 1,685,129 of 1,238,829,689 IV mul+inv (0.136 %).",
            ["P2SS-A-0007"], num([DATA / "sha256.txt", DATA / "dump_scalars.txt", DATA / "dump_driver_time.log", DATA / "counted_run.err", DATA / "counted_run.out", DATA / "result.json"],
                                 "g++ build of cpp/dump_driver.cpp and of the patched copy (cpp/patch_counters.py)",
                                 note="Counts are single-thread, on the instrumented copy; the second invocation of init_constants (init_constants_again) is not in the denominator; the VR_m evaluations of init_after_co that bcons re-executes are not credited in the numerator, so the share is conservative.")),
        rec("P2SS-X-0002", "X", "numeric",
            "Compilation record under pinned Lean 4.34.1 + Mathlib d13f23b7 (cores 4,5): of the 54 saved compile transcripts 51 have rc 0 and the 3 must-fail files rc 1; only the transcript of Controls.lean contains a sorry warning (the planted ctl_sorry_pi); audit aggregate over AxiomsAll.lean: 615 reports, 603 with [propext], 6 with no axioms, 6 with [propext, Classical.choice, Quot.sound], none outside the whitelist.",
            ["P2SS-A-0002"], num([DATA / "result.json", DATA / "axioms_all_summary.json", DATA / "compile_Chain.json", DATA / "compile_AxiomsAll.json"], "lean_pinned.py compile (scripts/certified_numerics/lean_pinned.py)")),
        rec("P2SS-X-0003", "X", "numeric",
            "Must-fail files (rc 1): ControlsReject.lean has exactly 7 errors, CalcKReject.lean 2, CalcControlsReject.lean 2; every error line is mapped to one planted claim (rej_pi_shift, rej_ln2_199, rej_pair, rej_gmf_121, rej_erdrop_x2, rej_det, rej_G_eight_to_four; rej_S0_ulp, rej_F0_ulp; rej_calcK_er12, rej_calcLam_evipp12) and there is no other error. 10 are 'decide proved that the proposition is false'; rej_pi_shift is 'decide failed ... did not reduce' (its falsity is proved by the honest control ctl_pi_shift_false). A decide rejection is an observation of the failing run, not a kernel-checked negation; the negations are the A-0013 rows.",
            ["P2SS-A-0013"], num([DATA / "reject_map.json", DATA / "compile_ControlsReject.json", DATA / "compile_CalcKReject.json", DATA / "compile_CalcControlsReject.json"],
                                 "lean_pinned.py compile; gen_inputs.py error-to-theorem mapping", all_mapped=rej["all_mapped"])),
        rec("P2SS-X-0004", "X", "numeric",
            "LeanFlow decide_kernel on the 12 assertions: exact endpoints -> status ok, code verified, tier A, no axioms; planted copy (gmin - factor >= 1.21e-5 instead of 1.20e-5) -> rejected, false-statement, failing exactly cert_5, whose theorem then depends on sorryAx. The planted-run observation is a decide rejection, not a negation proof.",
            ["P2SS-A-0016"], num([DATA / "leanflow_result_exact.json", DATA / "leanflow_result_planted.json", DATA / "leanflow_claim_exact.json", DATA / "leanflow_claim_planted.json"],
                                 "LeanFlow certify() with decide_kernel, commit 06084ef5c40057c66c476feba18ea3da8fb150ba", planted_failed=lfp["failed"])),
        rec("P2SS-X-0005", "X", "numeric",
            "LeanFlow test suite at commit 06084ef5c40057c66c476feba18ea3da8fb150ba, rerun at the paper stage read-only (python -I -B -m pytest, no cache): 94 passed in 23.84 s (88 before the decide_kernel commit).",
            [], num([DATA / "leanflow_pytest.txt"], "AutoevolveAI .venv python -I -B -m pytest -p no:cacheprovider --rootdir LeanFlow worktree")),
        rec("P2SS-X-0006", "X", "numeric",
            "Measured cost of the remaining stages at level L1: process time of the ported files (calcK chunk files S0-3, F0-7: %s s; with CalcK.lean and CalcKCore.lean %s s; calcLam 20 chunk files %s s, with CalcLam.lean and CalcLamCore.lean %s s); rate %d ops/s lower bound (1,682,203 IV mul+inv of calcK+calcLam over all those files), %d ops/s upper bound (kernel benchmark); projection %d-%s core-hours (counts x measured rates); measured at machine load average 12-16, so ranges." % (
                f"{nums['t_calck_chunks']:,.1f}", f"{nums['t_calck_all']:,.1f}", f"{nums['t_calclam_chunks']:,.1f}", f"{nums['t_calclam_all']:,.1f}",
                round(nums["rate_low"]), nums["rate_hi"], round(nums["tot_lo"]), f"{nums['tot_hi']:,.0f}"),
            ["P2SS-A-0004", "P2SS-A-0005"], num([DATA / "cost_numbers.json", DATA / "bench_results.json", DATA / "bench_calck_trial.json", DATA / "result.json"], "gen_inputs.py over the compile logs; bench/BenchIV*.lean")),
        rec("P2SS-X-0007", "X", "numeric",
            "Tiling of the chunk ranges in Chain.lean (script over the statement text): chunkS 97 chunks cover [0,3103), chunkF 194 chunks cover [0,1552), chunkEacc 300 and chunkFacc 300 chunks each cover [0,45000), contiguous from 0 with no gap or overlap. Lean does not check this.",
            ["P2SS-A-0004", "P2SS-A-0005"], num([DATA / "tiling_check.json", LEAN / "Chain.lean"], "gen_inputs.py regular expressions over Chain.lean")),
        rec("P2SS-X-0008", "X", "numeric",
            "String search of the pinned Mathlib (d13f23b7): TrapezoidalRule.lean and Elliptic/Weierstrass.lean exist; the word 'midpoint' occurs in MeasureTheory/Integral only in TrapezoidalRule.lean (a docstring naming the single-trapezoid formula); 'voronoi' occurs once in Mathlib (a docstring of GeometryOfNumbers.lean); no file mentions a torus Green function. A string search is not a proof of absence.",
            ["P2SS-A-0010"], num([DATA / "mathlib_grep.json"], "mathlib_grep.py (Python string search)")),
        rec("P2SS-X-0009", "X", "numeric",
            "Observation of the axiom gate on the planted cheats (Controls.lean): ctl_sorry_pi 'proves' the shifted-pi claim with sorry and ctl_axiom_pi with a planted axiom; both files compile with rc 0, and #print axioms reports sorryAx, respectively ProgSandierSerfaty.Cert.Controls.ctl_cheat. Both are OUTSIDE the allowlist, which is what the gate must report. This is a control observation, not a Tier A theorem (re-filed from Tier A after the audit); no genuine theorem imports Controls.lean except the must-fail file ControlsReject.lean.",
            ["P2SS-A-0013"], num([DATA / "compile_Controls.json"], "lean_pinned.py compile of Controls.lean and its #print axioms lines")),
        rec("P2SS-X-0010", "X", "numeric",
            "Consistency of the table premises (auditor's script check_windows, reported in AUDIT.md section 2): all 891 windows (97 + 194 + 300 + 300) with 9,673 node literals and 8,782 cell literals equal entries of dump/dump.txt, each window a contiguous run of table indices with its cells exactly those between its nodes; the scalar copies equal the dump. Lean does not check this. A 1-ulp shift of every node f lower endpoint is absorbed by the outward rounding of h*G and accepted by the chunk theorem (auditor's plant), so stage-output bit equality alone would not detect it.",
            ["P2SS-A-0004", "P2SS-A-0005"], num([PAPER / "AUDIT.md", A1 / "STATEMENT_LOCK.json"], "independent AI auditor's scripts (scratch, not saved in the repository); numbers as reported in AUDIT.md")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    tiers = {t: sum(1 for c in claims if c["tier"] == t) for t in "ALCX"}
    print(f"claims {len(claims)} {tiers}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
