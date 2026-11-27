"""Build the Elenchus claim ledger for the N4 preprint (papers/p3_isothermal_theorem).

Modelled on papers/prog_population_genetics_fixation/ledger/build_ledger.py, minus the independent-audit transcripts (N4 has none).
Every claim gets a content-addressed evidence blob (evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A),
verbatim primary-source excerpts (Tier L, sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py ; then run_gate.py
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
N4 = W / "results/proposal3/2026-10-26/N4"
PS = PAPER / "paper_stage"
LEAN = W / "formal_cert/Programmes/EvoGraph"
P7LEAN = W / "formal_cert/Programmes/PopGen"
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612 (pinned via scripts/certified_numerics/lean_pinned.py)"
BASE = "git commit 8ff5912 (formal_cert/Programmes/EvoGraph/ committed there)"
STATUS = ("producer-side compile by an AI agent (results/proposal3/2026-10-26/N4/compile_*.json, rc 0); recompiled at the paper stage by the same AI "
          "pipeline (papers/p3_isothermal_theorem/paper_stage/recompile_*.json, rc 0, identical axiom lines). then independently audited by an AI auditor (separate olean dir, own #print axioms, leanchecker replay rc 0 with forged-control rejection, independent exact numerics; ACCEPT_WITH_CORRECTIONS, papers/p3_isothermal_theorem/AUDIT.md); NO human audit")
JSONS = {"Transport": N4 / "compile_Transport.json", "BirthDeath": N4 / "compile_BirthDeath.json", "Examples": N4 / "compile_Examples.json",
         "ImportAll": N4 / "compile_ImportAll.json", "PlantedControls": N4 / "compile_PlantedControls.json"}
RECOMP = {k: PS / f"recompile_{k}.json" for k in JSONS}
ORDER = ["Transport", "BirthDeath", "Examples", "ImportAll", "PlantedControls"]


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


def find_line(name: str, table: dict[str, Path]) -> tuple[str, str]:
    """The unique '#print axioms' line for `name` in the first transcript (in ORDER) that has it."""
    for k in ORDER:
        lines = [l.strip() for l in out_of(table[k]).split("\n") if f"'{name}'" in l]
        if lines:
            if len(lines) != 1:
                raise SystemExit(f"{name} not unique in {table[k]}")
            return k, lines[0]
    raise SystemExit(f"no axiom line for {name}")


def lean_ev(names: list[str], srcs: list[Path]) -> dict:
    used: set[str] = set()
    lines: list[str] = []
    for n in names:
        k, l = find_line(n, JSONS)
        k2, l2 = find_line(n, RECOMP)
        if k2 != k or re.sub(r"\s+", " ", l) != re.sub(r"\s+", " ", l2):
            raise SystemExit(f"paper-stage recompile differs for {n}")
        used.add(k)
        lines.append(l)
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "base": BASE, "axiom_output": lines,
            "allowlist": ["propext", "Classical.choice", "Quot.sound"],
            "compile_transcripts": [file_ref(JSONS[k]) for k in ORDER if k in used],
            "paper_stage_recompile_transcripts": [file_ref(RECOMP[k]) for k in ORDER if k in used],
            "sources": [file_ref(p) for p in srcs], "status": STATUS,
            "note": "compile transcripts also contain Lean deprecation warnings (if_true/if_false); no errors",
            "statement_adequacy": "not audited by a human"}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def cite(keys: list[str], **kw: object) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"), **kw}


def arg(text: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    bd, tr, ex, pc, ia = (LEAN / f for f in ("BirthDeath.lean", "Transport.lean", "Examples.lean", "EvoGraphPlantedControls.lean", "EvoGraphImportAll.lean"))
    pabs, pmm = P7LEAN / "Absorption.lean", P7LEAN / "MoranModel.lean"
    E = "EvoGraph."
    claims = [
        rec("EG-A-0001", "A", "lean_axioms",
            "Transport of P7's absorption limit (Transport.lean): EvoGraph.two_absorbing_limit, for a stochastic kernel P on a finite type with absorbing bot != top, h harmonic off {bot,top}, h bot = 0, h top = 1 and positive one-step variance off {bot,top}: P^t(s,top) -> h s and P^t(s,bot) -> 1 - h s; obtained from ProgPopGen.fixation_limit by conjugating with an enumeration of the state type, nothing re-proved. Also sPow_top_mono: P^t(s,top) is non-decreasing in t.",
            [], lean_ev([E + n for n in ("two_absorbing_limit", "sPow_top_mono", "kPow_conj", "exists_equiv_fin")], [tr, pabs])),
        rec("EG-A-0002", "A", "lean_axioms",
            "Birth-death configuration chain (BirthDeath.lean): bd_absorbing (bdK mu W r is stochastic with absorbing empty set and univ for row-stochastic W, mu > 0, r > 0, 0 < n), up_eq (P+(S) = r cutOut(S)/F(S)), down_eq (P-(S) = cutIn(S)/F(S)), expect_eq (first-step expectation).",
            [], lean_ev([E + n for n in ("bd_absorbing", "up_eq", "down_eq", "expect_eq")], [bd, tr])),
        rec("EG-A-0003", "A", "lean_axioms",
            "Forward bias (BirthDeath.lean): for row-stochastic W and mu stationary (sum_i mu_i W_ij = mu_j), flow_balance (net flow of mu W across every set S is 0), cut_balance (cutOut S = cutIn S) and forward_bias: upP S = r * downP S for EVERY configuration S.",
            ["EG-A-0002"], lean_ev([E + n for n in ("flow_balance", "cut_balance", "forward_bias")], [bd])),
        rec("EG-A-0004", "A", "lean_axioms",
            "Harmonicity (BirthDeath.lean): moranFix_card_harmonic (for stationary mu, S -> moranFix n r |S| satisfies the first-step equation of the configuration chain at every non-empty S) and moranFix_card_var_pos (positive one-step variance at S whenever an edge i in S -> j not in S has mu_i W_ij > 0).",
            ["EG-A-0002", "EG-A-0003"], lean_ev([E + n for n in ("moranFix_card_harmonic", "moranFix_card_var_pos")], [bd, pmm])),
        rec("EG-A-0005", "A", "lean_axioms",
            "cutPositive_of_strongly_connected (BirthDeath.lean): if mu > 0 and the digraph {(a,b): W a b > 0} is strongly connected (TransGen), then every proper non-empty S has an edge leaving it with mu_i W_ij > 0. Only this direction is proved.",
            [], lean_ev([E + "cutPositive_of_strongly_connected"], [bd])),
        rec("EG-A-0006", "A", "lean_axioms",
            "stationary_fixation (BirthDeath.lean): 0 < n, 0 < r, mu > 0, W row-stochastic, mu W = mu, cut positivity => for every S, P^t(S,univ) -> moranFix n r |S| and P^t(S,empty) -> 1 - moranFix n r |S| (n-step kernel limits of the configuration chain).",
            ["EG-A-0001", "EG-A-0002", "EG-A-0003", "EG-A-0004", "EG-A-0005"], lean_ev([E + "stationary_fixation"], [bd, tr, pmm, pabs])),
        rec("EG-A-0007", "A", "lean_axioms",
            "Isothermal theorem for birth-death updating (BirthDeath.lean): isothermal_fixation (mu = 1, W doubly stochastic, strongly connected: P^t(S,univ) -> moranFix n r |S| for every S), isothermal_fixation_single (r != 1, single mutant at any node v: limit (1 - r^-1)/(1 - r^-n)), isothermal_fixation_neutral (r = 1: |S|/n), isothermal_fixation_uniform (uniformly placed single mutant), bd_fixation_mono (P^t(S,univ) non-decreasing in t).",
            ["EG-A-0006"], lean_ev([E + n for n in ("isothermal_fixation", "isothermal_fixation_single", "isothermal_fixation_neutral", "isothermal_fixation_uniform", "bd_fixation_mono")], [bd])),
        rec("EG-A-0008", "A", "lean_axioms",
            "Positive controls (Examples.lean): wellMixed_up / wellMixed_down (for W = J/n and every n, S: upP = moranUp n r |S| and downP = moranDown n r |S|, an exact lumping onto P7's Moran chain); wellMixed3_fixation (n = 3, r = 2: limit 4/7); starStationary_fixation (star n = 3 with stationary mu = (1/2,1/4,1/4): limit from the centre 4/7).",
            ["EG-A-0006", "EG-A-0007"], lean_ev([E + n for n in ("wellMixed_up", "wellMixed_down", "wellMixed3_fixation", "starStationary_fixation")], [ex])),
        rec("EG-A-0009", "A", "lean_axioms",
            "Negative controls, star graph n = 3 (centre 0, W_0j = 1/2, W_j0 = 1), r = 2, mu = 1 (Examples.lean): star_not_isothermal (centre column sum 2), star_bias (upP {0} = downP {0} = 1/2, ratio 1 != r), star_fixation_centre (5/12), star_fixation_leaf (2/3), star_fixation_uniform (7/12), star_ne_moran (5/12, 7/12 and 2/3 each differ from moranFix 3 2 1 = 4/7).",
            ["EG-A-0001"], lean_ev([E + n for n in ("star_not_isothermal", "star_bias", "star_fixation_centre", "star_fixation_leaf", "star_fixation_uniform", "star_ne_moran")], [ex])),
        rec("EG-A-0010", "A", "lean_axioms",
            "Negative controls (Examples.lean): cycle4_not_lumpable (isothermal 4-cycle W_{i,i+-1} = 1/2 without self-loops, r = 2, mu = 1: configurations {0,1} and {0,2} have the same number of mutants, upP = 1/3 resp. 2/3, yet upP = 2 downP at both) so the one-step probability of a count increase is not a function of the count; identity_no_fixation (W = I on 2 nodes is doubly stochastic but not strongly connected, P^t({0},univ) = 0 for all t, no convergence to moranFix 2 2 1).",
            ["EG-A-0003"], lean_ev([E + "cycle4_not_lumpable", E + "identity_no_fixation"], [ex])),
        {"schema_version": 1, "id": "EG-A-0011", "tier": "A", "kind": "lean_axioms", "depends_on": [], "audit": None,
         "statement": "Planted controls (EvoGraphPlantedControls.lean; imported by nothing) are CAUGHT by #print axioms: EvoGraphControls.ctl_sorry (false claim: star centre -> 4/7) reports sorryAx; ctl_axiom (false: uniform single mutant on the star -> 4/7) and ctl_axiom_lumpable (false: upP {0,1} = upP {0,2} on the 4-cycle) report the planted axiom EvoGraphControls.ctl_cheat. The file compiles with rc 0, so exit status is not the gate.",
         "evidence": blob({"kind": "lean_axioms", "toolchain": TOOLCHAIN, "base": BASE,
                           "axiom_output": [find_line("EvoGraphControls." + n, JSONS)[1] for n in ("ctl_sorry", "ctl_axiom", "ctl_axiom_lumpable")],
                           "raw_output": json.loads(JSONS["PlantedControls"].read_text())["output"], "rc": json.loads(JSONS["PlantedControls"].read_text())["rc"],
                           "recompile_axiom_output": [find_line("EvoGraphControls." + n, RECOMP)[1] for n in ("ctl_sorry", "ctl_axiom", "ctl_axiom_lumpable")],
                           "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected_violations": ["sorryAx", "EvoGraphControls.ctl_cheat"],
                           "compile_transcripts": [file_ref(JSONS["PlantedControls"])], "paper_stage_recompile_transcripts": [file_ref(RECOMP["PlantedControls"])],
                           "sources": [file_ref(pc)], "status": STATUS, "statement_adequacy": "not audited by a human"})},
        rec("EG-L-0001", "L", "citation",
            "Keller and Ugurlu (arXiv:2403.12598v2) CLAIM that the Lieberman-Hauert-Nowak (2005) proof projects the configuration chain onto the mutant count, treats it as a birth-and-death process, and that this projection need not be Markovian (abstract, p. 1; Section 1.2, p. 4; Section 2.2, p. 7), and that therefore 'the isothermal theorem remains unproven till today' (p. 4). This ledger records the claim as the authors' claim; it does not endorse 'unproven' (see EG-C-0005).",
            [], cite(["ku_abstract", "ku_gap"])),
        rec("EG-L-0002", "L", "citation",
            "Keller and Ugurlu (arXiv:2403.12598v2): Definition 2.1 (selection policy pi with pi W = pi), Theorem 3.1 (for every micSMP with stationary selection and every initial distribution on X_j the fixation probability is the Moran value), proved by the martingale r^{-M_k} and optional stopping (p. 9), Theorem 3.2 (p^-/p^+ is constant iff mu is the stationary vector, then 1/r; p. 10), and the equivalence 'isothermal iff bistochastic' (Section 2.3, p. 7).",
            [], cite(["ku_thm31", "ku_thm32", "ku_iso"])),
        rec("EG-L-0003", "L", "citation",
            "Pattni, Broom, Rychtar and Silvers (arXiv:1505.06021v1, 22 May 2015): Lemma 1 (Constant Forward Bias, Appendix A.2, p. 11): for processes whose transitions change at most one site and have forward and backward moves at every interior state, 'fixation probability equals the Moran value with ratio c' is equivalent to 'P+_S/P-_S = d for all S', with c = d; the proof of (b) => (a) removes holding, lumps the resulting jump chain onto |S| (Kemeny-Snell Thm 6.3.2) and solves the birth-death walk (p. 12). Proposition 2 (p. 6) and the remark on p. 7: for birth-death with fitness-proportional birth (BDB), W is rho-equivalent to the Moran process for all r iff f_R(W) is a circulation, i.e. 'the Isothermal theorem from [LHN05]' for right-stochastic matrices; the forward bias equals r when U = f_R(W) is doubly stochastic (p. 14). They assume strong connectivity and allow self-loops (p. 2, 5).",
            [], cite(["pattni_title", "pattni_lemma1", "pattni_prop2"])),
        rec("EG-L-0004", "L", "citation",
            "Bibliographic data for Lieberman, Hauert and Nowak (2005): E. Lieberman, C. Hauert, M. A. Nowak, 'Evolutionary dynamics on graphs', Nature 433(7023):312-316, January 2005, doi:10.1038/nature03204, as listed in the reference list of Keller and Ugurlu (p. 18) and in an IDEAS/RePEc record. The paper itself was NOT read by the authors of this preprint; everything said here about its argument is second-hand through EG-L-0001 and EG-L-0003. (Keller and Ugurlu's abstract names the venue 'Nature Communications'; their own reference list gives Nature.)",
            [], cite(["ku_ref", "lhn_repec"])),
        rec("EG-C-0001", "C", "argument",
            "PREREGISTRATION DEVIATION. The preregistered N4 statement (preregistration.json, 2026-10-26) reads: 'prove that if the graph is isothermal ... the number of mutants is a birth-death chain with the Moran ratio r, hence fixation probability (1 - r^-1)/(1 - r^-N) ...'. The clause 'the number of mutants is a birth-death chain' is false as a Markov-chain statement for the chain with holding: kernel-checked cycle4_not_lumpable shows the one-step increase probability is a function of the configuration and not of the count. The proved replacements are the per-configuration forward bias upP = r downP (forward_bias) and the harmonicity of moranFix n r |S| on configurations; the fixation conclusion is proved in full. Not claimed: that the count is Markov, in particular not claimed to be non-Markov from every initial law (cycle4_not_lumpable refutes strong lumpability only).",
            ["EG-A-0003", "EG-A-0007", "EG-A-0010", "EG-L-0001"], arg("See Section 'Preregistration deviation' of the paper; source: results/proposal3/2026-10-26/preregistration.json item N4 and N4/result.json verdict_vs_prereg.", file=file_ref(W / "results/proposal3/2026-10-26/preregistration.json"))),
        rec("EG-C-0002", "C", "argument",
            "Step-by-step human proof of the isothermal theorem (model; forward bias P+ = r P- per configuration from cut balance; harmonicity of S -> moranFix(|S|) by a telescoping first-step computation; absorption limit by transport of P7; strong connectivity implies cut positivity; why the count does not lump). Each step is paired with the Lean declaration of EG-A-0001..0007 and EG-A-0010; the human text itself is not machine-checked.",
            ["EG-A-0001", "EG-A-0002", "EG-A-0003", "EG-A-0004", "EG-A-0005", "EG-A-0006", "EG-A-0007", "EG-A-0010"],
            arg("Section 'Step-by-step human proof' of the paper; derived from BirthDeath.lean (docstring and proof structure).", file=file_ref(bd))),
        rec("EG-C-0003", "C", "argument",
            "On the isothermal 4-cycle (r = 2, no self-loops) the HOLDING-REMOVED jump chain does lump onto the count: P+/(P+ + P-) = (1/3)/(1/2) = 2/3 at {0,1} and (2/3)/1 = 2/3 at {0,2}, as Pattni et al.'s Lemma 1 requires; what fails to lump is the chain with holding (holding probability 1/2 at {0,1} and 0 at {0,2}). So cycle4_not_lumpable does not contradict the theorem or Pattni et al.'s route; it contradicts only the claim that the count of the lazy chain is Markov. Hand computation from upP, downP values in cycle4_not_lumpable, cutOut/cutIn/F.",
            ["EG-A-0010", "EG-L-0003"], arg("cutOut{0,1} = cutIn{0,1} = 1, cutOut{0,2} = cutIn{0,2} = 2 (each W entry 1/2), F = 2*2 + 2*1 = 6; P+ = 2*cutOut/6, P- = cutIn/6; matches numerics_evograph.json cycle4_up_down_two_mutants (1/3,1/6) and (2/3,1/3).")),
        rec("EG-C-0004", "C", "argument",
            "Bridge to probability (not formalised, as in P7): P^t(S,univ) is by definition the t-step transition probability of the configuration chain; since univ is absorbing it equals P(T_univ <= t) (consistent with the kernel-checked monotonicity bd_fixation_mono), and its limit is the fixation probability P(T_univ < infinity). No path space is built in Lean.",
            ["EG-A-0007"], arg("Standard identification of matrix powers with n-step laws; the monotone limit is the probability of ever reaching the absorbing state.")),
        rec("EG-C-0005", "C", "argument",
            "Relation to the literature (our reading; not machine-checked). (i) Keller and Ugurlu locate a gap in the projection argument and prove the theorem by a martingale (EG-L-0001, EG-L-0002); Pattni et al. (2015) give a proof through per-configuration forward bias and lumping of the jump chain (EG-L-0003). So a valid route to the theorem existed before 2024 and we do not endorse the phrase 'unproven' (the gap is in projecting the chain with holding; we did not read LHN 2005 and cannot say how it argued). (ii) The Lean proof uses the per-configuration forward-bias hypothesis (Pattni et al.'s condition (b)), but then proceeds by harmonicity of moranFix(|S|) on configurations and P7's absorption limit, which is closer in spirit to the Keller-Ugurlu martingale r^{-M_k} than to Pattni et al.'s lumping. (iii) stationary_fixation matches Keller-Ugurlu Theorem 3.1 in statement (selection weight a left eigenvector of W, fixation probability the Moran value) up to normalisation of mu; it is proved in Lean here, in the n-step-kernel sense of P7.",
            ["EG-L-0001", "EG-L-0002", "EG-L-0003", "EG-A-0003", "EG-A-0006"], arg("Comparison of the cited statements with the Lean statements; see the paper, Section 'Relation to the literature'.")),
        rec("EG-C-0006", "C", "argument",
            "Biological relevance (motivation only; every sentence is Tier C): the model is the standard evolutionary-graph-theory setting in which structure is a weighted replacement digraph and a graph is compared with the well-mixed Moran process (Pattni et al. p. 1-2); the theorem says that, for birth-death updating with fitness-proportional birth, balanced (doubly stochastic, strongly connected) replacement structure does not change the single-mutant fixation probability. Hence an amplifier or suppressor of selection under this updating must break the balance. The star control shows an unbalanced graph that differs from the Moran value at ONE fitness (r = 2, n = 3: 7/12 vs 4/7); one value of r does not establish that the star amplifies for all r. Tissue architecture is cited only as the usual motivation for studying structured populations; no tissue data enter this preprint and no biological prediction is made. Death-birth and other updatings, mutation, and time-dependent structure are not covered.",
            ["EG-A-0007", "EG-A-0009", "EG-L-0003"], arg("Interpretive statement; carries no Tier A content.")),
        rec("EG-C-0007", "C", "argument",
            "Novelty: none claimed for the mathematics (Lieberman-Hauert-Nowak 2005; Pattni et al. 2015; Keller-Ugurlu 2024). We are not aware of a prior machine-checked formalisation of the isothermal theorem, but no systematic search of Lean/Coq/Isabelle libraries or the proof-assistant literature was done; absence by search is not proof. Scope of the Lean statements: sufficiency only (isothermal => Moran); birth-death with fitness at birth only; row-stochastic W (general weights reduce to this through Pattni et al.'s map f_R, not formalised); limit of the n-step kernel (no path measure); exact star values for n = 3 only.",
            [], arg("Scope statement; see the paper, Section 'Scope and limitations'.")),
        rec("EG-C-0008", "C", "argument",
            "Dependencies: the N4 modules import only Mathlib and P7's Programmes.PopGen.Absorption and Programmes.PopGen.MoranModel (doi:10.5281/zenodo.23653850, unchanged, sha256 recorded); no result of openai/math is used. The P7 Tier A statements are used as they are; their own status (producer compile, same-pipeline recompile, independent AI audit ACCEPT_WITH_CORRECTIONS, no human audit) is stated in the P7 preprint.",
            ["EG-A-0001"], arg("Imports: Transport.lean imports Programmes.PopGen.Absorption; BirthDeath.lean imports Programmes.EvoGraph.Transport and Programmes.PopGen.MoranModel; Examples.lean imports BirthDeath.", sources=[file_ref(p) for p in (tr, bd, ex, pabs, pmm)])),
        rec("EG-C-0009", "C", "argument",
            "Review status: the Lean files were compiled by their producer and re-compiled at the paper stage by the same AI pipeline. An independent adversarial AI auditor (producer != verifier; not a human) recompiled the modules from source into its own olean directory, re-ran #print axioms, ran a leanchecker kernel replay (rc 0; a debug.skipKernelTC forgery control was rejected), recomputed the star and 4-cycle values with an independent exact-rational script and checked both cited sources: verdict ACCEPT_WITH_CORRECTIONS (papers/p3_isothermal_theorem/AUDIT.md; statement lock results/proposal3/2026-10-26/N4/STATEMENT_LOCK.json). There has been no human audit, so the ledger audit fields stay null. Every Tier A tag means 'kernel-checked, statement adequacy not audited by a human'.",
            [], arg("Statement of status; the audit fields of the ledger stay null.")),
        rec("EG-X-0001", "X", "numeric",
            "Independent exact-rational numerics (numerics_evograph.py, Fractions, Gaussian elimination on all 2^n configurations, r = 2, mu = 1 unless stated): W_H n = 3 (4/7) and n = 4 (8/15), the 4-cycle and a random rational doubly stochastic 4x4 matrix reproduce the Moran value from every single mutant; star n = 3 gives (5/12, 2/3, 2/3), mean 7/12 (matches the Lean values); star n = 4 gives (392/1265, 168/253, 168/253, 168/253), mean 728/1265 != 8/15 (numerics only, not kernel-checked); a random row-stochastic non-doubly-stochastic matrix differs; the star n = 3 with stationary mu gives 4/7; the 4-cycle (up,down) at {0,1},{0,2} = (1/3,1/6),(2/3,1/3). result.json labels the n = 4 numbers Tier C; this ledger files all numerics as Tier X (computed by an unverified script, never supporting a claim). Re-running the script reproduced numerics_evograph.json (git reports no change).",
            [], num([N4 / "numerics_evograph.py", N4 / "numerics_evograph.json"], instrument="python3 Fractions script numerics_evograph.py")),
        rec("EG-X-0002", "X", "numeric",
            "Paper-stage recompile by the same AI pipeline (not independent): the five EvoGraph files compiled again with lean_pinned.py (taskset -c 4,5, no olean written), rc 0 for all five, #print axioms lines identical to the producer transcripts (23 lines for the claimed modules, 3 planted lines reporting sorryAx and ctl_cheat).",
            [], num([RECOMP[k] for k in ORDER], instrument="scripts/certified_numerics/lean_pinned.py compile")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(len(claims), "claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
