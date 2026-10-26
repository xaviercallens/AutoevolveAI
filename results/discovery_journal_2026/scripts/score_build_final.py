"""Apply the frozen RUBRIC.md to every candidate and emit scores.json, the ranked table and the selection.

Scores and their one-line justifications are entered by hand below (one row per candidate); this
script only checks coverage, sums, ranks, applies the hard rules mechanically and writes the files.
Run: .venv/bin/python -I results/discovery_journal_2026/scripts/score_build.py
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
OUT = ROOT / "results/discovery_journal_2026"
ZEN = json.loads((OUT / "zenodo_inventory.json").read_text())
GH = json.loads((OUT / "github_inventory.json").read_text())

M, P, G, N, A = ("mathematics", "physics", "genetics/biology", "numerics/software",
                 "AI methodology/verification")
C, F, E, O = "cosmology", "fusion/plasma", "education/textbook", "other"
MIN_DOMAINS = [M, P, G, N, A]
GH_DOMAIN = {"AI agents/methodology/verification": A, "education": E, "personal/other": O}

ZBY = {r["id"]: r for r in ZEN}
GBY = {r["name"]: r for r in GH["repos"] if r["science_relevant"]}

CRIT = ["c1_rigour", "c2_independent_check", "c3_reproducibility", "c4_synthesis",
        "c5_honesty_learning", "c6_novelty", "c7_value_to_people"]


def S(*pairs: Any) -> dict[str, dict[str, Any]]:
    """Seven (score, justification) pairs in criterion order."""
    assert len(pairs) == 14, pairs
    out: dict[str, dict[str, Any]] = {}
    for i, key in enumerate(CRIT):
        score, why = pairs[2 * i], pairs[2 * i + 1]
        assert score in (0, 1, 2, 3), (key, score)
        out[key] = {"score": score, "why": why}
    return out


CANDS: list[dict[str, Any]] = []


def Z(cid: str, members: list[int], primary: int, domain: str, title: str, scores: dict[str, Any],
      lesson: bool = False, merge: str = "", repos: list[str] | None = None,
      exclusion: str = "") -> None:
    CANDS.append({"id": cid, "source": "zenodo", "members": members, "primary": primary,
                  "domain": domain, "title": title, "scores": scores, "lesson": lesson,
                  "merge_note": merge, "repos": repos or [], "exclusion_note": exclusion})


def R(cid: str, repos: list[str], title: str, scores: dict[str, Any], lesson: bool = False,
      merge: str = "", domain: str | None = None) -> None:
    d = domain or GH_DOMAIN.get(GBY[repos[0]]["domain"], GBY[repos[0]]["domain"])
    CANDS.append({"id": cid, "source": "github", "members": [], "primary": None, "domain": d,
                  "title": title, "scores": scores, "lesson": lesson, "merge_note": merge,
                  "repos": repos, "exclusion_note": ""})


ZI = "zenodo_inventory.json"
RP = "results/kernel_replay_2026-10-26/replay.jsonl"
TS = "papers/textbook_formalisation_2026/TIER_STATUS.md"
FIVE_GATE = "'5-round peer review' label of the Oct-19 batch: AI-agent review with no audit artifact; the same batch's label was withdrawn as script-generated (23525655, 23468458)"

# ---------------------------------------------------------------- Zenodo works, May-Aug 2026
Z("Z-WARS", [20380024, 20391921, 20392279, 20392301, 20392380, 20392388, 20392541, 20392549,
             20392598, 20392604, 20392809, 20393020, 20393091], 20380024, A,
  "WARS-CI-DFA biomimetic learning on a TPU v5e",
  S(0, f"{ZI} 20380024: one-sentence claim of Lean verification; files list has no .lean file, only a benchmark JSON",
    0, "known_later_status: no memory note, no audit of this record",
    1, "files: runux_ai_engine.py, scikit_runux_ext_stub.py, tpu_benchmark_results.json (code, no commands)",
    1, "inventory flags lean yes (as claimed) + numerics yes = 2 pillars",
    1, "self_reported_caveats empty; 13 identical deposits",
    1, "claimed new learning loop, no later reuse recorded",
    1, "a 40% power saving is claimed but nothing lets a reader check it"),
  merge="13 identical-title deposits merged (duplicate cluster x13 in zenodo_inventory.md)")

Z("L-RUNUX", [20383038, 20383105, 20383112, 22879667], 22879667, N,
  "RunuX: fixed-point attention on a T4, version 2 withdrawing version 1",
  S(1, f"{ZI} 22879667: v2 keeps measured T4 results and closed-form analysis; lean_component no",
    1, "self-withdrawal; the claims-vs-evidence audit 22985926 comes from the same pipeline and its independence is not documented",
    2, "files: zenodo_open_science_bundle.tar.gz + paper (code and measured data)",
    0, "numerics only (domain numerics/software, lean no): 1 pillar",
    3, "description: v1 TPU, 70B and Lean results 'were never run ... withdrawn, not relabeled'",
    1, "incremental measurement of one attention kernel",
    3, "a concrete trust-in-AI lesson: an AI-assisted paper reported experiments that never ran"),
  lesson=True, merge="RunuX v1 (3 duplicate deposits) merged with its v2 withdrawal (same concept per known_later_status)",
  exclusion="v1 central claims withdrawn by v2: eligible only as a lesson, scored on 22879667")

Z("Z-SYMBRAIN", [20397720], 20397720, A, "SymBrain neuro-symbolic small-model architecture",
  S(0, f"{ZI} 20397720: GSM8K/MATH figures self-reported, floating point only",
    0, "known_later_status: no memory note",
    0, "files: a paper draft and a results JSON, no code",
    0, "numerics only: 1 pillar",
    1, "no caveat",
    1, "architecture description, not reused",
    1, "benchmark numbers a reader cannot check"))

Z("Z-CPUGYM", [20538871, 20539058], 20538871, N, "CPUGym V9 final freeze artefacts",
  S(0, f"{ZI} 20538871: RL checkpoints and telemetry, floating point only",
    0, "known_later_status: no memory note",
    1, "files: model package and dataset tarballs; no commands documented",
    0, "numerics only",
    1, "no caveat",
    1, "artefact freeze; the second deposit is a duplicate",
    0, "a compiler-RL artefact freeze with no stated public benefit"),
  merge="two freezes of the same artefacts merged")

Z("L-DUALSCALE", [20863378, 20863381, 21350629, 22837833, 22837837, 22837842, 22841095], 22837842, P,
  "The dual-scale hypothesis tested against data and retracted (revision 5 and the pre-registered verdicts)",
  S(2, f"{ZI} 22837842: the formal mathematics stays Tier A, standard axioms only, '#print axioms logs' (description)",
    1, "the twining test and the pre-registered verdicts (22837837) were run by the programme itself; no independent verdict file",
    1, "files: PDF + LaTeX only; the Lean code is in public repos (LeanMaster, LeanProposal)",
    2, "physics + mathematics + formal proof (22837842 numerics flag no): 3 pillars",
    3, "rev. 5: 'the conjecture in its testable form does not survive', the 27720 lock fails at all 25 non-identity classes; 22837837 reports four negative verdicts",
    2, "pre-registered confrontation with frozen decision rules (22837837) was new for the programme",
    2, "a dark-sector theory tested against data and dropped: a story anyone can follow"),
  lesson=True,
  merge="research-line merge (same hypothesis): K3 dark-sector Parts I-II (20863378, 20863381), Topological Phase Cosmology (21350629), the Stream-3 test (22837833), the pre-registered verdicts (22837837), rev. 5 (22837842) and the student companion book (22841095); repos DarkMatterK3-Home, Dual-Scale-Agora-Lab, DualScaleTopologicalUniverseModel-LeanProposal, Agora-AlphaEvolve-K3-T2, Agora-K3-Quatum, DualScaleSimulator",
  repos=["DarkMatterK3-Home.github.io", "SocrateAI-Dual-Scale-Agora-Lab",
         "SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal",
         "SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2",
         "xaviercallens-SocrateAI-Scientific-Agora-K3-Quatum", "SocrateAI-Scientific-DualScaleSimulator"],
  exclusion="the physical dual-scale/K3 dark-sector claims were refuted by 22837837/22837842: eligible only as a lesson, scored on 22837842")

Z("Z-TRIADIC", [22108301], 22108301, M, "Triadic frustration index in 3D Navier-Stokes",
  S(1, f"{ZI} 22108301: 'zero unproven physical axioms' is not an axiom audit; a conditional reduction (human argument)",
    0, "known_later_status: no memory note",
    1, "files: two .tex and one .lean, no data or commands",
    2, "mathematics + formal (lean yes) + numerics (Galerkin ball): 3 pillars",
    2, "self_reported_caveats: the bridge is a 'conditional reduction'",
    1, "incremental index proposal",
    1, "abstract for a non-specialist"))

Z("Z-ETA-RAMANUJAN", [22160184], 22160184, M, "Ramanujan eta-quotients: classification, Lean, numerics",
  S(1, f"{ZI} 22160184: Lean theorems via native_decide, which trusts the compiler (outside the axiom whitelist; known_later_status, memory verification-traps.md); Python audit 108/108",
    0, "no audit recorded",
    2, "files: REPRODUCE.md, eta_quotient_verify.py, Lean file, zip",
    2, "mathematics + numerics + formal: 3 pillars",
    2, "AI-assistance disclosure under Tao's guidelines (caveat)",
    1, "reconstruction of a known classification",
    1, "abstract for a non-specialist"))

Z("Z-MHD-NO", [22161523], 22161523, P, "Structure-preserving neural operators for MHD",
  S(1, f"{ZI} 22161523: '5 theorems, zero sorry, exit 0'; exit code is not an axiom check (memory verification-traps.md)",
    0, "no audit recorded",
    2, "files: REPRODUCE.md, spectral_verification.py, Lean module, zip",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    1, "no caveat",
    2, "a new method-tool (divergence-free operator)",
    2, "plasma modelling for fusion energy, explained in the record"))

Z("Z-FRICKE", [22682139], 22682139, M, "Lean 4 formalization of the Fricke involution",
  S(2, f"{ZI} 22682139: 16 headline theorems pinned by #print axioms guards, footprint exactly the 3 standard axioms; negative control",
    1, "the 'first formalization' claim was 'refuted during audit'; the auditor is not identified and no verdict file exists",
    2, "files: Lean sources, theorems.jsonl, PROOF-PATH.md",
    1, "mathematics + formal: 2 pillars",
    3, "self_reported_caveats: a negative-result section, and a claim refuted during audit and withdrawn",
    2, "a new formalization",
    1, "abstract for a non-specialist"))

Z("Z-LIGOZAT", [22682148], 22682148, M, "Eta-quotients in Lean 4: cusp orders and Ligozat's criterion",
  S(2, f"{ZI} 22682148: 'the Lean development compiles and is axiom-audited'",
    1, "REVIEW_RESPONSE.md present, reviewer not identified; 'NOT PEER REVIEWED'",
    2, "files: Lean sources, paper_gate.py, theorems.jsonl",
    1, "mathematics + formal: 2 pillars",
    2, "names the exact obstruction for general N, which is not proved",
    2, "a new formalization at three strengths",
    1, "abstract for a non-specialist"))

Z("Z-FRICKE-SD", [22692600], 22692600, M, "Fricke-self-dual eta-quotients are eigenforms",
  S(2, f"{ZI} 22692600: 'axiom-audited', 333 declarations sorry-free",
    1, "no external referee (caveat)",
    2, "files: Lean sources, theorems.jsonl",
    1, "mathematics + formal: 2 pillars",
    2, "physics only in docstrings, marked not formalized",
    1, "a corollary of 22682148",
    1, "abstract for a non-specialist"))

Z("L-NS-FRAMING", [22723078, 22773907], 22773907, P,
  "Where the continuum ends: version 2 withdrawing the 'topological censorship' framing of the OpenAI Navier-Stokes analysis",
  S(2, f"{ZI} 22773907: compiles against OpenAI's ProblemStatement 'with no sorry and standard axioms only'",
    1, "REVIEW_AND_NEW_DIRECTION.md is an internal review, no independent verdict",
    1, "files: ModelValidity.lean + .tex",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "withdraws v1's framing ('topological censorship', 'pathway to Statement A') with a table of corrections",
    3, "the model-validity (Knudsen/Mach) reading is reused by 22838708 ('companion to 22773907') and Trilogy II",
    2, "why a mathematical blow-up need not mean real water blows up"),
  lesson=True, merge="22723078 (v1 framing) merged with its successor 22773907",
  exclusion="22723078's framing was withdrawn: eligible only as a lesson, scored on 22773907")

Z("Z-NS-PHYSREAD", [22838708], 22838708, P, "The OpenAI Navier-Stokes and Euler blow-up proofs: a physical reading",
  S(1, f"{ZI} 22838708: 'zero custom axioms' refers to OpenAI's proofs; the record's own Lean files carry no axiom statement in the inventory",
    1, "PEER_REVIEW_2026-09-15.md, reviewer not identified",
    2, "67 files: code, experiment results, gate JSONs",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    2, "'This is not a refutation of that result'; one reading withdrawn with a formal reason",
    2, "exact BGK shear-mode spectrum as a new result",
    2, "the difference between a fluid equation and real fluids, explained"),
  repos=["OpenAI-NSE-Epistemic-Audit"], merge="repo OpenAI-NSE-Epistemic-Audit is this record's code home")

Z("Z-MECHANICA", [22823607], 22823607, M, "MechanicaFluidorum: verifier-in-the-loop programme on 3D Navier-Stokes regularity",
  S(2, f"{ZI} 22823607: kernel-checked theorems, zero sorry, axiom footprint {{propext, Classical.choice, Quot.sound}}",
    1, "internal audit packet (docs/AUDIT_PACKET.md); no independent verdict",
    2, "release tarball v1.9.0 with exact-rational checkers and failing negative controls",
    2, "mathematics + formal + numerics: 3 pillars",
    2, "'Hypothesis U itself remains open'",
    2, "a staged verifier-in-the-loop programme design",
    1, "abstract for a non-specialist"),
  repos=["SocrateAI-Scientific-MechanicaFluidorum", "SocrateAI-Scientific-Mensura"],
  merge="repos MechanicaFluidorum and its exact-arithmetic companion Mensura are this record's code home")

Z("Z-LABMETHOD", [22829767], 22829767, A, "A laboratory method for AI-assisted science (the claim ledger that became Elenchus)",
  S(1, f"{ZI} 22829767: a method paper; its claims are about practice (human argument)",
    1, "self-report of one month of practice",
    0, "files: one PDF; the Elenchus repository is PRIVATE (github_inventory visibility)",
    2, "inventory flags lean yes + numerics yes: formal, mathematics, numerics = 3 pillars",
    2, "reports what it did, including an audit of an AI-generated blow-up proof",
    3, "became the Elenchus tier ledger whose gate runs on every later programme paper (known_later_status; registry ledger_gate ED-06..24)",
    3, "how to make AI-assisted science trustworthy, stated in plain terms"),
  repos=["SocrateAI-Scientific-Elenchus"], merge="private repo SocrateAI-Scientific-Elenchus implements this method")

Z("Z-DS-GEOM", [22823718], 22823718, P, "Dual-scale generalized geometry on K3 x T2 (Lean)",
  S(2, f"{ZI} 22823718: Tier A, no axioms beyond the three standard ones",
    1, "no independent audit",
    1, "files: PDF + LaTeX; Lean in the public LeanMaster repo",
    2, "physics + mathematics + formal: 3 pillars",
    2, "Tier A/L/C labels separate the kernel-checked part from physical readings",
    1, "incremental Lean result",
    1, "abstract for a non-specialist"),
  exclusion="kept separate from L-DUALSCALE: rev. 5 says the formal mathematics stays Tier A")

Z("Z-MOONSHINE", [22837835, 22823720], 22837835, M, "Mathieu moonshine computed in Lean (with M24 rigidity and BPS dyons)",
  S(2, f"{ZI} 22837835: Tier A, 101 and 44 theorems, at most the three standard axioms",
    1, "no independent audit",
    1, "files: PDF + LaTeX; Lean in public repos",
    2, "physics (22823720) + mathematics + formal: 3 pillars",
    2, "every physical reading is Tier L or C",
    2, "moonshine computed from closed formulas in Lean",
    1, "abstract for a non-specialist"),
  merge="research-line merge: 22823720 (M24 rigidity) and 22837835 (moonshine computed) are the same Lean moonshine computation; per-criterion best member cited")

Z("Z-AGORA-RES", [22823724, 22823726, 22823729], 22823724, P, "Formal resolutions of conjectures in the Lean 5 Agora corpus (papers 4-6)",
  S(2, f"{ZI} 22823724: Tier A, three standard axioms (description)",
    1, "no independent audit",
    1, "files: PDF + LaTeX",
    2, "physics + mathematics + formal: 3 pillars",
    2, "Tier A/L/C labels stated (caveat field)",
    1, "three papers of one series, incremental",
    1, "abstract for a non-specialist"),
  merge="research-line merge: papers 4, 5, 6 of the same series")

Z("Z-LATTICES", [22837843], 22837843, M, "Lattices, T-duality and double field theory on K3 x T2 in Lean (LeanMaster)",
  S(2, f"{ZI} 22837843: 100 theorems, zero sorry, three standard axioms",
    1, "LeanMaster README revised after an internal audit (github_inventory lessons); no verdict file for this record",
    2, "public LeanMaster repo with lake build and the axiom-audit / statement-lock tools (github summary)",
    1, "mathematics + formal (numerics no): 2 pillars",
    2, "a dedicated section on what the formalization does not establish",
    3, "LeanMaster's gate tools and its contrib/openai_math_corollaries are reused by the later papers (memory five-contributions-workflow-2026-10-25.md)",
    1, "abstract for a non-specialist"),
  repos=["SocrateAI-Scientific-Agora-LeanMaster", "xaviercallens-SocrateAI-Scientific-LeanMaster-StringTheoryFormalization",
         "SocrateAI-Scientific-LeanMaster-CoreStringTheoryFormalization"],
  merge="LeanMaster repo, its earlier public copy and a one-commit placeholder are this record's code home")

Z("Z-TRIAD", [22841098], 22841098, P, "The Frontier Triad on K3 x T2",
  S(2, f"{ZI} 22841098: Tier A, three standard axioms",
    1, "no independent audit",
    1, "files: PDF + LaTeX",
    2, "physics + mathematics + formal: 3 pillars",
    3, "the published revision corrects orientifold bookkeeping without changing any Lean statement",
    1, "incremental",
    1, "abstract for a non-specialist"))

Z("Z-BH-K3", [22854868], 22854868, M, "Smallest black hole picks a K3 surface, the vacuum does not",
  S(1, f"{ZI} 22854868: 'checked by the Lean 4 kernel' without an axiom statement in the inventory",
    1, "no independent audit",
    0, "the record lists no files",
    1, "mathematics + formal: 2 pillars",
    2, "physical readings labelled with the three-tier convention",
    1, "incremental",
    1, "abstract for a non-specialist"))

Z("Z-TDUAL-CORR", [22872083], 22872083, P, "Tiered formal and numerical methods for T-duality (corrected version)",
  S(1, f"{ZI} 22872083: lean4_formal_proofs.tar.gz shipped, no axiom statement in the inventory",
    1, "corrections came from bridging to an external Lean formalization: a cross-check, not an audit verdict",
    2, "12 files incl. PRE_REGISTRATION.md, TELEMETRY_PROVENANCE.json, a Rust solver",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "supersedes 22683565 and withdraws its claims; 'withdrawn as a physical result'",
    1, "incremental",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("Z-CLAIMS-AUDIT", [22985926], 22985926, A, "Claims vs. evidence: audit of an AI-assisted Rust kernel",
  S(1, f"{ZI} 22985926: static measurements of a codebase (counts); SpecDefects.lean without an axiom statement",
    1, "the audit is by the same author pipeline as the audited code",
    2, "files: metrics.baseline.json, units_status.csv, units_summary.json, SpecDefects.lean, source",
    2, "inventory flags lean yes + numerics yes: 3 pillars",
    3, "finds 141 of 316 crates are placeholders and 249 open sorry obligations behind a 'zero sorry' claim; quarantines an unsubstantiated peer-review report",
    2, "proposes an oracle-gated proof-completion workflow",
    3, "the documentation said 'zero sorry' while much of the code was placeholders: a concrete trust-in-AI lesson"),
  lesson=True)

Z("Z-SELFDUAL", [22992255], 22992255, P, "When does self-duality cause physics? A machine-checked criterion",
  S(3, f"{ZI} 22992255: 116 theorems, every module re-checked by a second, independent kernel (nanoda)",
    1, "no independent audit recorded",
    1, "record ships one PDF; the public repo SectorCausalityTheory has the Lean, notebooks and MCP server",
    3, "physics + mathematics + formal + numerics/experiment: 4 pillars",
    3, "publishes an erratum on the CMB forecast basis and keeps the 'not forced' cases (caveats)",
    2, "a new criterion tested on sixteen systems",
    2, "when a symmetry matters physically, explained with the Ising model"),
  repos=["SocrateAI-Scientific-SectorCausalityTheory"], merge="repo SectorCausalityTheory is this record's code home")

Z("Z-BAO-REPRO", [23003926], 23003926, C, "Agent-executed preregistered BAO reproduction pipeline (cosmo3)",
  S(2, f"{ZI} 23003926: 28 Lean theorems, trusted axioms only",
    3, "three rounds x three AI referees with author responses recorded (papers/cosmo_synthesis/reviews/round{1,2,3}_*.md; memory cosmo3-run.md)",
    2, "bundle + MANIFEST + Hugging Face dataset (memory cosmo3-run.md)",
    3, "cosmology + mathematics + formal + numerics: 4 pillars",
    2, "limitations stated: no human review, preregistrations not git-committed, DR1 offset unexplained",
    2, "agent-executed reproduction with preregistered tolerances",
    2, "AI agents reproducing a dark-energy measurement within preset tolerances"))

Z("Z-K3-BOOK", [23030322], 23030322, E, "K3 Surfaces from the Lattice Up (textbook, ed. 0.1)",
  S(1, f"{ZI} 23030322: 'a verified core', no axiom statement",
    0, "no review recorded",
    1, "files: LaTeX sources only",
    2, "inventory flags lean + numerics: 3 pillars",
    1, "self_reported_caveats empty",
    2, "a new textbook",
    2, "teaching material"))

Z("Z-LAYA", [23078485, 23095224], 23078485, A, "Laya-LoRA Coding Companion (camera-ready v3)",
  S(0, f"{ZI} 23078485: latency and anti-hallucination claims; Lean claim without axiom evidence",
    0, "telemetry treated as self-reported (memory kev-saaw-decision-gate-finding.md)",
    0, "the record lists no files",
    1, "inventory flags lean + numerics: 2 pillars",
    1, "no caveat",
    1, "incremental",
    1, "a coding assistant whose claims cannot be checked from the record"),
  merge="duplicate deposit 23095224 merged")

Z("Z-GWAYA", [23119953, 23120120], 23119953, A, "GWAYA fail-closed verification gate for LLM-generated code (v3, v3.1)",
  S(2, f"{ZI} 23119953: shows a Lean file proving 1 = 2 from a hidden axiom compiles with exit 0 and is rejected only by the axiom audit",
    1, "repo CLAIM_AUDIT files are the author's own audits (CLAIM_AUDIT_3120_author.md)",
    2, "description: bundle with sources, tests, raw results and SHA-256",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "withdraws v1/v2 benchmark figures; reports that the gate accepted semantic bugs",
    2, "a new fail-closed gate",
    3, "a filter that stops AI-written code that only looks correct"),
  repos=["GWAYA-GwenLayaOpenModel"], merge="v3 and v3.1 (consecutive versions deposited as separate concepts) merged; repo GWAYA is the code home")

Z("Z-COND-DEPTH", [23228685], 23228685, M, "Logarithmic boundary depth and conditioning of the discrete inverse conductance problem",
  S(0, f"{ZI} 23228685: preregistered floating-point measurements",
    1, "preregistered gates run by the author (self-check)",
    2, "files: code.zip, dataset.zip, paper",
    1, "mathematics + numerics: 2 pillars",
    3, "'refuted predictions are kept and listed'",
    2, "a new measured scaling law",
    1, "abstract for a non-specialist"))

Z("Z-DYADIC", [23232389], 23232389, M, "The absolute dyadic triangular Hilbert sum: sharp constant at least 3",
  S(1, "registry ED-01: exact integer traces and a human proof; 'nothing in it is machine-checked'",
    1, "an independent pre-publication review is documented (memory dyadic-hilbert-preprint.md) but no verdict file exists (registry audit_verdict null): lower value",
    2, "source bundle + MANIFEST",
    1, "mathematics + exact computation: 2 pillars",
    2, "absolute sum only; nothing claimed for the signed form",
    2, "an exact product rule and a new lower bound",
    1, "abstract for a non-specialist"))

Z("Z-CALDERON", [23241463], 23241463, M, "Exact exponential rates for the discrete Calderon problem on strips",
  S(1, f"{ZI} 23241463: sharp exponent by block diagonalisation (human proof); a Bernstein-Walsh step is 'a sketch'",
    1, "preregistered gates run by the author",
    2, "files: code.zip, dataset.zip",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "one prediction refuted narrowly and a gate failed as written, both reported",
    2, "a sharp exponent",
    1, "abstract for a non-specialist"))

Z("Z-TOPO-PROXY", [23244556], 23244556, M, "A topological proxy for ill-conditioning (persistent homology)",
  S(0, f"{ZI} 23244556: floating-point persistent homology",
    1, "preregistered gates run by the author",
    2, "files: code.zip, dataset.zip",
    1, "mathematics + numerics: 2 pillars",
    3, "the waveform prediction was refuted narrowly, reported",
    1, "incremental",
    1, "abstract for a non-specialist"))

Z("Z-LT-NULL", [23245266], 23245266, M, "Null result for the matrix-valued sharp 1D Lieb-Thirring inequality, and a Comparator check",
  S(3, "memory matrix-lt-lab.md: the scalar theorem is accepted by leanprover/comparator (kernel replay) under the pinned stack, with controls; whitelist axioms",
    1, "the pre-publication review that fixed defects has no verdict file (registry ED-02 audit_verdict null): lower value",
    2, "bundle + MANIFEST; tables generated from result files",
    2, "mathematics + formal + numerics: 3 pillars",
    3, "a published null result that refuses the 'breakthrough' framing",
    2, "a new adversarial search instrument",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("Z-BAO-P1", [23247730], 23247730, C, "Kernel-checked enclosures of DESI DR2 BAO distances",
  S(3, "memory certified-numerics-p1.md + results/certified_numerics/P1_bao/verification.md: an untrusted solver's integer tables are re-checked by the Lean kernel (decide +kernel, no native_decide); 55 theorems axiom-audited",
    3, "P1 verification.md CONFIRMED_WITH_CORRECTIONS; 13 attribution and scope defects fixed before publication (memory)",
    3, "the independent verifier recompiled Core/Fit/EdS/FitOm101 with matching axiom output (verification.md section 2)",
    3, "cosmology + mathematics + numerics (CVODE, astropy) + formal: 4 pillars",
    2, "scope: one parameter point, Om = 0.29743 is the rusty-SUNDIALS fit, not DESI's",
    3, "the integer-certificate method is reused by P2/P3 (23284020) (memory certified-numerics-p2-p3.md)",
    2, "distances across the universe with a machine-checked error bar"))

Z("Z-COLRES", [23248393], 23248393, M, "Ill-conditioning as dependence on earlier span: a column-residual certificate",
  S(1, f"{ZI} 23248393: 'one bound is machine-checked in Lean', no axiom statement",
    1, "preregistered gates run by the author",
    2, "files: code.zip, dataset.zip",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "a preregistered bound of 1.5 was refuted, reported",
    2, "a new certificate",
    1, "abstract for a non-specialist"))

Z("Z-COOPER", [23248582], 23248582, M, "Symmetric-square structure theorem for Cooper's Apery-like operators",
  S(2, f"{ZI} 23248582: three standard axioms, no sorry, no native_decide",
    1, "no independent audit",
    2, "files: Lean development tarball + LaTeX",
    1, "mathematics + formal: 2 pillars",
    3, "publishes that the s10 and s18 partners are non-integral by finite witnesses; repo README discloses retracted C1/C2 numbers",
    2, "a structure theorem",
    1, "abstract for a non-specialist"),
  repos=["SocrateAI-Scientific-Agora-K3-DarkMatter"], merge="repo Agora-K3-DarkMatter holds these Cooper s7/s10 proofs")

Z("L-VORTEX", [23262132, 23262143], 23262132, P, "Vortex friction follows temperature, not normal density (correction, with transport paper v2.2)",
  S(0, f"{ZI} 23262132/23262143: floating-point classical-field measurements; no axiom-checked Lean claim",
    3, "23262143: 'revised after an external peer review (recorded verbatim in the repository, docs/peer_review/)', corrections applied in v2 and v2.2",
    1, "records ship PDFs only; code in the public QuantumFluids/rusty-SUNDIALS repos",
    3, "inventory flags physics + lean + numerics: 4 pillars",
    3, "withdraws the 'geometric core size' reading; a second implementation finds a 5-20% bias, reported",
    2, "a cutoff-independent friction law",
    1, "abstract for a non-specialist"),
  lesson=True, merge="correction paper 23262132 merged with the paper it corrects (23262143 v2.2); per-criterion best member cited")

Z("Z-QFPGPE", [23269715], 23269715, N, "qf-pgpe: Rust projected Gross-Pitaevskii engine",
  S(0, f"{ZI} 23269715: floating-point solver",
    1, "validated across languages by the author",
    1, "record ships a PDF; code in the public rusty-SUNDIALS repo (23272154 description)",
    0, "numerics only: 1 pillar",
    2, "'no claim is made about GPU codes'",
    2, "a new solver tool",
    1, "abstract for a non-specialist"))

Z("Z-GODFRIN", [23272154], 23272154, E, "Quantum Fluids in Lean 4: a tribute to Henri Godfrin (textbook)",
  S(2, f"{ZI} 23272154: every module compiles with no sorry and depends only on the three standard axioms",
    1, "audited for the book by the author",
    2, "book sources tarball; Lean library public",
    2, "inventory flags lean + numerics (domain education): 3 pillars",
    3, "corrections found while writing are stated (Kosterlitz-Thouless hypotheses admit only trivial trajectories)",
    2, "a new textbook",
    3, "a teaching book built on real neutron-scattering experiments"))

Z("Z-TOPO-PROG", [23283365], 23283365, P, "Topology constrains, under a gap, what geometry determines (programme)",
  S(1, f"{ZI} 23283365: Lean where reachable, no axiom statement in the inventory",
    1, "preregistered measurements by the author",
    2, "files: code.zip, dataset.zip",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    2, "measured limits stated",
    1, "a programme paper",
    1, "abstract for a non-specialist"))

Z("Z-BAO-P23", [23284020], 23284020, C, "Kernel-checked constraints from DESI DR2 BAO: Omega_m bands and H0 >= 73 excluded",
  S(3, "registry ED-04 (206 Lean files) + memory certified-numerics-p2-p3.md: interval evaluation and planner boxes re-checked by the Lean kernel, axiom audit control C7/C11",
    3, "P2 and P3 verification.md, both CONFIRMED_WITH_CORRECTIONS (registry ED-04)",
    3, "independent recompiles into a separate olean dir (P2 verification.md section 2, 3 of 29 slabs rebuilt; P3 verification.md section 2)",
    3, "cosmology + mathematics + numerics + formal: 4 pillars",
    2, "certified version of a known tension; the preregistered slab layout H8 failed and was amended (disclosed)",
    2, "extends the P1 method to a likelihood",
    3, "the Hubble tension, a well-known open puzzle, bounded by a proof checker"))

Z("Z-RIESZ", [23285631], 23285631, M, "Riesz-energy, finiteness and every-density corollaries of openai/math universal optimality",
  S(3, f"{RP}: Triangular.Riesz, RieszFinite, AnyDensity replayed rc 0; whitelist axioms",
    3, "results/discovery/D1, D2 verification.md CONFIRMED_WITH_CORRECTIONS; referee ACCEPT_WITH_CORRECTIONS, all applied (memory discovery-triangular-riesz.md)",
    3, "the verifiers recompiled independently (D1 verification.md) and the 2026-10-26 replay matches",
    1, "mathematics + formal (numerics no): 2 pillars",
    2, "conditional on the upstream AI-generated theorem; informative only for Riesz s > 2",
    3, "its admissibility corollaries are reused by the exciton, Yukawa and Keldysh papers and the textbook (registry ED-08..11)",
    1, "abstract for a non-specialist"),
  repos=["triangular-universal-optimality-lean"], merge="repo triangular-universal-optimality-lean is the red-team home of these corollaries")

Z("L-EXCITON", [23289027, 23294615, 23297479, 23298292, 23302787, 23458123], 23297479, P,
  "Gated exciton fluids, papers I-V and the lattice-optimality dependency check",
  S(2, f"{ZI} 23297479 (II): 52-theorem Lean formalisation, no sorry, standard axioms only",
    1, "no independent audit file; V answers 'the reviewer's question' without a recorded verdict",
    2, "each record ships a sources tarball",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "III, IV and V publish failed gates and unconfirmed heuristics (23298292, 23302787, 23458123)",
    2, "image-charge complete-monotonicity proof (I) is new",
    2, "gated exciton fluids for future devices, honestly reported as not working yet"),
  lesson=True, repos=["rusty-Fenris-CMRR"],
  merge="research-line merge: the 'Gated exciton fluids' series I-V plus its opening dependency check 23289027; repo rusty-Fenris-CMRR is the CM-relaxation code of IV; per-criterion best member cited")

Z("Z-UO-TIERED", [23293429], 23293429, P, "Planar universal optimality, tiered: Lean consequences and a CVODE N-body check (v1/v2)",
  S(3, f"{RP}: Triangular.UniversalOptimality (D3) replayed rc 0",
    3, "results/discovery/ledger/manuscript_audit_2026-10-11.md: ACCEPT_WITH_CORRECTIONS (B1-B3 fixed), re-audit RESOLVED_WITH_MINOR (memory yukawa-cvode-tiered-paper.md)",
    3, "D3 verification.md: verifier recompiled all five theorems; replay rc 0",
    3, "physics + mathematics + CVODE N-body numerics + formal: 4 pillars",
    2, "reports the annealing failure at kappa = 1; the truncation erratum is owed and fixed later in 23646105",
    3, "its ledger + CVODE consistency-check design is reused by 23646103/05/07 (registry ED-09..11)",
    2, "why repelling particles settle into triangles, shown by simulation"),
  merge="v1 23293112 and v2 23293429 share concept 23293111 (registry ED-06/07)")

Z("Z-UO-BOOK", [23295142], 23295142, E, "The Triangular Lattice and Universal Optimality (student textbook)",
  S(3, f"{RP}: Triangular.OpenDisk and OpenDiskAny (D4) replayed rc 0",
    3, "results/discovery/D4/verification.md ACCEPT_WITH_CORRECTIONS; the whole-book AI audit led to 20 fixes (memory textbook-universal-optimality.md)",
    3, "D4 verification.md: all four theorems recompiled by the verifier, rc 0",
    2, "inventory flags lean + numerics (domain education): 3 pillars",
    2, "AI-generated source theorem, not peer reviewed; inherits the truncation erratum",
    2, "a new textbook",
    3, "a student textbook from definition to laboratory"))

Z("Z-QFLIB", [22853896, 23319576], 23319576, P, "QuantumFluids: Lean 4 library of quantum-fluid structure (89 to 257 theorems)",
  S(3, f"{ZI} 22853896: every theorem axiom-audited and re-checked by Comparator against two independent kernels",
    1, "the withdrawals came from the project's own literature check (RETRACTIONS.md)",
    2, "versioned release zips v1.2.0 to v1.23.0",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "two findings withdrawn after a literature check; a topological hypothesis refuted by simulation",
    3, "the library is reused by 23646111/23646117 and the Godfrin textbook 23272154",
    2, "what formal verification does and does not buy for quantum-fluid codes"),
  repos=["SocrateAI-Scientific-QuantumFluids"],
  merge="22853896 (89 theorems) and 23319576 (257 theorems) are the same library under two concepts")

Z("Z-WEIERSTRASS", [23434158], 23434158, M, "Kernel-checked Weierstrass elliptic-curve arithmetic and Dream-to-Retrain",
  S(2, f"{ZI} 23434158: zero sorryAx, trusted axioms only",
    1, "'all referee audits carry auditor_kind = model', no verdict quoted: lower value",
    2, "bundle + MANIFEST",
    2, "mathematics + formal + numerics: 3 pillars",
    2, "limitations stated (the BSD sentinel fails as expected)",
    1, "incremental",
    1, "abstract for a non-specialist"))

Z("Z-ENSTROPHY10", [23458238, 23468458], 23468458, M, "Cutoff-uniform enstrophy bounds in dyadic hierarchies: ten hypotheses (v2.1)",
  S(2, f"{ZI} 23458238: zero sorryAx",
    1, "no independent audit",
    2, "bundle + MANIFEST",
    2, "mathematics + formal + numerics: 3 pillars",
    3, "v2.1 withdraws the scripted 'peer review report' with invented referee personas and corrects the v2.0 description",
    1, "incremental",
    1, "abstract for a non-specialist"),
  merge="23458238 superseded by 23468458")

Z("Z-BIHELM", [23460214], 23460214, M, "Bi-Helmholtz thresholds, dyadic paraproducts, Heegner-Lienard obstructions",
  S(1, f"{ZI} 23460214: no axiom statement in the inventory",
    1, "no independent audit",
    2, "bundle + MANIFEST",
    2, "mathematics + formal + numerics: 3 pillars",
    3, "9 of 15 preregistered hypotheses refuted or obstructed, published",
    1, "incremental",
    1, "abstract for a non-specialist"))

Z("Z-AR-SCREEN", [23467992], 23467992, A, "Karpathy-autoresearch screening and Elenchus deep-dive",
  S(1, f"{ZI} 23467992: no axiom statement in the inventory",
    1, "no independent audit",
    2, "bundle + MANIFEST",
    2, "inventory flags lean + numerics: 3 pillars",
    1, "no caveat",
    2, "a screening funnel",
    1, "abstract for a non-specialist"))

Z("Z-TRILOGY", [23469404, 23482419, 23469410, 23482422, 23469418, 23482424], 23469404, M, "Elenchus Trilogy I-III",
  S(2, f"{ZI} 23469404: 'zero sorryAx, zero custom axioms' (as recorded)",
    1, FIVE_GATE,
    1, "Lean + .tex + telemetry JSON; no runnable numerics shipped",
    2, "mathematics + formal + numerics: 3 pillars",
    1, "no caveat; 'peer-reviewed' label",
    1, "incremental",
    1, "abstract for a non-specialist"),
  merge="three papers x two duplicate deposits merged (one batch)")

Z("L-STELLARATOR", [23478809, 23480005, 23481378, 23482410, 23483052, 23483564, 23483643, 23532458], 23532458, N,
  "RK4 cools at resolved step sizes, it does not heat (edition 2, refuting the stellarator paper's premise)",
  S(1, f"{ZI} 23532458: '18 of 18 declarations clean' with a gate JSON; the inventory text does not state the axiom footprint: lower value",
    1, "'This paper has not been reviewed by anyone other than the author'",
    2, "files: paper_a_v2_experiment.py, figures script, harness, results JSON, Lean",
    2, "numerics + mathematics + formal: 3 pillars",
    3, "refutes edition 1's own motivating hypothesis; withdraws its confidence figures and the Villani/Landau theorem",
    2, "a preregistered 2000-orbit falsification with controls that can fail",
    2, "fusion-plasma simulation: a feared error turned out to be the opposite one"),
  lesson=True, merge="7 identical stellarator deposits merged with their edition-2 refutation",
  exclusion="the stellarator edition-1 premise was refuted by 23532458: eligible only as a lesson, scored on 23532458")

Z("Z-CAP-NS", [23478811, 23480007], 23478811, M, "Computer-assisted proofs in 3D Navier-Stokes and hurricane eyewall Galerkin dynamics",
  S(2, f"{ZI} 23478811: zero sorryAx (as recorded)",
    1, FIVE_GATE,
    1, "Lean + .tex + telemetry; no data",
    2, "mathematics + formal + numerics: 3 pillars",
    2, "includes a formal refutation of an unamended draft identity",
    1, "incremental",
    2, "hurricane eyewall dynamics"),
  merge="two deposits of the same title merged")

Z("L-PQC", [23478813, 23480009, 23481388, 23482416, 23483056, 23483568, 23483649, 23532601], 23532601, O,
  "Maximal order of SQIsign's starting curve (edition 2): withdrawal of three headline claims",
  S(1, f"{ZI} 23532601: edition 2 replaces claims with a PARI measurement; no axiom statement",
    1, "'has not been reviewed by' anyone else (caveat)",
    2, "files: main.rs, paper_c_v2_pari_worker.py, figure scripts",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "withdraws three headline claims: the 'verified SQIsign verifier' accepts the scalar 256",
    1, "incremental",
    3, "post-quantum security: a 'verified' verifier that accepted a forgery"),
  lesson=True, merge="7 PQC deposits (two titles) merged with their edition-2 withdrawal",
  exclusion="edition-1 headline claims withdrawn by 23532601: eligible only as a lesson, scored on 23532601")

Z("Z-LEANFLOW", [23481384, 23482414, 23483054], 23481384, N, "LeanFlow MCP: architecture for computer-assisted proofs and residue certificates",
  S(2, f"{ZI} 23481384: Lean 4.34.1, zero sorryAx, zero custom axioms (as recorded)",
    1, FIVE_GATE,
    1, "the record's files are the Paper B (Navier-Stokes) files, not LeanFlow sources; code is in the public solver repo",
    2, "numerics + mathematics + formal: 3 pillars",
    1, "no caveat",
    2, "a new framework; the lean.certify generator later reused by 23655392/23663551 came from LeanFlow PR #1 commits of the 10-25 P1 lane (registry ED-14), after this record, so the reuse is credited to ED-14",
    2, "a proof checker certifying a simulator's numbers"),
  repos=["SocrateAI-Numeric-DualScale-Solver", "SocrateAI-Numeric-DualScale-Solver-Enterprise",
         "SocrateAI-Scientific-Agora-LeanFlow"],
  merge="three deposits merged; LeanFlow solver repos (public, private copy, private planning) are the code home")

Z("L-SUBGRID", [23483566, 23483647, 23532595], 23532595, M, "Scale-dual subgrid model of 3D Navier-Stokes: the true quadratic invariant (edition 2)",
  S(1, f"{ZI} 23532595: exact rational triads (59,780 evaluations) and Lean files; no axiom statement",
    1, "no independent audit",
    2, "17 files: Lean, scripts, figures",
    2, "mathematics + formal + numerics: 3 pillars",
    3, "refutes edition 1's Theorem 2.5, withdraws the blow-up claim, renames the model (modified Leray-alpha)",
    1, "incremental",
    1, "abstract for a non-specialist"),
  lesson=True, merge="two edition-1 deposits merged with edition 2",
  exclusion="edition 1 Theorem 2.5 refuted by 23532595: eligible only as a lesson, scored on 23532595")

Z("Z-BIOPHYS", [23484342], 23484342, G, "Non-equilibrium biophysics, conformational genetics, bio-inspired materials (Lean)",
  S(2, f"{ZI} 23484342: zero sorryAx (as recorded)",
    1, FIVE_GATE,
    1, "Lean + .tex + telemetry, no data",
    3, "biology + mathematics + formal + numerics: 4 pillars",
    1, "no caveat",
    1, "incremental",
    2, "molecular biophysics"))

Z("L-PROOFREADING", [23490729, 23526783], 23526783, G, "Hopfield-Ninio proofreading (edition 3): refuting the paper's own POLE P286R mechanism",
  S(2, f"{ZI} 23526783: 7 declarations, each with a #print axioms line, whitelist",
    1, "internal AUDIT_2026-10-21 (Genetic repo)",
    2, "26 files incl. tests and a TCGA empirical-check JSON",
    3, "biology + mathematics + formal + numerics: 4 pillars",
    3, "refutes its own mechanism for POLE P286R and adds a no-go theorem",
    2, "a no-go theorem",
    3, "a cancer-associated DNA-polymerase mutation: a model that was wrong, said so"),
  lesson=True, repos=["SocrateAI-Scientific-Genetic"],
  merge="edition 1 (23490729) merged with edition 3; repo SocrateAI-Scientific-Genetic is the code home",
  exclusion="the edition-1/2 POLE mechanism was refuted by 23526783: eligible only as a lesson, scored on 23526783")

Z("L-STOCHTHERMO", [23510019, 23525655], 23525655, G, "Stochastic thermodynamics and chromatin remodelling (edition 2 audit)",
  S(2, f"{ZI} 23525655: ST.T1-T6 depend only on the three standard axioms; 18 helper lemmas unchecked",
    1, "audit by the author pipeline (AUDIT_2026-10-21.md)",
    2, "files: Lean, scripts, AUDIT_2026-10-21.md",
    2, "biology + mathematics + formal (numerics flag no): 3 pillars",
    3, "withdraws 'peer reviewed': the bundled review file 'was generated by a script that calls no reviewer'",
    1, "incremental",
    2, "molecular machines in cells, and an honest correction about fake review"),
  lesson=True, merge="edition 1 (23510019) merged with its edition-2 correction")

Z("Z-RETICULATE", [23604793, 23610116], 23610116, G, "Proof-carrying detection of reticulate evolution (split certificates, tree-level null)",
  S(2, f"{ZI} 23604793: 27/27 declarations, no sorry, whitelist axioms",
    1, "no independent audit",
    2, "real-data JSON, Rust splits, Lean, null sweeps",
    3, "biology + mathematics + formal + numerics: 4 pillars",
    3, "the transfer fails through three named mechanisms; floors understated, corrected (23610116)",
    2, "a split-level certificate",
    2, "detecting recombination in viruses (Hepatitis B, Coxsackievirus)"),
  lesson=True, merge="research-line merge: 23604793 and its correction 23610116; per-criterion best member cited")

Z("Z-GEN-BOOK", [23610123], 23610123, G, "Formal Genetics: Proof, Computation and Evidence in Molecular Biology (edition 12)",
  S(1, f"{ZI} 23610123: no axiom statement in the inventory",
    1, "no independent audit",
    2, "build.py + data JSON + sources",
    3, "biology + mathematics + formal + numerics: 4 pillars",
    3, "this edition publishes the floor correction",
    2, "a new textbook",
    3, "a textbook on evidence in molecular biology"))

Z("Z-GP-TRANSFER", [23611425], 23611425, G, "Behavioural profiles are not heritable sequences: refuted transfer to genetic programming",
  S(1, f"{ZI} 23611425: integer quartet certificate (exact), no axiom statement",
    1, "no independent audit",
    2, "89 files incl. FASTA and Lean",
    3, "biology + mathematics + formal + numerics: 4 pillars",
    3, "three preregistered controls fail in the same direction: a published refutation",
    1, "incremental",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("Z-CROSSOVER", [23626924], 23626924, A, "Recombination does not help: kernel-gated crossover measurement",
  S(2, f"{ZI} 23626924: per-declaration axiom line, whitelist free of sorryAx",
    1, "no independent audit",
    2, "18 files: code, tests, result JSONs",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "published null; nothing survives multiple-comparison correction",
    1, "incremental",
    2, "a measured 'no' about a popular AI idea"),
  lesson=True)

Z("Z-KGE", [23640856], 23640856, A, "Kernel-Gated Evolution (KGE): foundation paper and Rust implementation",
  S(2, f"{ZI} 23640856: obligations proved with an axiom dependency free of sorryAx; whitelist only",
    1, "'an internal review'",
    2, "45 files: Rust ladders, result JSONs, Lean",
    2, "inventory flags lean + numerics: 3 pillars",
    2, "each mechanism 'earned its place under measurement' (caveats)",
    2, "a new search method",
    2, "evolution-inspired AI search judged by a proof checker"))

Z("ED-09", [23646103], 23646103, P, "The bilayer dipolar-exciton interaction is completely monotone",
  S(3, f"{RP}: Autoresearch.DipolarExciton, DipolarExcitonMultipolar, DipolarExcitonStep1 replayed rc 0",
    3, "papers/ar_dipolar_exciton/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor recompiled, re-ran the gate and an independent Epstein-sum check (AUDIT.md, audit/)",
    3, "physics + mathematics + CVODE numerics + formal: 4 pillars",
    2, "corollaries conditional on the upstream AI-generated theorem; CVODE is Tier X",
    2, "a new admissibility result",
    2, "excitons in stacked 2D materials should crystallise in triangles"))

Z("ED-10", [23646105], 23646105, P, "The triangular lattice minimises the planar Yukawa energy",
  S(3, f"{RP}: Autoresearch.Yukawa and YukawaMix replayed rc 0",
    3, "papers/ar_yukawa_crystal/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor recompiled with the pinned Lean (AUDIT.md section 1)",
    3, "physics + mathematics + CVODE numerics + formal: 4 pillars",
    3, "publishes the exact-potential fix of the shifted-force erratum of 23293429 (registry ED-10)",
    2, "a new corollary family",
    2, "dusty plasmas and colloids form triangular crystals"))

Z("ED-11", [23646107], 23646107, P, "The Rytova-Keldysh interaction is a positive Gaussian mixture",
  S(3, f"{RP}: Autoresearch.KeldyshCM replayed rc 0",
    3, "papers/ar_keldysh_tmd/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "'the numerics are bit-identical on rerun' (AUDIT.md)",
    3, "physics + mathematics + numerics + formal: 4 pillars",
    2, "Struve link Tier C; producer and verifier not separated at paper stage (registry caveat)",
    2, "a new admissibility result",
    2, "the force between charges in atomically thin semiconductors"))

Z("ED-12", [23646111], 23646111, M, "Cutoff-independent enstrophy bound for the sigma = 3 dispersive shell model",
  S(2, f"Lean axiom-checked on the QuantumFluids stack; no replay record for that stack ({TS})",
    3, "papers/ar_sigma3_enstrophy/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "'a full rerun of the numerics gives a bit-identical summary' (AUDIT.md)",
    2, "mathematics + formal + numerics (domain mathematics): 3 pillars",
    2, "conditional: existence of solutions is a hypothesis",
    1, "a specialisation of an existing owner lemma (registry caveat)",
    1, "abstract for a non-specialist"))

Z("ED-13", [23646117], 23646117, P, "Bogoliubov structure factor under the dual-scale envelope",
  S(2, f"no replay record for the QuantumFluids stack ({TS})",
    3, "papers/ar_bogoliubov_sk/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor recompiled, own planted sorry caught (AUDIT.md section 1)",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    2, "says no high-frequency S(k) dataset exists; the test is one-sided",
    1, "superseded by the diffraction test of 23653846",
    1, "abstract for a non-specialist"),
  exclusion="exclusion test: 23653846 refutes the envelope as a bound for real He-4 in the roton region, but this record's central claims are Lean shape theorems and a test that stayed silent; not withdrawn or refuted, so eligible")

Z("ED-14", [23653827], 23653827, M, "Sandier-Serfaty triangular-lattice claim: reproduction and audit (no proof claimed)",
  S(3, f"{RP} (final, 93 rows): Programmes.SandierSerfatyStatement replayed rc 0 (source sha256 35add509 = the published file, publication_meta.json); the LeanFlow data certificate (SSA-A-0007) is not in the replay, and the reproduced certificate is upstream's own code, not an independent checker",
    3, "papers/prog_sandier_serfaty_audit/AUDIT.md (3 blocking corrections, incl. a fail-open LeanFlow defect) + REVISION.md",
    3, "certificate re-run reproduced in 478 s with untouched sources; the auditor traced every number (AUDIT.md; memory programmes-workflow-2026-10-25.md)",
    2, "mathematics + formal + numerics (domain mathematics): 3 pillars",
    2, "'does not prove, verify or refute that claim'",
    3, "its fail-closed LeanFlow data-certificate generator is reused unmodified by 23655392 (registry ED-20); its reproduction underlies 23655002 and 23656804",
    3, "checking an AI-generated proof claim before anyone relies on it"))

Z("ED-15", [23653833], 23653833, P, "Does the triangular lattice minimise the harmonic zero-point energy? (numerical counterexample)",
  S(3, f"{RP} (final, 93 rows): Programmes.ZeroPoint.Basic replayed rc 0 (source sha256 7d59f181 = the published file, publication_meta.json); the 8 Tier A rows certify none of the E_zp statements, the headline is Tier X",
    3, "papers/prog_zero_point_optimality/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor's fifth, real-space implementation reproduces E_zp to about 1e-12 (AUDIT.md)",
    3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "a published counterexample: QU-1 fails for 8 of 12 potentials",
    2, "a new counterexample",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("ED-16", [23653842], 23653842, M, "Completely monotone and Bernstein functions in Lean 4",
  S(3, f"{RP}: Programmes.CompletelyMonotone.* replayed rc 0",
    3, "papers/prog_cm_bernstein_library/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "byte-identical rebuild of all 11 files and Tier X numbers (AUDIT.md)",
    1, "mathematics + formal (numerics flag no): 2 pillars",
    2, "not Mathlib-ready; no PR opened",
    2, "a new library with a general subordination theorem",
    1, "abstract for a non-specialist"))

Z("ED-17", [23653846], 23653846, P, "Feynman-Bijl single-mode bound in Lean and a diffraction test on He-4 data",
  S(3, f"{RP}: Programmes.FeynmanBijl.Basic replayed rc 0",
    3, "papers/prog_superfluid_structure_factor/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "independent recompile with a private olean build; He-4 numbers re-derived (AUDIT.md)",
    3, "physics + mathematics + formal + data analysis/numerics: 4 pillars",
    3, "a published refutation: He-4 data refute the Bogoliubov envelope at all 21 roton-region points",
    2, "a new formalization and test",
    2, "superfluid helium measured with neutrons tests a textbook formula"))

Z("ED-18", [23653850], 23653850, G, "Fixation probabilities as absorption limits, kernel-checked (Wright-Fisher, Moran, Price)",
  S(3, f"{RP}: Programmes.PopGen.* replayed rc 0",
    3, "papers/prog_population_genetics_fixation/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the CVODE run reproduces byte for byte; 14 Tier A rows recompiled (AUDIT.md)",
    3, "biology + mathematics + CVODE numerics + formal: 4 pillars",
    2, "textbook results newly kernel-checked; the path-measure identification is Tier C",
    3, "Absorption and MoranModel are reused by 23660071 (EvoGraph imports PopGen; papers/p3_isothermal_theorem/AUDIT.md)",
    2, "the chance that a new mutation takes over a population"))

Z("ED-19", [23655002], 23655002, P, "Can the planar Sandier-Serfaty architecture reach 3D bcc jellium? (negative)",
  S(1, "Tier C obstruction argument + floating-point numerics; registry ED-19 lists no Lean file",
    3, "papers/p2_3d_feasibility/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "cheap numerics reproduce byte for byte; the auditor ran the missing rotation control (AUDIT.md)",
    3, "inventory flags physics + lean + numerics: 4 pillars",
    3, "a published negative feasibility result",
    1, "incremental",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("ED-20", [23655392], 23655392, P, "The triangular lattice is not a local minimum of zero-point energy for exp(-pi r^2)",
  S(3, "papers/p3_zero_point_physical/data/leanchecker_replay.json: Programmes.ZeroPointCert.Basic replayed by leanchecker rc 0; the integrals are ball arithmetic outside the kernel",
    3, "papers/p2_certified_zero_point/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the certificate keeps its sign when re-run with coarser cells; an independent float reimplementation agrees (AUDIT.md)",
    3, "physics + mathematics + formal + certified numerics: 4 pillars",
    3, "a certified counterexample",
    2, "a certified linear-response method",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("ED-21", [23655625], 23655625, P, "Triangular-to-oblique instability of the quantum Gaussian-core crystal (negative)",
  S(0, f"{ZI} 23655625: 'Tier X (floating point; nothing here is a proof)'",
    3, "papers/p2_quantum_transition/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "headline numbers reproduce with the auditor's own code (AUDIT.md)",
    1, "physics + numerics (lean flag no): 2 pillars",
    3, "a preregistered negative result",
    1, "incremental",
    1, "abstract for a non-specialist"),
  lesson=True)

Z("ED-22", [23656804], 23656804, M, "Toward a machine-checked Sandier-Serfaty certificate: 4 of 12 stages in the Lean kernel",
  S(3, f"{RP} (final, 93 rows; CalcLamE9 and CalcLamF0-F9 were not yet in the 71-row snapshot): Programmes.SandierSerfaty.CalcK*/CalcLam* replayed rc 0; the auditor's rebuilt oleans are byte-identical (AUDIT.md)",
    3, "papers/p2_sandier_serfaty_lean/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor rebuilt a sample independently with byte-identical oleans (AUDIT.md)",
    2, "mathematics + formal + numerics (domain mathematics): 3 pillars",
    2, "partial: 4 of 12 stages; 'the conjecture is not formally proved'",
    2, "a decide_kernel tactic and a measured cost",
    2, "checking an AI proof step by step, with its measured cost"))

Z("ED-23", [23660071], 23660071, G, "The isothermal theorem of evolutionary graph theory, kernel-checked",
  S(3, "papers/p3_isothermal_theorem/AUDIT.md: the auditor ran a leanchecker kernel replay (rc 0); EvoGraph modules rc 0 in replay.jsonl",
    3, "papers/p3_isothermal_theorem/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "the auditor recompiled and recomputed every number with its own exact-rational script (AUDIT.md)",
    3, "biology + mathematics + formal + exact numerics: 4 pillars",
    3, "reports that its own preregistered 'birth-death chain' clause was false (registry ED-23)",
    2, "a newly kernel-checked theorem",
    2, "which network shapes help or hinder natural selection"))

Z("ED-24", [23661381], 23661381, M, "Independent rebuild, kernel replay and audit of openai/NavierStokesAndEuler",
  S(3, f"{ZI} 23661381: 88,400 declarations replayed in the kernel (leanchecker, papers/p2_navier_stokes_audit/AUDIT.md toolchain); no soundness escape",
    3, "papers/p2_navier_stokes_audit/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md",
    3, "every technical claim reproduced with the auditor's own scripts (AUDIT.md)",
    1, "mathematics + formal (numerics flag no): 2 pillars",
    2, "'not a claim that a Clay problem is solved'; fidelity reported with a caveat",
    2, "a full independent rebuild",
    3, "an independent check of an AI lab's claimed proof on a famous prize problem"))

Z("Z-HIVEMIND", [23649757], 23649757, A, "Project HiveMind: decentralized sparse MoE training on 8 GB GPUs",
  S(1, f"{ZI} 23649757: 128 Lean theorems 'compile without sorry' (bookkeeping), no axiom statement",
    1, "no independent audit",
    2, "99 files incl. T4_REPLICATION_KIT.md, preregistration JSONs, raw results",
    2, "inventory flags lean + numerics: 3 pillars",
    3, "withdraws the verdicts of rows whose negative control failed",
    2, "a new system design",
    2, "training AI on cheap volunteer GPUs"),
  repos=["HiveMind"], merge="repo HiveMind is this record's code home")

N2_ID = 23663551
Z("N2", [N2_ID], N2_ID, P, "The triangular lattice is not a local minimum of zero-point energy for planar Yukawa kappa = 1, 2 (N2)",
  S(3, "papers/p3_zero_point_physical/data/leanchecker_replay.json: ZeroPointPhys.Taylor and Basic replayed rc 0; the headline also uses ball arithmetic outside the kernel",
    3, "papers/p3_zero_point_physical/AUDIT.md ACCEPT_WITH_CORRECTIONS + REVISION.md (12 items)",
    3, "'two runs reproduce bit for bit (Gaussian a = 2 and Yukawa kappa = 2)' (AUDIT.md)",
    3, "physics + mathematics + formal + certified numerics: 4 pillars",
    3, "a certified negative result: classically optimal, not zero-point optimal",
    2, "a moving comparison matrix with exact curvature",
    1, "abstract for a non-specialist"),
  lesson=True, merge="not in the inventory (published after it was fetched); added from papers/p3_zero_point_physical/ (zenodo_doi.txt, AUDIT.md, REVISION.md, ledger gate exit 1)")

# ---------------------------------------------------------------- GitHub repositories not represented by a Zenodo work
R("G-AUTOEVOLVE", ["AutoevolveAI"], "AutoevolveAI / ANSE: verification-first harness for LLM-agent science",
  S(1, "github AutoevolveAI: a harness; claims about it are human argument; its only sound Lean gate is lean_runner.py (memory verification-traps.md)",
    1, "internal audits docs/remediation/AUDIT_2026-09-25.md and -26.md (honesty_files)",
    1, "public code (1,004 .py files)",
    2, "Lean (164 files) + Rust/numerics: mathematics, formal, numerics = 3 pillars",
    3, "README publishes that an internal audit found 14 components reporting success without doing the work",
    3, "hosts lean_pinned.py, the ledger gate and the publish scripts used by every programme paper (papers/*/ledger, memory)",
    3, "a test bench built so that wrong AI claims fail"))

R("G-RUSTY", ["rusty-SUNDIALS"], "rusty-SUNDIALS: AI-assisted pure-Rust translation of SUNDIALS CVODE",
  S(0, "its numerics are Tier X by the Elenchus rule; its Lean specification files include vacuous axioms (memory openai-math-crosswalk.md)",
    3, "PR #60 (merged 2026-09-27) adds the separate agents' audit docs/audit/fusion-2026-09-27/{A_paper_claims,B_numerics,C_lean_provenance}.md and RETRACTION_NOTICE.md, with the retractions applied (gh pr view 60; memory fusion-project-audit.md)",
    3, "non-producer auditors re-ran its CVODE runs with byte-identical output (papers/prog_population_genetics_fixation/AUDIT.md; papers/ar_sigma3_enstrophy/AUDIT.md)",
    2, "numerics + Lean specs: mathematics, formal, numerics = 3 pillars",
    3, "PR #60 publishes an audit with retractions of fusion claims (memory fusion-project-audit.md)",
    3, "the numerics backbone of 23293429, 23646103/05/07/11 and 23653850 (registry code fields)",
    2, "open stiff-ODE solver used for plasma and population models"))

R("G-MIRROR", ["Mirror-Map-Sieve"], "Mirror-Map-Sieve: an Apery-like sum and a possible Calabi-Yau reading",
  S(1, "github summary: exploratory pipeline, Lean files without an axiom report", 0, "no audit",
    1, "public code", 2, "mathematics + formal + numerics: 3 pillars",
    2, "README: 'We do not claim a discovery'", 1, "exploratory", 1, "abstract for a non-specialist"))
R("G-CYCLO", ["OpenCycloInitiative"], "OpenCycloInitiative: open algae photobioreactor design documents",
  S(0, "design documents only", 0, "no audit", 0, "no code (documentation-level)", 0, "biology only: 1 pillar",
    1, "no caveat", 1, "design notes", 2, "an open algae bioreactor for local production"))
R("G-OPTENERGY", ["OptimalEnergyAI"], "OptimalEnergyAI: triangular-lattice optimality as latent geometry for ML (private)",
  S(1, "Lean spec, no axiom report in the inventory", 0, "no audit", 0, "PRIVATE repo: not available to readers",
    2, "mathematics + formal + CPU experiments: 3 pillars", 2, "'no real-data PoC yet'", 1, "early",
    1, "abstract for a non-specialist"))
R("G-CK8D", ["SocrateAI-CohnKumar-8D-Numeric"], "SocrateAI-CohnKumar-8D-Numeric (empty)",
  S(0, "empty repository", 0, "none", 0, "no content", 0, "none", 1, "no caveat", 0, "no content", 0, "none"))
R("G-LEANLIB", ["SocrateAI-Lean-Lib"], "SocrateAI-Lean-Lib: 14-domain Lean library with an axiom-audit report",
  S(2, "docs/AXIOM_AUDIT_REPORT.md (honesty_files)", 1, "the author's own axiom report", 1, "public code",
    1, "mathematics + formal: 2 pillars", 1, "'zero axioms' checks are theorems about specific numbers, not flagged as such",
    1, "incremental", 0, "none stated"))
R("G-LEANVERIF", ["SocrateAI-Lean-Verification"], "SocrateAI-Lean-Verification (private, tensor rank)",
  S(1, "Lean files, no axiom report", 0, "no audit", 0, "PRIVATE repo", 1, "mathematics + formal: 2 pillars",
    1, "no caveat", 1, "single commit", 0, "none stated"))
R("G-AGORA-WS", ["SocrateAI-Scientific-Agora", "SocrateAI-Scientific-NewDiscoveries"],
  "SocrateAI Agora / NewDiscoveries multi-agent workspace (private)",
  S(1, "workspace; Lean files without an axiom report in the inventory", 1, "holds the registry of audited programme DOIs (NewDiscoveries REGISTRY.json)",
    0, "PRIVATE repos", 2, "Lean + Rust + numerics: 3 pillars", 2, "registry records caveats per DOI",
    2, "hosts the Elenchus discoveries registry", 1, "infrastructure"),
  merge="identical metrics; probably the same repository under two names (github summary)")
R("G-CINETIQUE", ["SocrateAI-Scientific-Agora-Physique-Cinetique"], "Physique-Cinetique: exact-rational kinetic response engine, with retractions",
  S(1, "Lean (6 files) and exact rational engine, no axiom report", 1, "two audits (AUDIT_SUMMARY.md, SCIENTIFIC_AUDIT_REPORT.md), auditor not identified",
    1, "public code", 3, "physics + mathematics + formal + numerics: 4 pillars",
    3, "RETRACTIONS; an audit exposed a 'fabricated phantom simulation' and a stub kernel (github lessons)",
    1, "incremental", 1, "abstract for a non-specialist"),
  lesson=True)
R("G-RAMANUJAN", ["SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic"], "RamanujanNeuroSymbolic: automated pipeline on mock modular forms",
  S(1, "4,471 Lean files, likely generated; no axiom report", 0, "no audit", 1, "public code",
    1, "mathematics + formal: 2 pillars", 1, "no caveat", 1, "generated pipeline", 0, "none stated"))
R("G-ALIEN", ["SocrateAI-Scientific-AlienMathematics-Foundation"], "AlienMathematics-Foundation: retrospective of a failed AI-driven exploration",
  S(1, "human retrospective", 1, "self-assessment", 1, "public code (16 Lean files)",
    1, "mathematics + formal: 2 pillars", 3, "'an honest account ... its failures': 6 methods failed where a decomposition is known (github lessons)",
    1, "retrospective", 2, "what AI exploration of mathematics looks like when it mostly fails"),
  lesson=True)
R("G-AUTOEVOLVE-K3", ["SocrateAI-Scientific-AutoEvolve-K3xT2"], "AutoEvolve-K3xT2: evolutionary cosmology search, with a NANOGrav refutation",
  S(1, "7 Lean files, no axiom report", 1, "internal PEER_REVIEW_AUDIT_REPORT.md", 1, "public code",
    3, "cosmology + mathematics + formal + numerics: 4 pillars",
    3, "records a decisive NANOGrav refutation (lnB = -51.58) of one spectrum (github lessons)",
    1, "incremental", 2, "a candidate signal checked against pulsar-timing data"),
  lesson=True)
R("G-COMM", ["SocrateAI-Scientific-Communication"], "Scientific-Communication: papers with the reviews that examined them",
  S(0, "documents only", 1, "reviews collected by the author", 0, "no code", 0, "1 pillar",
    3, "keeps visible a 'first Lean 4 formalization' claim that 'was false, and it was refuted' (github lessons)",
    1, "a curation", 2, "showing readers which claims did not survive"),
  lesson=True)
R("G-CMT", ["SocrateAI-Scientific-CondensedMatterTheory"], "CondensedMatterTheory: AdS/CMT literature review with Lean offsets",
  S(1, "Lean offsets file with an explicit 'not proved' section", 0, "no audit", 1, "public code",
    3, "physics + mathematics + formal + numerics: 4 pillars", 2, "'not proved' section", 1, "literature review",
    1, "abstract for a non-specialist"))
R("G-FUSION-EMPTY", ["SocrateAI-Scientific-FusionEnergy"], "SocrateAI-Scientific-FusionEnergy (empty)",
  S(0, "empty repository", 0, "none", 0, "no content", 0, "none", 1, "no caveat", 0, "no content", 0, "none"))
R("G-MATHESIS", ["SocrateAI-Scientific-Mathesis"], "Mathesis: shared notation, verification kernel and epistemic ledger (Stream 0)",
  S(1, "Lean files, no axiom report in the inventory", 1, "AUDIT_PACK.md by the author", 1, "public code",
    2, "mathematics + formal + numerics: 3 pillars", 2, "'a statement can be non-vacuous ... and still be the wrong statement'",
    2, "an early epistemic ledger", 1, "abstract for a non-specialist"))
R("G-POLY", ["SocrateAI-Scientific-Poly-Algebraic-Calculus"], "Poly-Algebraic-Calculus (placeholder)",
  S(0, "abstract only", 0, "none", 0, "no code", 0, "none", 1, "no caveat", 0, "placeholder", 0, "none"))
R("G-QC", ["SocrateAI-Scientific-QuantumComputing"], "QuantumComputing stream ('prepared, not implemented')",
  S(0, "not implemented", 0, "none", 0, "no implementation", 0, "none", 2, "README: 'prepared, not implemented'", 0, "nothing built", 0, "none"))
R("G-TNN", ["SocrateAI-Scientific-TNN-UniversModel"], "TNN-UniversModel: tensor-NN universe model with a real-data registry",
  S(1, "Lean files, no axiom report", 1, "the author's 'certified audit'", 1, "public code",
    2, "mathematics + formal + numerics: 3 pillars", 3, "the audit renamed over-claimed items ('Live Sonic Horizon Simulator' became a 1D advection-diffusion proxy)",
    1, "incremental", 1, "abstract for a non-specialist"),
  lesson=True)
R("G-WOLFRAM", ["SocrateAI-Wolfram-Hypergraph"], "Wolfram-Hypergraph: computation-augmented generation for hypergraph cosmology",
  S(1, "Lean files, no axiom report", 1, "an audit brief by the author", 1, "public code",
    3, "cosmology + mathematics + formal + numerics: 4 pillars", 2, "'does not claim to have discovered particles'",
    1, "proof of concept", 1, "abstract for a non-specialist"))
R("G-THESIS", ["SocrateAI-thesisautoresearch"], "thesisautoresearch: DBA thesis copilot (private)",
  S(1, "Lean/Z3 tracks, no axiom report", 0, "no audit", 0, "PRIVATE repo", 2, "Lean + Z3 + RAG: 3 pillars counted as mathematics, formal, numerics",
    1, "no caveat", 1, "a copilot", 1, "thesis support"))
R("G-SUPERGRAVITY", ["SuperGravity"], "SuperGravity: zero-trust gateway for agentic coding",
  S(1, "Lean files, no axiom report", 0, "no audit", 1, "public code", 1, "mathematics + formal: 2 pillars",
    1, "no caveat", 1, "built on AutoevolveAI", 1, "safer AI coding agents"))
R("G-EXOPLANET", ["TIC4206066-Exoplanet-Verification"], "TIC 4206066 b: independent adversarial re-analysis of an exoplanet candidate",
  S(1, "two Lean files, no axiom report in the inventory", 1, "METHOD_AUDIT.md by the author", 2, "a Zenodo-ready data package with environment freezes and logs (honesty_files)",
    3, "astrophysics + mathematics + formal + numerics: 4 pillars", 2, "refutation gates with positive and negative controls stated",
    2, "refutation gates applied to someone else's candidate", 2, "checking another team's planet claim before believing it"))
R("G-UNIVERSCRAFT", ["Universcraft"], "Universcraft: Rust procedural rendering engine",
  S(0, "software with physics-flavoured claims", 1, "Lab-5 audit memo by the author", 1, "public code", 0, "numerics only: 1 pillar",
    1, "no caveat", 1, "not a research result", 1, "a rendering engine"))
R("G-AMCP", ["amcp", "amcp-v1.5-opensource"], "AMCP: agent mesh communication protocol (Java)",
  S(0, "a framework; status files report tests", 0, "none", 1, "public code", 0, "1 pillar", 1, "no caveat", 1, "framework",
    1, "agent infrastructure"), merge="enterprise and open-source editions of the same framework")
R("G-ATTENTION", ["attentionmatter"], "attentionmatter: prompt-token reduction proof of concept (private)",
  S(0, "README claims 30-56% reduction, not checked", 0, "none", 0, "PRIVATE repo", 0, "1 pillar", 1, "no caveat", 1, "proof of concept", 1, "cheaper prompts"))
R("G-NSYMBO", ["nSymboCoder"], "nSymboCoder: sub-1B neuro-symbolic code-model concept (private)",
  S(0, "concept only", 0, "none", 0, "PRIVATE, one commit", 0, "none", 1, "no caveat", 0, "concept", 0, "none"))
R("G-LEVELDB", ["rusty-leveldb"], "rusty-leveldb: Rust LevelDB port (fork-derived)",
  S(0, "not science", 0, "none", 1, "public code", 0, "1 pillar", 1, "no caveat", 0, "derived from a fork", 0, "none"))
R("G-XAURA", ["xAuraOS"], "xAuraOS: local-first governed agent runtime",
  S(0, "runtime software", 1, "DEEP_AUDIT_REPORT.md by the author", 1, "public code", 0, "1 pillar", 2, "carries its own deep audit",
    1, "a runtime", 1, "agent infrastructure"))
R("G-FLUIDMEC", ["xaviercallens-SocrateAI-Scientific-FluidMecanism"], "FluidMecanism (empty placeholder)",
  S(0, "empty", 0, "none", 0, "no content", 0, "none", 1, "no caveat", 0, "placeholder", 0, "none"))


def created(c: dict[str, Any]) -> str:
    if c["source"] == "github":
        return GBY[c["repos"][0]]["created"]
    if c["primary"] == N2_ID:
        return "2026-10-26T10:50:08"  # mtime of papers/p3_zero_point_physical/zenodo_doi.txt (DOI minted)
    return ZBY[c["primary"]]["created"]


def check_coverage() -> None:
    zids = [m for c in CANDS for m in c["members"] if m != N2_ID]
    assert len(zids) == len(set(zids)), "a Zenodo record is in two candidates"
    missing = set(ZBY) - set(zids)
    extra = set(zids) - set(ZBY)
    assert not missing and not extra, (sorted(missing), sorted(extra))
    reps = [r for c in CANDS for r in c["repos"]]
    assert len(reps) == len(set(reps)), "a repo is in two candidates"
    assert set(reps) == set(GBY), (sorted(set(GBY) - set(reps)), sorted(set(reps) - set(GBY)))


def total(c: dict[str, Any]) -> int:
    return sum(v["score"] for v in c["scores"].values())


def rank_key(c: dict[str, Any]) -> tuple[int, int, int, str]:
    s = c["scores"]
    return (-total(c), -s["c1_rigour"]["score"], -s["c2_independent_check"]["score"], created(c))


def select(ranked: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Hard rules: domain minimums (2 each), lessons (>= 3), cap 7 per domain, then fill in rank order."""
    log: list[str] = []
    picks: list[dict[str, Any]] = []

    def count(dom: str) -> int:
        return sum(1 for p in picks if p["domain"] == dom)

    for dom in MIN_DOMAINS:
        for c in [c for c in ranked if c["domain"] == dom][:2]:
            if c not in picks:
                picks.append(c)
                log.append(f"reserve (domain minimum, {dom}): {c['id']} total {total(c)}, pure rank {ranked.index(c) + 1}")
    for c in ranked:
        if sum(1 for p in picks if p["lesson"]) >= 3:
            break
        if c["lesson"] and c not in picks and count(c["domain"]) < 7:
            picks.append(c)
            log.append(f"reserve (lessons >= 3): {c['id']} total {total(c)}, pure rank {ranked.index(c) + 1}")
    for c in ranked:
        if len(picks) >= 20:
            break
        if c in picks:
            continue
        if count(c["domain"]) >= 7:
            log.append(f"skip (cap 7 for {c['domain']}): {c['id']} total {total(c)}, pure rank {ranked.index(c) + 1}")
            continue
        picks.append(c)
    picks.sort(key=lambda c: ranked.index(c))
    return picks, log


def main() -> None:
    check_coverage()
    ranked = sorted(CANDS, key=rank_key)
    picks, log = select(ranked)
    pure = ranked[:20]
    harness = {"G-AUTOEVOLVE", "G-RUSTY"}
    cf_picks, _ = select([c for c in ranked if c["id"] not in harness])
    counterfactual = {
        "question": "selection if the harness repos AutoevolveAI and rusty-SUNDIALS were treated as represented by the Zenodo works whose code they host",
        "selected": [c["id"] for c in cf_picks],
        "enter": [c["id"] for c in cf_picks if c not in picks],
        "leave": [c["id"] for c in picks if c not in cf_picks],
    }
    rows = []
    for i, c in enumerate(ranked, 1):
        p = c["primary"]
        rows.append({
            "rank": i, "id": c["id"], "title": c["title"], "domain": c["domain"], "source": c["source"],
            "primary_doi": (f"10.5281/zenodo.{p}" if p else None),
            "member_dois": [f"10.5281/zenodo.{m}" for m in c["members"]],
            "repos": [{"name": r, "visibility": GBY[r]["visibility"]} for r in c["repos"]],
            "created": created(c), "lesson": c["lesson"], "total": total(c), "scores": c["scores"],
            "merge_note": c["merge_note"], "exclusion_note": c["exclusion_note"],
            "selected": c in picks, "in_pure_top20": c in pure,
        })
    (OUT / "scores_final.json").write_text(json.dumps({
        "rubric": "results/discovery_journal_2026/RUBRIC.md (frozen 2026-10-26)",
        "n_candidates": len(rows), "selection_log": log,
        "pure_top20": [c["id"] for c in pure], "selected": [c["id"] for c in picks],
        "counterfactual_harness_repos": counterfactual,
        "candidates": rows}, indent=1, ensure_ascii=False))
    print(len(rows), "candidates")
    for r in rows[:40]:
        print(r["rank"], r["id"], r["domain"], r["total"], [v["score"] for v in r["scores"].values()],
              "SEL" if r["selected"] else "", "pure" if r["in_pure_top20"] else "", "L" if r["lesson"] else "")
    print("\n".join(log))
    doms: dict[str, int] = {}
    for c in picks:
        doms[c["domain"]] = doms.get(c["domain"], 0) + 1
    print(doms, "lessons", sum(1 for c in picks if c["lesson"]))
    print("counterfactual", counterfactual["enter"], counterfactual["leave"])


if __name__ == "__main__":
    main()
