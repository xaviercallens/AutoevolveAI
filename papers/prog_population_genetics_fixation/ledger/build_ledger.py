"""Build the Elenchus claim ledger for the P7 preprint (papers/prog_population_genetics_fixation).

Modelled on papers/ar_dipolar_exciton/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim primary-source excerpts
(Tier L, from sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence   (see run_gate.py)
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
P7 = W / "results/programmes/2026-10-25/P7"
PS = P7 / "paper_stage"
LEAN = W / "formal_cert/Programmes/PopGen"
AR = W / "formal_cert/Autoresearch"
DATA = PAPER / "data"
GEN = PAPER / "gen"
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p7/crates/qf-popgen")
RUSTY_SHA = "cda9a9057ec16820f2e16b560cc0e63cf7eb05b9"
RUSTY_PARENT = "2b716c58fc7175798ad54dd9363938a3df37d9b0"  # the commit the independent audit examined
RS = P7 / "revision_stage"
AS = P7 / "audit_stage"  # copy of the independent auditor's transcripts (its scratch tree is /home/callensxavier_gmail_com/programmes-2026-10-25/P7/audit/)
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, pinned openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (only Mathlib is used by the P7 modules)"
H11_STATUS = ("imports Autoresearch.PopGenWrightFisher (H11, sha256 9cac6b9d5d0c76be771d8b004777699c539ea384741f7483f362de5884a4e530, unchanged), "
              "which a separate AI verifier recompiled with verdict ACCEPT_WITH_CORRECTIONS (results/autoresearch/2026-10-25/H11/verification.md); no human audit")
PRODUCER = ("producer-side compile by a Claude Opus 5.5 subagent (WORK1/WORK2); recompiled at the paper stage by the same AI pipeline "
            "(results/programmes/2026-10-25/P7/paper_stage/, rc 0, identical axiom lines); then recompiled FROM SOURCE by an independent AI auditor in its own "
            "olean directory with its own axiom audit and planted controls (AUDIT.md, ACCEPT_WITH_CORRECTIONS; transcripts in results/programmes/2026-10-25/P7/audit_stage/out/). "
            "The auditor is an AI of the same model family as the producer; NO human audit")
AUDIT_OUT = {"Absorption": "build_Absorption", "WrightFisherFixation": "build_WrightFisherFixation", "MoranModel": "build_MoranModel",
             "MoranFixation": "build_MoranFixation", "Price": "build_Price", "PopGenProgImportAll": "compile_PopGenProgImportAll",
             "PriceImportAll": "compile_PriceImportAll", "PopGenProgControls": "compile_PopGenProgControls", "PriceControls": "compile_PriceControls",
             "FixationDataCert": "compile_FixationDataCert", "FixationDataCertControls": "compile_FixationDataCertControls"}


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


def out_of(p: Path) -> str:
    return json.loads(p.read_text())["output"].replace("\n ", " ")


def axiom_lines(spec: dict[str, Path]) -> list[str]:
    """spec maps a fully qualified declaration name to the compile JSON that prints it."""
    res = []
    for name, jf in spec.items():
        lines = [l.strip() for l in out_of(jf).split("\n") if f"'{name}'" in l]
        if len(lines) != 1:
            raise SystemExit(f"axiom line for {name} not unique in {jf}: {lines}")
        res.append(lines[0])
    return res


def recompile_of(src_json: Path) -> Path:
    """The paper-stage recompile JSON that corresponds to a producer compile JSON."""
    m = {"compile_Absorption.json": "Absorption", "compile_WrightFisherFixation.json": "WrightFisherFixation",
         "compile_MoranModel.json": "MoranModel", "compile_MoranFixation.json": "MoranFixation", "compile_Price.json": "Price",
         "compile_import_all.json": "PopGenProgImportAll", "compile_price_import_all.json": "PriceImportAll",
         "compile_controls.json": "PopGenProgControls", "compile_price_controls.json": "PriceControls",
         "compile_FixationDataCert.json": "FixationDataCert", "compile_FixationDataCertControls.json": "FixationDataCertControls"}
    return PS / f"recompile_{m[src_json.name]}.json"


def audit_of(src_json: Path) -> Path:
    """The independent auditor's transcript that corresponds to a producer compile JSON."""
    return AS / "out" / (AUDIT_OUT[recompile_of(src_json).stem.removeprefix("recompile_")] + ".json")


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(spec: dict[str, Path], srcs: list[Path], status: str) -> dict:
    jfs = sorted(set(spec.values()))
    lines = axiom_lines(spec)
    # the paper-stage recompile must print identical lines
    rlines = axiom_lines({n: recompile_of(j) for n, j in spec.items()})
    if rlines != lines:
        raise SystemExit(f"paper-stage recompile differs from producer transcript for {list(spec)}")
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines,
            "allowlist": ["propext", "Classical.choice", "Quot.sound"],
            "compile_transcripts": [file_ref(j) for j in jfs],
            "paper_stage_recompile_transcripts": [file_ref(recompile_of(j)) for j in jfs],
            "independent_ai_audit_transcripts": [file_ref(audit_of(j)) for j in jfs],
            "independent_ai_audit_note": ("the auditor recompiled the pre-revision text of FixationDataCert.lean (sha256 79ced614...); only a doc comment changed since, "
                                          "recompiled by the revising agent (same pipeline)" if any("FixationDataCert" in str(j) for j in jfs) else "audited text identical to the hashed source"),
            "sources": [file_ref(p) for p in srcs], "status": status,
            "statement_adequacy": "not audited by a human"}


def cite(keys: list[str], **kw: object) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"), **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": f"rusty-SUNDIALS crates/qf-popgen (CVODE BDF) at {RUSTY_SHA} on branch physics/p7-fixation-2026-10-25 (base 7630f7e = origin/main, not pushed), plus numpy/scipy/mpmath scripts",
            "files": [file_ref(p) for p in files], **kw}


def arg(text: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, **kw}


def main() -> int:
    for old in EV.glob("*.json"):  # rebuild the blob store from scratch so no stale blob survives
        old.unlink()
    cA, cW, cM, cMF = (P7 / f"compile_{n}.json" for n in ("Absorption", "WrightFisherFixation", "MoranModel", "MoranFixation"))
    cP, cI, cPI = P7 / "compile_Price.json", P7 / "compile_import_all.json", P7 / "compile_price_import_all.json"
    cCtl, cPCtl = P7 / "compile_controls.json", P7 / "compile_price_controls.json"
    cDC, cDCC = P7 / "compile_FixationDataCert.json", P7 / "compile_FixationDataCertControls.json"
    N = "ProgPopGen."
    PN = "ProgPopGen.Price."
    srcA, srcWF, srcMM, srcMF = LEAN / "Absorption.lean", LEAN / "WrightFisherFixation.lean", LEAN / "MoranModel.lean", LEAN / "MoranFixation.lean"
    srcP = LEAN / "Price.lean"
    claims = [
        rec("PG-A-0001", "A", "lean_axioms",
            "ProgPopGen.fixation_limit and harmonic_unique_of_var (Absorption.lean), with kPow_harmonic, second_moment, interiorMass_tendsto_zero, absorption_tendsto, mass_split, kPow_last_mono: for a stochastic kernel P on Fin (N+1) (non-negative entries, unit row sums) with 0 and N absorbing, 0 < N, and h interior-harmonic with h 0 = 0, h N = 1 and positive one-step variance sum_j P(k,j)(h j - h k)^2 at every interior k, the n-step kernel kPow P n (left Chapman-Kolmogorov recursion) satisfies kPow P n i N -> h i and kPow P n i 0 -> 1 - h i; every interior-harmonic g with the same boundary values equals h; kPow P n i N is non-decreasing in n. The statement concerns the matrix power kPow, not a path measure.",
            [], lean_ev({N + n: cA for n in ["kPow_harmonic", "second_moment", "interiorMass_tendsto_zero", "absorption_tendsto", "mass_split",
                                             "kPow_last_mono", "fixation_limit", "harmonic_unique_of_var"]}, [srcA], PRODUCER)),
        rec("PG-A-0002", "A", "lean_axioms",
            "ProgPopGen.wright_fisher_fixation_limit (WrightFisherFixation.lean), with wf_absorbing, wf_var_pos, wright_fisher_fixation_mono: for 0 < N and the neutral Wright-Fisher kernel wfP N (H11's kernel C(N,j)(i/N)^j(1-i/N)^(N-j), unchanged), kPow (wfP N) n i N -> i/N and kPow (wfP N) n i 0 -> 1 - i/N; kPow (wfP N) n i N is non-decreasing in n. Closes the gap H11 recorded as 'not formalised'.",
            ["PG-A-0001"], lean_ev({N + n: cW for n in ["wf_absorbing", "wf_var_pos", "wright_fisher_fixation_limit", "wright_fisher_fixation_mono"]},
                                    [srcWF, AR / "PopGenWrightFisher.lean"], PRODUCER + "; " + H11_STATUS)),
        rec("PG-A-0003", "A", "lean_axioms",
            "Moran model, Nat-indexed lemmas (MoranModel.lean): bdP_sum (first-step expectation of a birth-death kernel), moranUp_eq (p_i = r q_i), moran_stay_nonneg, moranFix_harmonic_nat (p_i h(i+1) + q_i h(i-1) + (1 - p_i - q_i) h(i) = h(i) for every i > 0, h = moranFix), moran_var_pos_nat (positive one-step variance at interior i), moranFix_closed (r != 1: moranFix N r i = (1 - r^-i)/(1 - r^-N)), moranFix_neutral (moranFix N 1 i = i/N), moranFix_tendsto_one and moran_closed_tendsto_neutral ((1 - r^-i)/(1 - r^-N) -> i/N as r -> 1 within r != 1). Definitions: moranUp N r i = r i/(r i + N - i) * ((N - i)/N), moranDown N r i = ((N - i)/(r i + N - i)) * (i/N), moranFix N r i = S_i/S_N with S_n = sum_{k<n} r^-k, all in real arithmetic.",
            [], lean_ev({N + n: cM for n in ["bdP_sum", "moranUp_eq", "moran_stay_nonneg", "moranFix_harmonic_nat", "moran_var_pos_nat", "moranFix_closed",
                                             "moranFix_neutral", "moranFix_tendsto_one", "moran_closed_tendsto_neutral"]}, [srcMM], PRODUCER)),
        rec("PG-A-0004", "A", "lean_axioms",
            "Moran chain theorems (MoranFixation.lean): moran_absorbing, moran_interiorHarmonic, moran_var_pos, and for 0 < N, 0 < r: moran_fixation_limit (kPow (moranP N r) n i N -> moranFix N r i and kPow (moranP N r) n i 0 -> 1 - moranFix N r i), moran_fixation_limit_closed (r != 1: limit (1 - r^-i)/(1 - r^-N)), moran_fixation_limit_neutral (r = 1: limit i/N), moran_fixation_unique (every interior-harmonic g with g 0 = 0, g N = 1 equals moranFix N r).",
            ["PG-A-0001", "PG-A-0003"], lean_ev({N + n: cMF for n in ["moran_absorbing", "moran_interiorHarmonic", "moran_var_pos", "moran_fixation_limit",
                                                                       "moran_fixation_limit_closed", "moran_fixation_limit_neutral", "moran_fixation_unique"]},
                                                 [srcMF, srcMM, srcA], PRODUCER)),
        rec("PG-A-0005", "A", "lean_axioms",
            "ProgPopGen.Price.price_equation (Price.lean), over an arbitrary field K and a Finset of types: if sum n != 0 and sum n w != 0 then wmean n w * (zbarNext n w z' - wmean n z) = wcov n w z + wmean n (fun i => w i * (z' i - z i)), where zbarNext = (sum n w z')/(sum n w) is the offspring-generation mean (the modelling assumption). Also wcov_eq_moment (Cov = E(fg) - E f E g), wmean_ne_zero, and price_equation_pos over R under s.Nonempty, n i > 0, w i > 0.",
            [], lean_ev({PN + n: cP for n in ["price_equation", "wcov_eq_moment", "wmean_ne_zero", "price_equation_pos"]}, [srcP], PRODUCER)),
        rec("PG-A-0006", "A", "lean_axioms",
            "Haploid selection increment from Price (Price.lean): with z = w and no transmission bias z' = w, fisher_haploid (wbar (wbar' - wbar) = Var_n(w)), fisher_haploid_div (wbar' - wbar = Var_n(w)/wbar), wvar_nonneg, fisher_haploid_nondecreasing (n >= 0, sum n > 0, sum n w > 0 implies wbar <= wbar') and fisher_haploid_pos (R, s nonempty, n i > 0, w i > 0). Scope: haploid/asexual types with constant type fitnesses; NOT Fisher's theorem in the partial-change / additive-genetic-variance reading and NOT the diploid case.",
            ["PG-A-0005"], lean_ev({PN + n: cP for n in ["fisher_haploid", "fisher_haploid_div", "wvar_nonneg", "fisher_haploid_nondecreasing", "fisher_haploid_pos"]},
                                    [srcP], PRODUCER)),
        rec("PG-A-0007", "A", "lean_axioms",
            "Crosswalk (Price.lean, namespace ProgPopGen.Price.Alix): meanFit and selectP copied verbatim from SocrateAI-Scientific-Genetic formal/ANSE/AlixPopulationGenetics.lean over Q; aurelia_mean_fitness_increment (derived from the multi-type fisher_haploid_div at Fin 2, n = ![p, 1-p]) and kal_increment_is_variance (the wvar definition at Fin 2) restate two of that file's three H12 theorems with identical statement text. The match is textual; no Lean term links ProgPopGen.Price.Alix to ANSE.Alix.",
            ["PG-A-0006"], lean_ev({PN + "Alix." + n: cP for n in ["wmean_two", "wbarNext_two", "wvar_two", "aurelia_mean_fitness_increment", "kal_increment_is_variance"]},
                                    [srcP], PRODUCER)),
        rec("PG-A-0008", "A", "lean_axioms",
            "Negative controls, kernel-checked: ctl_neg_identity_no_absorption (Absorption.lean: the identity kernel on {0,1,2} is stochastic and absorbing, j/2 is interior-harmonic, yet kPow n 1 2 = 0 for all n, so it does not tend to 1/2 - the positive-variance hypothesis of fixation_limit cannot be dropped); ctl_neg_flipped_value (flipped formula (1 - r^i)/(1 - r^N) gives 1/7, not 4/7, at N = 3, r = 2, i = 1), ctl_neg_flipped_not_harmonic, ctl_neg_neutral_not_harmonic (MoranModel.lean); ctl_neg_wrong_limits (MoranFixation.lean: for N = 3, r = 2, kPow (moranP 3 2) n 1 3 tends neither to 1/3 nor to 1/7).",
            ["PG-A-0001", "PG-A-0004"], lean_ev({N + "ctl_neg_identity_no_absorption": cA, N + "ctl_neg_flipped_value": cM, N + "ctl_neg_flipped_not_harmonic": cM,
                                                  N + "ctl_neg_neutral_not_harmonic": cM, N + "ctl_neg_wrong_limits": cMF}, [srcA, srcMM, srcMF], PRODUCER)),
        rec("PG-A-0009", "A", "lean_axioms",
            "Positive controls, kernel-checked (each evaluated directly, not through the limit theorems): ctl_pos_wf_two_steps (kPow (wfP 2) 2 1 2 = 3/8), ctl_pos_moran_rates (moranUp 2 2 1 = 1/3, moranDown 2 2 1 = 1/6), ctl_pos_moranFix_N2 (2/3), ctl_pos_moranFix_N3 (moranFix 3 2 1 = 4/7, moranFix 3 2 2 = 6/7, and the first-step equation holds with these numbers).",
            [], lean_ev({N + "ctl_pos_wf_two_steps": cW, N + "ctl_pos_moran_rates": cM, N + "ctl_pos_moranFix_N2": cM, N + "ctl_pos_moranFix_N3": cM},
                        [srcWF, srcMM], PRODUCER)),
        rec("PG-A-0010", "A", "lean_axioms",
            "Price controls, kernel-checked (Price.lean): ctl_pos_three_types (n = (1,2,3), w = (1,2,4), z = (0,1,3), z' = (1,1,2): both sides of the Price equation evaluate to -13/36); ctl_neg_transmission_bias (n = (1,1), w = z = (1,2), z' = (1,1): delta wbar = -1/2 but Var/wbar = 1/6, while Price still holds, -3/4 = -3/4); ctl_neg_missing_wbar (delta wbar = 1/6 but Var = 1/4: the 1/wbar factor cannot be dropped); nonvacuous_pos.",
            [], lean_ev({PN + n: cP for n in ["ctl_pos_three_types", "ctl_neg_transmission_bias", "ctl_neg_missing_wbar", "nonvacuous_pos"]}, [srcP], PRODUCER)),
        rec("PG-A-0011", "A", "lean_axioms",
            "Non-vacuity and import-together (PopGenProgImportAll.lean, PriceImportAll.lean): AbsorbingChain (moranP 3 2) and AbsorbingChain (wfP 3) hold; instance_wf_N3 (kPow (wfP 3) n 1 3 -> 1/3) and instance_moran_N10 (r = 3/2: kPow (moranP 10 (3/2)) n 1 10 -> (1 - (2/3)^1)/(1 - (2/3)^10)); instance_four_types (the monotonicity theorem for n = (1,1,1,1), w = (1,2,3,4)); the H11, H12 and all P7 modules import together without name clashes.",
            ["PG-A-0001", "PG-A-0005"], lean_ev({"ProgPopGenCheck." + n: cI for n in ["nonvacuous_moran_chain", "nonvacuous_wf_chain", "instance_wf_N3", "instance_moran_N10"]}
                                                | {"ProgPopGenPriceCheck.instance_four_types": cPI}, [LEAN / "PopGenProgImportAll.lean", LEAN / "PriceImportAll.lean"], PRODUCER)),
        rec("PG-A-0012", "A", "lean_axioms",
            "Planted controls for the fixation and Price modules (PopGenProgControls.lean, PriceControls.lean; never imported) are caught by #print axioms: ProgPopGenControls.ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ProgPopGenControls.ctl_cheat (they claim the wrong limits 1/7 and 1/3 for the Moran chain at N = 3, r = 2); ProgPopGenPriceControls.ctl_sorry and ctl_axiom (false Price statements) likewise. Both files compile with rc 0, so exit status is not the gate.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines({"ProgPopGenControls.ctl_sorry": cCtl, "ProgPopGenControls.ctl_axiom": cCtl,
                                              "ProgPopGenPriceControls.ctl_sorry": cPCtl, "ProgPopGenPriceControls.ctl_axiom": cPCtl}),
                 "raw_output": [json.loads(cCtl.read_text())["output"], json.loads(cPCtl.read_text())["output"]],
                 "rc": [json.loads(cCtl.read_text())["rc"], json.loads(cPCtl.read_text())["rc"]],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "all four planted controls OUTSIDE the allowlist",
                 "sources": [file_ref(LEAN / "PopGenProgControls.lean"), file_ref(LEAN / "PriceControls.lean"), file_ref(cCtl), file_ref(cPCtl)],
                 "paper_stage_recompile_transcripts": [file_ref(recompile_of(cCtl)), file_ref(recompile_of(cPCtl))],
                 "independent_ai_audit_transcripts": [file_ref(audit_of(cCtl)), file_ref(audit_of(cPCtl)), file_ref(AS / "out/audit_AuditPlanted.json"),
                                                      file_ref(AS / "out/audit_AuditMutation.json")],
                 "statement_adequacy": "control rows; not audited by a human"}),
        rec("PG-A-0013", "A", "lean_axioms",
            "Arithmetic data certificates (FixationDataCert.lean): for the decimal literals L printed by the CVODE run, |L - moranFix N r i| < 1e-11 for (N, r, i) = (2, 2, 1), (3, 2, 1), (3, 2, 2), (10, 3/2, 1), (10, 3/2, 5) and < 1e-12 for (10, 1, 3) (cert_*); negative control ctl_neg_wrong_literal: |0.1 - moranFix 10 (3/2) 1| < 1e-3 is false. These are inequalities between decimal literals and exact rationals; they do not certify CVODE and are not statements about a Markov chain.",
            ["PG-A-0003"], lean_ev({"ProgPopGenCert." + n: cDC for n in ["cert_N2_r2_i1", "cert_N3_r2_i1", "cert_N3_r2_i2", "cert_N10_r1p5_i1", "cert_N10_r1p5_i5",
                                                                      "cert_N10_neutral_i3", "ctl_neg_wrong_literal"]}, [LEAN / "FixationDataCert.lean", srcMM],
                                    "paper-stage module (written after the producer stages, by the paper-stage agent); revised once after the audit: only a doc comment changed (pointer to FixationDataCertControls.lean), "
                                    "sha256 79ced614... -> 87dea63c..., recompiled rc 0 with identical axiom lines by the revising agent; " + PRODUCER)),
        rec("PG-A-0014", "A", "lean_axioms",
            "Planted controls for the data-certificate module (FixationDataCertControls.lean, never imported): ProgPopGenCertControls.ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ctl_cheat; both claim the false bound |0.1 - moranFix 10 (3/2) 1| < 1e-11; the file compiles with rc 0.",
            ["PG-A-0013"], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                            "axiom_output": axiom_lines({"ProgPopGenCertControls.ctl_sorry": cDCC, "ProgPopGenCertControls.ctl_axiom": cDCC}),
                            "raw_output": json.loads(cDCC.read_text())["output"], "rc": json.loads(cDCC.read_text())["rc"],
                            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "both controls OUTSIDE the allowlist",
                            "sources": [file_ref(LEAN / "FixationDataCertControls.lean"), file_ref(cDCC)],
                            "paper_stage_recompile_transcripts": [file_ref(recompile_of(cDCC))],
                            "independent_ai_audit_transcripts": [file_ref(audit_of(cDCC))],
                            "statement_adequacy": "control rows; not audited by a human"}),
        rec("PG-L-0001", "L", "citation",
            "Keller and Ugurlu (arXiv:2403.12598v2), eq. (3), p. 2: the classic Moran process on {0,...,n} with absorbing 0 and n has up/down probabilities p+(j) = r/(1+(r-1)j/n) (j/n)(n-j)/n and p-(j) = 1/(1+(r-1)j/n) ((n-j)/n)(j/n), the individual to be replaced being chosen uniformly at random. These are the rates the Lean definitions moranUp and moranDown are checked against (algebraic identity by hand, PG-C-0004).",
            [], cite(["ku_rates", "ku_typos"])),
        rec("PG-L-0002", "L", "citation",
            "Keller and Ugurlu (arXiv:2403.12598v2), eq. (4), p. 4 and Section 1.1.2, p. 3: the Moran fixation probabilities are rho_i = i/n for r = 1 and (1 - 1/r^i)/(1 - 1/r^n) for r != 1; they are derived there by optional stopping applied to the martingale r^(-M_k) (h(j) = r^(-j) is harmonic on the transient states). Theorem 2.1 on p. 7 prints a typo in the denominator (missing the exponent n); the optional-stopping line on p. 3 prints r^i, r^M0, r^MT, r^0, r^n where r^-i, r^-M0, r^-MT, r^0, r^-n are meant (sign slip in the source; not copied). Moran (1958) is cited as [Mor58] on p. 18 and was not read.",
            [], cite(["ku_fix", "ku_typos", "ku_moran58"])),
        rec("PG-L-0003", "L", "citation",
            "Marion (arXiv:2506.18616v5): the Ionescu-Tulcea construction, i.e. a trajectory measure of a Markov chain (partialTraj, traj : Kernel (Pi i : Iic a, X i) (Pi n, X n), pp. 9 and 12), is described as integrated into Mathlib (p. 1); the paper does not treat hitting or absorption probabilities. That ProbabilityTheory.Kernel.traj is present in the PINNED Mathlib build is a separate repository fact, not a Tier L citation: it is declared in Mathlib/Probability/Kernel/IonescuTulcea/Traj.lean at line 518 (found by grep by the independent auditor). This is the available route for formalising the bridge PG-C-0001, which this paper does not take.",
            [], cite(["marion_markov"])),
        rec("PG-L-0004", "L", "citation",
            "LaGatta (arXiv:2202.10289v4): the discrete Price equation Delta(X-bar) = cov(X, U) + E[Delta_w(X) U] (1.6, p. 9); Fisher's theorem in Price's reading d_NS(U) = var(U) (1.8, p. 9); the aggregate form d_NS(W) = var(W)/W-bar (2.24, p. 18); the two-generation identity W'-bar - W-bar = var(W)/W-bar + E[Delta_w(W,W')W]/W-bar (2.27, p. 19), of which the Lean fisher_haploid_div is the case in which the environmental/transmission term vanishes. Price (1970) and Price (1972) are listed on p. 69 and were not read.",
            [], cite(["lagatta_price", "lagatta_agg", "lagatta_refs"])),
        rec("PG-L-0005", "L", "citation",
            "Price's (1972) reading of Fisher, as quoted by LaGatta (p. 4): the theorem concerns the change due to natural selection, not the total change. Baez (arXiv:2107.05610v3, p. 4): with constant fitness functions d f-bar/dt = Var(f); p. 1-2: the naive reading 'rate of change of mean fitness = variance' holds only under very restrictive conditions, and Ewens concluded that the theorem does not provide the substantial biological statement Fisher claimed.",
            [], cite(["lagatta_price72", "baez_const", "baez_ewens"])),
        rec("PG-C-0001", "C", "argument",
            "Bridge to probability (not formalised): kPow P n i N is by definition the n-step transition probability of the Markov chain with kernel P, i.e. P_i(X_n = N); since N is absorbing this equals P_i(T_N <= n) (consistent with the kernel-checked monotonicity kPow_last_mono), so its limit is the fixation probability P_i(T_N < infinity). No path space and no ProbabilityTheory.Kernel.traj measure is built in Lean. The Tier A statements are about matrix powers; the words 'fixation probability' attach to them only through this standard identification.",
            ["PG-A-0001", "PG-L-0003"], arg("kPow is defined by the Chapman-Kolmogorov recursion, which is the definition of the n-step law of a time-homogeneous chain; absorbing N makes {X_n = N} = {T_N <= n}.", paper_section="Bridge")),
        rec("PG-C-0002", "C", "argument",
            "Uniformisation link (not formalised): exp(t (P - I)) = sum_n Poisson(t; n) P^n, so the absorption mass pi_N(t) of the CVODE ODE d pi/dt = pi (P - I) is a Poisson mixture of the n-step probabilities kPow P n i N; because kPow P n i N is non-decreasing and bounded by 1 and converges to h(i) (PG-A-0001), the mixture converges to the same limit. The CVODE runs therefore test the same closed forms but not the Lean matrix powers themselves.",
            ["PG-A-0001"], arg("Poisson(t; n) = e^-t t^n/n!; a Poisson mixture of a bounded monotone convergent sequence converges to the same limit as t -> infinity.", paper_section="Numerics")),
        rec("PG-C-0003", "C", "argument",
            "Step-by-step human proof of the absorption limit and of the Moran formulas (martingale; second-moment accumulation; squeeze; uniqueness by uniqueness of limits; Wright-Fisher variance via the jump to 0; Moran first-step equation via p_i = r q_i and h(i+1) - h(i) = r^-i/S_N). Each step is paired with the Lean declaration of PG-A-0001..0004; the human text itself is not machine-checked and has had no human referee.",
            ["PG-A-0001", "PG-A-0002", "PG-A-0003", "PG-A-0004"], arg("See Section 'Step-by-step human demonstration' of the paper and results/programmes/2026-10-25/P7/FIXATION.md section 3.", file=file_ref(P7 / "FIXATION.md"))),
        rec("PG-C-0004", "C", "argument",
            "Definition fidelity of the Moran rates: moranUp N r i = r i/(r i + N - i) * ((N - i)/N) equals Keller-Ugurlu's p+(j) = r/(1 + (r-1)j/n) (j/n)(n-j)/n because r (j/n)/(1 + (r-1) j/n) = r j/(n + (r-1) j) = r j/(r j + n - j); likewise moranDown N r i equals p-(j). This is a hand computation; no Lean term compares the two forms.",
            ["PG-L-0001", "PG-A-0003"], arg("r (j/n) / (1 + (r-1)(j/n)) = r j / (n + (r-1) j) = r j / (r j + n - j), and 1/(1+(r-1)j/n) * (n-j)/n = (n-j)/(n + (r-1) j) = (n-j)/(r j + n - j).")),
        rec("PG-C-0005", "C", "argument",
            "Scope of the Price/Fisher results: the Lean identity is the exact Price equation for a finite population in which the offspring-generation mean trait is defined as sum n w z'/sum n w; the corollary delta wbar = Var_n(w)/wbar holds for haploid/asexual types with constant type fitnesses and no transmission bias. It is not Fisher's fundamental theorem in the Price (1972)/Ewens/Edwards partial-change reading with additive genetic variance, and not the diploid multi-allele case. The preregistered item fisher_general (prior 0.35) was NOT achieved.",
            ["PG-A-0006", "PG-L-0004", "PG-L-0005"], arg("Only the special case z = w, z' = w is proved; the general partial-change statement needs a regression (average-effect) decomposition that is not formalised.", prereg=file_ref(W / "results/programmes/2026-10-25/preregistration.json"))),
        rec("PG-C-0006", "C", "argument",
            "Novelty: none claimed. Absorption of finite chains, the Wright-Fisher value i/N, the Moran formula and the Price equation are classical. The literature search for prior proof-assistant formalisations was limited to a few alphaXiv queries (absence by search is not proof). The only items offered are the explicit, kernel-checked statements in the stated form (matrix-power limits, one general theorem covering both models, uniqueness by uniqueness of limits) and the fail-closed CVODE certificate.",
            ["PG-L-0002"], arg("No priority claim.", note_file=file_ref(P7 / "FIXATION.md"))),
        rec("PG-C-0007", "C", "argument",
            "Genetic-repo relation: a whole-repo search of the SocrateAI-Scientific-Genetic clone found no Price-equation or covariance-decomposition result ('price' appears only as unrelated English; 'covariance' only as phylogenetic tree covariance matrices); the crosswalk theorems (PG-A-0007) are textual restatements in a separate namespace, and Price.lean was compiled only under the AutoevolveAI pin, not inside the Genetic repo's own build (that clone has no lean-toolchain or lakefile at its root).",
            ["PG-A-0007"], arg("See GENETIC_CONTRIB_NOTE.md.", file=file_ref(P7 / "GENETIC_CONTRIB_NOTE.md"))),
        rec("PG-C-0008", "C", "argument",
            "Conditionality: the P7 Lean modules import only Mathlib and the earlier modules H11 and H12 (which themselves import only Mathlib); no result of the openai/math repository is used, so the Tier A claims here are not conditional on openai/math results. The pinned toolchain happens to be the openai/math checkout.",
            ["PG-A-0001"], arg("Imports of the claimed files: Mathlib.* and Autoresearch.PopGen{WrightFisher,Fisher} only.", sources=[file_ref(p) for p in [srcA, srcWF, srcMM, srcMF, srcP]])),
        rec("PG-X-0001", "X", "numeric",
            "CVODE absorption runs (rusty-SUNDIALS qf-popgen, BDF, rtol 1e-11, atol 1e-15, analytic linear Jacobian): 106 accepted runs (78 Moran with N = 2..30 and r in {0.8, 1, 1.2, 1.5, 2}; 28 Wright-Fisher with N = 10, 20), every start i = 1..N-1; the absorption mass at N agrees with the closed forms i/N or S_i/S_N to at most 3.1e-10, the interior mass at the stopping time is at most 6.3e-10, the largest mass drift |sum pi - 1| is 9.8e-14, and the smallest component pi_k(t) seen at any output of any accepted run is -4.6e-18 (the certificate requires >= -1e-12 for every component, added in commit cda9a90 after the audit; all other fields of results.jsonl are identical to the first version produced at 2b716c5 - compare_results.json).",
            ["PG-C-0002"], num([DATA / "results.jsonl", DATA / "summary.json", RUSTY / "src/lib.rs", RUSTY / "src/bin/fixation_ode.rs", RS / "compare_results.json",
                                RS / "results.v1_2b716c5.jsonl"])),
        rec("PG-X-0002", "X", "numeric",
            "Negative controls of the fail-closed certificate: 9 of 9 refused for the stated reason - exponent-flipped target and neutral i/N under selection (6 ValueMismatch at N = 10, r = 1.5, i = 1, 3, 7), the identity kernel (NotAbsorbed: valid absorbing kernel, no absorption flow), a horizon of t <= 4 (NotAbsorbed), and a corrupted row sum (InvalidKernel). No negative control was accepted. The identity-kernel row carries r = null (the first version of the file carried a meaningless r = 1.5). In addition, a unit-level negative control (cargo test, not a CVODE run) shows that the new componentwise check check_nonnegative refuses the state (0.5, -0.25, 0.25, 0.5), whose total mass is 1 and interior mass 0, together with a round-off-level positive control.",
            ["PG-X-0001"], num([DATA / "results.jsonl", DATA / "cargo_test.txt"])),
        rec("PG-X-0003", "X", "numeric",
            "Independent cross-check: kernels rebuilt in numpy (separate code from the Rust constructors) and exp(t_stop (P - I)) evaluated with scipy.linalg.expm; the CVODE absorption mass differs from it by at most 1.0e-13 over all 106 accepted runs.",
            ["PG-X-0001"], num([GEN / "independent_check.json", GEN / "gen_all.py"])),
        rec("PG-X-0004", "X", "numeric",
            "Provenance of the decimal literals in FixationDataCert.lean: they are the shortest round-trip decimal forms (Python repr) of the p_fix doubles that fixation_ode writes with 18 significant digits (e.g. JSONL text 6.66666666666660079e-1 gives the literal 0.6666666666666601), for (N, r, i) = (2, 2, 1), (3, 2, 1), (3, 2, 2), (10, 3/2, 1), (10, 3/2, 5), (10, 1, 3). Differences between the DECIMAL LITERAL as written in Lean and the exact rational (exact arithmetic): 6.57e-15, 9.55e-14, 7.79e-14, 6.49e-13, 8.46e-13, 2.30e-16. Differences between the float64 p_fix and the float64 nearest the exact value (the abs_err field of results.jsonl): 6.55e-15, 9.55e-14, 7.79e-14, 6.49e-13, 8.46e-13, 2.22e-16 (the (10,1,3) literal 0.29999999999999977 is 2.30e-16 below 3/10 as a decimal and 2.22e-16 below as a float64 difference). Both are far inside the Lean bounds (1e-11, and 1e-12 for the neutral case).",
            ["PG-X-0001"], num([DATA / "results.jsonl", LEAN / "FixationDataCert.lean", RS / "literals.json"])),
        rec("PG-X-0005", "X", "numeric",
            "WORK1 cross-check: exact rationals (WF N = 2: P^2(1,2) = 3/8; Moran N = 3, r = 2: [0, 4/7, 6/7, 1]; N = 10, r = 3/2: exact first-step solve equals the closed form and not the flipped one) and mpmath 60-digit matrix powers P^4096 at N = 10 (Wright-Fisher error <= 2e-61; Moran r = 3/2 error <= 3.7e-50; r = 4/5 errors <= 2.2e-41 and r = 1 errors at most 6.6062e-37 (rounds to 6.7e-37 upward) on the sampled i; the flipped formula is off by 0.33-0.67 and i/N by 0.24-0.42 at r = 3/2).",
            [], num([DATA / "numerics_fixation.json", P7 / "numerics_fixation.py"])),
        rec("PG-X-0006", "X", "numeric",
            "WORK2 cross-check of the Price results: exact Fraction values reproduce all Lean control values (-13/36; -1/2 vs 1/6 with Price -3/4 = -3/4; 1/6 vs 1/4); 500/500 random exact instances (1-8 types) satisfy the Price identity and the haploid increment; the worst float64 residual is 1.42e-14.",
            [], num([DATA / "price_numerics.json", P7 / "price_numerics.py"])),
        rec("PG-X-0007", "X", "numeric",
            "Build hygiene of the rusty-SUNDIALS change (branch physics/p7-fixation-2026-10-25, commit cda9a90 (parent 2b716c58, which the audit examined: 6 tests passed there), base 7630f7e, not pushed): cargo test --release -p qf-popgen -- --test-threads=2: 8 passed, 0 failed (two new tests for the componentwise non-negativity check); cargo clippy --workspace --features experimental -- -D warnings: exit 0, no warnings or errors; cargo fmt --all --check: rc 0.",
            ["PG-X-0001"], num([DATA / "cargo_test.txt", DATA / "clippy_workspace.txt"])),
        rec("PG-X-0008", "X", "numeric",
            "Paper-stage recompile by the same AI pipeline of all 11 claimed or control Lean files (pinned Lean 4.34.1): every rc 0; sha256 values equal those recorded in FIXATION.md and PRICE.md; axiom lines identical to the producer transcripts (11, 5, 16, 8, 21, 6, 4, 2, 2, 7, 2 #print axioms lines). Same AI pipeline (the FixationDataCert row is the recompile of the revised file, sha256 87dea63c...; the pre-revision records are in revision_stage/). The independent recompile is PG-X-0009.",
            [], num([PS / "summary.json"] + sorted(PS.glob("recompile_*.json")))),
        rec("PG-X-0009", "X", "numeric",
            "Independent AI audit of this preprint (AUDIT.md, verdict ACCEPT_WITH_CORRECTIONS, no blocking issue; auditor: a separate Claude agent, same model family as the producer, NOT a human): every Lean module recompiled from source into the auditor's own olean directory (producer .olean_out excluded) with rc 0 and only allowlisted axioms for the claimed declarations (36 key declarations printed by the auditor's own file); the producer's planted controls and the auditor's own planted controls (sorry, planted axiom, sorry hidden in a lemma) caught by #print axioms; a mutation (4/7 -> 1/3) rejected by the kernel (rc 1); qf-popgen at 2b716c5 rebuilt and fixation_ode re-run with results.jsonl byte-identical to the first version; macros, tables and literals recomputed from data; hand proofs checked with sympy residual 0; four arXiv citations matched page by page and tools/citation_check.py accepted a real quote and refused a mutated one on the primary KU Theorem 3.1 text. It audited the pre-revision FixationDataCert.lean (doc comment later changed) and the Rust crate at 2b716c5 (componentwise check later added); the 14 Tier A audit fields stay null because no human has audited statement adequacy.",
            [], {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
                 "instrument": "independent AI auditor (Claude), Lean 4.34.1 + Mathlib d13f23b7 pinned toolchain, sympy, mpmath, exact Fractions, cargo 2b716c5; its scratch tree is /home/callensxavier_gmail_com/programmes-2026-10-25/P7/audit/, copied here to results/programmes/2026-10-25/P7/audit_stage/",
                 "files": [file_ref(PAPER / "AUDIT.md"), file_ref(AS / "audit_lean.log"), file_ref(AS / "audit_lean.py"), file_ref(AS / "audit_numbers.json"),
                           file_ref(AS / "audit_sympy.txt"), file_ref(AS / "gate_rerun.txt"), file_ref(AS / "check_evidence.py")]
                 + [file_ref(p) for p in sorted((AS / "out").glob("*.json"))] + [file_ref(p) for p in sorted((AS / "src").glob("*.lean"))]}),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
