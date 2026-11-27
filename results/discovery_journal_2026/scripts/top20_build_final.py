"""Write TOP20.json and SELECTION.md from scores.json (run score_build.py first).

The plain-language text below is hand-written per pick; every number in it is taken from the
records cited in scores.json. Run: .venv/bin/python -I results/discovery_journal_2026/scripts/top20_build.py
"""

import json
from pathlib import Path
from typing import Any

OUT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/discovery_journal_2026")
SC = json.loads((OUT / "scores_final.json").read_text())
ROWS = {r["id"]: r for r in SC["candidates"]}

ARC = {
    "P1": "Phase 1 (May-Aug): agents and over-claims",
    "P2": "Phase 2 (Sep 1-28): the formal turn and the first public corrections",
    "P3": "Phase 3 (Oct 1-11): Elenchus in practice: certified numerics and the openai/math corollaries",
    "P4": "Phase 4 (Oct 17-21): relapse and withdrawal",
    "P5": "Phase 5 (Oct 23-26): the kernel-checked programme with independent audits",
}

PROSE: dict[str, dict[str, str]] = {
    "Z-BAO-P1": {
        "what": "Astronomers measure the distances to very far galaxies with a 'standard ruler' left in the early universe (baryon acoustic oscillations). Turning a measurement into a distance needs an integral that a computer only approximates. Here a fast solver produced the numbers together with a table of whole-number checks, and the Lean proof checker then confirmed, step by step, that the true distance lies inside a narrow interval (relative width about 0.03%) at each of DESI's seven redshifts. Caveats: it is done at one value of the matter density, the project's own fit and not DESI's; it certifies a calculation, not a new measurement; the audit was by an AI agent, not a person.",
        "analogy": "A shop's till total re-added receipt by receipt by an auditor who trusts only pencil and paper.",
        "checked": "Elenchus Tier A: the Lean kernel re-checks the untrusted solver's integer table (decide +kernel, no native_decide), 55 theorems with only the three standard axioms; an independent AI verifier recompiled everything (CONFIRMED_WITH_CORRECTIONS). The solver values themselves stay Tier X.",
        "arc": "P3",
        "arc_role": "Numerics explore, Lean judges: the first time a simulator's own output became a kernel-checked statement. The integer-certificate method was reused at once in P2/P3.",
    },
    "Z-BAO-P23": {
        "what": "Two families of measurements of how fast the universe expands disagree (the 'Hubble tension'; the local, distance-ladder side sits near 73 km/s per megaparsec, the threshold this paper tests). Combining DESI distance data with what the first minutes of the universe tell us about light elements, this paper proves with Lean that, inside the standard flat model and its stated simplifications (radiation ignored, a fitting formula for the ruler, Gaussian errors), every expansion rate of 73 or more fits the data far worse than the best fit. It also certifies which matter densities are excluded. This is a certified version of a tension already known from ordinary statistics, not a new measurement; one pre-planned way of slicing the calculation failed and was replaced, and the paper says so.",
        "analogy": "Checking that a radio picks up no station anywhere on the dial above 73, band by band, with a notary signing each band.",
        "checked": "Elenchus Tier A for the bounds (kernel-checked interval evaluation, axiom audit controls); two independent AI verifiers (CONFIRMED_WITH_CORRECTIONS), with 3 of 29 slab files rebuilt by the P2 verifier.",
        "arc": "P3",
        "arc_role": "The same method scaled from one distance to a whole likelihood: a famous open puzzle stated as a kernel-checked inequality.",
    },
    "Z-UO-TIERED": {
        "what": "In September 2026 OpenAI released an AI-generated, computer-checked proof that, for a broad family of repulsive forces, the triangular arrangement has the lowest energy of all ways to place points on a plane at a given density. This paper derives consequences in Lean (for instance that the optimum is not unique: removing one point changes neither the density nor the energy), and checks one physical case, particles with a screened (Yukawa) repulsion, with an N-body simulation. Caveats, all stated: everything rests on the AI-generated upstream theorem, whose statement no person has audited; the simulation's cut-off of the force shifted energies by more than the gap being measured (an erratum fixed later in 10.5281/zenodo.23646105); simulated annealing failed to find the lattice at the weaker screening.",
        "analogy": "Oranges on a market stall: the proof says the neat stack is best; the simulation shakes the stall to see whether the oranges find it on their own.",
        "checked": "Elenchus ledger with 22 claims: Tier A rows kernel-checked and replayed (rc 0 on 2026-10-26), CVODE numerics Tier X, literature Tier L, proposals Tier C; an independent AI audit (ACCEPT_WITH_CORRECTIONS) and a re-audit. The ledger gate exits 1 because the Tier A rows lack a human statement audit; the owner published with those flags open and said so.",
        "arc": "P3",
        "arc_role": "The template of the whole loop: AI proposes (the upstream theorem), numerics explore (CVODE), Lean judges (Tier A), the human decides (publication with the flags shown).",
    },
    "ED-10": {
        "what": "Charged dust in plasmas and charged colloids repel each other with a screened (Yukawa) force. The paper proves in Lean that this force belongs to the family the upstream theorem covers, at every density and for any finite mixture of screening lengths. If the upstream AI-generated theorem is right, the triangular lattice is then the lowest-energy arrangement for these systems. It also corrects the earlier simulation erratum by using the exact, untruncated force.",
        "analogy": "Showing that a new key is cut from the same blank as keys already known to open the lock.",
        "checked": "Elenchus Tier A, replayed in the kernel (rc 0); an independent AI audit recompiled the files (ACCEPT_WITH_CORRECTIONS, revision recorded); simulations Tier X. Ledger gate exit 1: no human statement audit.",
        "arc": "P5",
        "arc_role": "A correction carried through to the end: the erratum of an earlier paper fixed in a later one, inside the same audited loop.",
    },
    "ED-17": {
        "what": "In superfluid helium, the classic Feynman-Bijl single-mode inequality bounds the energy of sound-like ripples by a quantity that neutron scattering measures (the structure factor). The paper proves that bound in Lean, then tests against published neutron data an 'envelope' formula proposed by this project earlier in the month. The data refute the envelope in the roton region (all 21 points there). One positive formal result and one negative physical result in the same paper.",
        "analogy": "Proving that your ruler is straight, then using it to show that your own earlier sketch was crooked.",
        "checked": "Elenchus Tier A for the bound (replayed, rc 0); the helium data are Tier L (a published table); the trapped-gas data were read from a figure (Tier X); an independent AI audit re-derived the numbers.",
        "arc": "P5",
        "arc_role": "Humans decide meaning: the proof stands, but measured nature overrules the project's own formula.",
    },
    "ED-18": {
        "what": "When a new mutation appears in a population, what is the chance it eventually takes over? Classic answers exist for the standard textbook models (Wright-Fisher, Moran) and for the Price equation. This work proves those classic results in Lean, as limits of many random steps, and checks them against a simulation. These are known results: what is new is that a proof checker has verified them, and the next paper reused the pieces.",
        "analogy": "Re-deriving the odds of a long dice game and having a referee check every line.",
        "checked": "Elenchus Tier A, replayed (rc 0); an independent AI audit recompiled the 14 Tier A rows and reproduced the simulation byte for byte; the link to a path measure is Tier C (stated).",
        "arc": "P5",
        "arc_role": "The method leaves physics: Elenchus applied to biology, with reusable building blocks.",
    },
    "ED-23": {
        "what": "In evolution on a network (who can replace whom), a classic theorem says that if every individual is replaced at the same overall rate, the network neither helps nor hinders natural selection: it behaves like a well-mixed population. The paper proves this in Lean for birth-death updating and a generalisation, and reports openly that one of its own pre-registered sub-claims was false. The converse direction and other update rules are not proved.",
        "analogy": "If every seat at a card table is refilled equally often, the seating plan does not change who tends to win.",
        "checked": "Elenchus Tier A: the auditor recompiled from source, ran its own axiom audit and a kernel replay with leanchecker (rc 0), and planted errors that were caught; exact-rational numerics Tier X.",
        "arc": "P5",
        "arc_role": "Reuse and humility in one paper: it imports the previous paper's Lean, and it records its own pre-registration error.",
    },
    "Z-UO-BOOK": {
        "what": "A 105-page textbook for students that follows one theorem, that the triangular arrangement has the least energy, from its definitions to the laboratory. Each result appears three times: as a step-by-step human proof, as a Lean statement and as Python and Rust tests. Five chapters were written independently from one shared fact sheet and then audited as a whole (20 fixes). The source theorem is AI-generated and not peer reviewed, and the book inherits the simulation erratum noted above.",
        "analogy": "A cookbook in which every recipe comes with a photo, a lab analysis and a tasting.",
        "checked": "New Lean content (open versus closed disks) recompiled by an independent verifier and replayed (rc 0); whole-book AI audit; no ledger of its own.",
        "arc": "P3",
        "arc_role": "Humans decide meaning: the method turned into teaching, with its limits printed inside.",
    },
    "ED-09": {
        "what": "Excitons are bound pairs of an electron and a hole; in stacked two-dimensional materials they line up as tiny dipoles that repel each other. The paper proves in Lean that this bilayer repulsion has the technical property ('complete monotonicity') the upstream theorem needs, so the triangular lattice is optimal at every density, conditional on the AI-generated upstream theorem. A simulation with exact long-range sums is a consistency check, not a proof.",
        "analogy": "Checking that a new ingredient meets the label rules, so that an existing guarantee on the recipe applies to it.",
        "checked": "Elenchus Tier A, replayed (rc 0); independent AI audit with its own recompilation and an independent numerical check; simulation Tier X.",
        "arc": "P5",
        "arc_role": "AI proposes a physical application, Lean checks the hypothesis, numerics stay advisory.",
    },
    "ED-11": {
        "what": "In atomically thin semiconductors the force between charges is not the usual Coulomb law but the Rytova-Keldysh law, because the thin layer screens it. The paper shows that this force is a positive mixture of bell-shaped (Gaussian) pieces, which makes it admissible for the upstream optimality theorem; the admissibility step is in Lean. One identification with a classical special-function form is a human argument only, and producer and verifier were not separated at the paper stage.",
        "analogy": "Showing that a complicated sound is a sum of pure tones, each of which a known rule already covers.",
        "checked": "Elenchus Tier A for admissibility (replayed, rc 0), Tier C for the Struve-form link; independent AI audit found the numerics bit-identical on rerun.",
        "arc": "P5",
        "arc_role": "The tiers kept apart inside one result: what the kernel checked and what a human argued are labelled differently.",
    },
    "ED-15": {
        "what": "A natural guess (called QU-1 here) was that the triangular lattice, which minimises the static energy of many repulsive forces, also minimises the quantum 'zero-point' vibration energy. The paper tested the guess before trying to prove it, and it fails numerically for 8 of the 12 completely monotone forces tried: for the Gaussian exp(-pi r^2) a slightly rhombic lattice has a lower zero-point energy (by about 1.3e-2), and two formulas in four implementations agree. These are floating-point results, not a proof that the guess is false; four forces were not refuted on the points sampled, and a first-reported best competitor was only marginally stable and was corrected. The Lean part checks 19 finite and algebraic lemmas (derivatives, rotation symmetry) and certifies none of the energy statements.",
        "analogy": "Testing a promised rule on twelve cases before trying to prove it, and finding that eight of them break it.",
        "checked": "Headline Tier X (floating point, four implementations); Lean lemmas Tier A, replayed in the kernel (rc 0, final replay record); independent AI audit (ACCEPT_WITH_CORRECTIONS) reproduced the Gaussian refutations with its own real-space code; ledger gate exit 1 (no human statement audit).",
        "arc": "P5",
        "arc_role": "Numerics explore and refute first: the preregistered falsification gate that the certified counterexamples then built on.",
    },
    "ED-20": {
        "what": "A natural guess (called QU-1 here) was that the triangular lattice also minimises the quantum 'zero-point' vibration energy. For one bell-shaped repulsion the paper proves that a tiny shear of the triangular lattice lowers that energy, so the lattice is not even a local minimum. Lean holds the logic and the exact fractions; the integrals are enclosed by rigorous interval ('ball') arithmetic outside the Lean kernel.",
        "analogy": "A marble that seems to rest at the bottom of a bowl, until a gentle nudge shows it sits on a saddle.",
        "checked": "Lean part replayed in the kernel (rc 0); ball-arithmetic certificate re-run by the auditor with coarser cells (sign kept) and cross-checked by an independent floating-point code; independent AI audit.",
        "arc": "P5",
        "arc_role": "Numerics found the counterexample first (QU-1 refuted numerically); this paper upgrades it to a certified one.",
    },
    "N2": {
        "what": "The same question as the previous paper, for the screened (Yukawa) forces common in plasmas and colloids, at two screening strengths: the triangular lattice is the classical optimum (if the upstream theorem holds) but not a local minimum of the zero-point energy. A new comparison technique makes the certificate possible. Some other cases (power-law forces) remain numerical evidence only, and the paper says nothing yet about the full quantum crystal.",
        "analogy": "The best way to stack the oranges is not the calmest way to let them jiggle.",
        "checked": "Lean modules replayed by leanchecker (rc 0); ball-arithmetic integrals outside the kernel; two runs reproduced bit for bit by an independent AI audit (ACCEPT_WITH_CORRECTIONS, 12 revisions recorded); ledger gate exit 1 (no human statement audit).",
        "arc": "P5",
        "arc_role": "The last result of the year: a negative answer, certified, about the project's own question.",
    },
    "ED-14": {
        "what": "OpenAI's release also claims a proof that the triangular lattice minimises the energy of charged points in a neutralising background (the Sandier-Serfaty conjecture), through a reduction plus a large computer certificate. This work re-ran that certificate (it reproduced in about 8 minutes), checked that a deliberately broken copy is rejected, and read the reduction step by step without finding a gap. It explicitly does not prove, verify or refute the conjecture. The audit also found and fixed a hole in the project's own certificate tool.",
        "analogy": "Re-running a stranger's long sum on your own calculator and reading their reasoning line by line, while saying plainly that this is not a referee's approval.",
        "checked": "Reproduction Tier X, reduction Tier C, Lean statement and non-degeneracy lemmas Tier A, replayed in the kernel (rc 0, final replay record); the LeanFlow data certificate is not in the replay; independent AI audit with three required corrections, applied.",
        "arc": "P5",
        "arc_role": "Humans decide meaning: checking an AI's claimed proof before anyone builds on it, and naming what remains unchecked.",
    },
    "ED-22": {
        "what": "Continuing the previous item, four of the twelve stages of that certificate were re-executed inside the Lean kernel and one reduction lemma was proved; the cost of the remaining stages was measured. The conjecture is not formally proved, and the paper says so in its title.",
        "analogy": "Rebuilding four floors of a twelve-storey building to code, and timing how long the rest would take.",
        "checked": "Elenchus Tier A for the four stages (replayed, rc 0; the auditor's rebuild gave byte-identical files); independent AI audit.",
        "arc": "P5",
        "arc_role": "Lean judges an AI's certificate piece by piece; progress reported as a fraction, not a victory.",
    },
    "ED-24": {
        "what": "OpenAI published Lean proofs of 'breakdown' theorems for the Navier-Stokes and Euler equations of fluids. This work rebuilt all 2,440 modules independently, replayed 88,400 declarations in the Lean kernel, found no soundness escape, and compared the statements with the official problem texts. It is not a claim that a Clay Millennium problem is solved; credit for the proofs belongs to the corpus authors.",
        "analogy": "Re-assembling a famous machine from its blueprint in your own workshop to check that it runs, without claiming you invented it.",
        "checked": "Kernel replay with leanchecker (Tier A for the replay facts); statement fidelity is a human-style comparison (Tier C); independent AI audit reproduced every technical claim with its own scripts.",
        "arc": "P5",
        "arc_role": "Trust in AI made concrete: an outside, reproducible check of an AI lab's flagship proof.",
    },
    "Z-RIESZ": {
        "what": "Three consequences of the upstream theorem, checked in Lean: optimality for every inverse-power repulsion ('Riesz' energies), finiteness of that energy for powers above 2 (so the statement is not empty), and optimality at every density, not only density one. Mathematically these follow quickly, and the upstream manuscript already mentions inverse powers; the value is that they are named, kernel-checked statements that later papers did build on. Conditional on the AI-generated upstream theorem.",
        "analogy": "Turning a general warranty into signed certificates for each specific model.",
        "checked": "Elenchus Tier A, recompiled by independent verifiers and replayed (rc 0); referee audit applied.",
        "arc": "P3",
        "arc_role": "The first bricks of the kernel-checked programme: small, honest, reusable.",
    },
    "G-RUSTY": {
        "what": "An AI-assisted translation into the Rust language of SUNDIALS CVODE, a widely used solver for 'stiff' differential equations, the workhorse of chemistry, plasma and biology simulations. It became the numerical backbone of many of the year's papers, and independent auditors re-ran its results byte for byte. Its numbers are never treated as proof (floating point), some of its Lean specification files contain empty ('vacuous') axioms that must not be built on, and an audit of its fusion material led to retractions.",
        "analogy": "A rebuilt engine that powers much of the fleet, with an inspection report listing the parts that turned out to be fake.",
        "checked": "Elenchus Tier X (floating point) for every output; independent AI audit of the fusion work merged with retractions (PR #60); reruns by auditors in later papers matched.",
        "arc": "P1",
        "arc_role": "Numerics explore: the instrument that makes the experiments possible, kept in its place below the proof checker.",
    },
    "Z-GWAYA": {
        "what": "A 'fail-closed' gate for code written by language models: code is accepted only if real compilers, a parser, the Rust type checker and the Lean kernel with an axiom audit all pass. It demonstrates that a Lean file 'proving' 1 = 2 through a hidden assumption compiles without error and is caught only by the axiom audit. Earlier benchmark figures were withdrawn; on a small author-built test set it made no in-scope errors, but it still accepted code with semantic bugs.",
        "analogy": "A door that opens only when every guard has signed, though the guards still cannot tell whether the visitor is honest about why they came.",
        "checked": "The 1 = 2 demonstration is a Lean fact with an axiom check; the gate's error rates are measured on the author's own corpus (self-check); reproduction bundle with sources, tests and checksums.",
        "arc": "P3",
        "arc_role": "Lean judges code, not only mathematics: the lesson that 'it compiled' proves nothing until the axioms are audited.",
    },
    "G-AUTOEVOLVE": {
        "what": "The project's own laboratory bench: the harness that runs local models, Lean checks, GPU jobs and the claim ledger used by the later papers. Its README publishes that an internal audit found 14 components that reported success without doing the work; the audit notes show, for example, a 'peer review' script that never called a reviewer and proof checks fooled by exit codes. Those findings shaped the gates used afterwards. Not peer reviewed.",
        "analogy": "A kitchen whose own inspection found ovens that displayed 'done' without heating, and which fixed the thermometers before cooking again.",
        "checked": "Internal audits (self-check), public code; the sound Lean gate it hosts checks axioms, not exit codes.",
        "arc": "P2",
        "arc_role": "The turn from agents that report success to gates that can fail: the infrastructure behind Phases 3 and 5.",
    },
    "L-STELLARATOR": {
        "what": "A batch of papers deposited on 19 October claimed, among other things, that a standard simulation method (RK4) slowly 'heats' charged particles in a fusion device's magnetic trap until they escape. Edition 2 tested that claim with 2,000 orbits per energy band and controls able to fail: the claim is false. At the step sizes used RK4 cools the particles, and its real failure is the opposite one: it traps particles that should escape. Confidence figures and a theorem from edition 1 were withdrawn, and the paper says no one but the author has reviewed it.",
        "analogy": "Blaming the thermostat for overheating the house, then measuring and finding that it keeps the house too cold.",
        "checked": "Tier X experiment with a falsification rule fixed in advance and six passing controls; Lean results for the linear case (axiom footprint not stated in the record); no independent review.",
        "arc": "P4",
        "arc_role": "Relapse and recovery: an over-claim from the 19 October batch withdrawn two days later by measuring it.",
    },
}


def short(t: str, n: int = 78) -> str:
    return t if len(t) <= n else t[: n - 1] + "…"


def main() -> None:
    sel = SC["selected"]
    assert set(sel) <= set(PROSE), (set(sel) - set(PROSE))  # final rescore: N2 prose kept, unused
    top = []
    for i, cid in enumerate(sel, 1):
        r = ROWS[cid]
        p = PROSE[cid]
        top.append({
            "pick": i, "id": cid, "title": r["title"], "domain": r["domain"], "date": r["created"][:10],
            "primary_doi": r["primary_doi"], "all_dois": r["member_dois"], "repos": r["repos"],
            "lesson": r["lesson"], "total": r["total"],
            "score_breakdown": {k: v["score"] for k, v in r["scores"].items()},
            "score_justifications": {k: v["why"] for k, v in r["scores"].items()},
            "what_it_is": p["what"], "analogy_suggestion": p["analogy"],
            "what_was_checked_and_how": p["checked"],
            "arc_phase": ARC[p["arc"]], "arc_role": p["arc_role"],
            "private_repo_warning": any(x["visibility"] == "PRIVATE" for x in r["repos"]),
        })
    (OUT / "TOP20_final.json").write_text(json.dumps({
        "rubric": SC["rubric"], "arc_spine": "AI proposes -> numerics explore -> Lean judges -> humans decide meaning",
        "picks": top}, indent=1, ensure_ascii=False))

    L: list[str] = []
    w = L.append
    w("# Discovery journal 2026: selection of the 20 contributions (final kernel replay record)")
    w("")
    w("Applied 2026-10-26 to the rubric frozen in `RUBRIC.md` (not changed). Built by `scripts/score_build_final.py` (scores, coverage")
    w("checks, ranking, hard rules) and `scripts/top20_build_final.py` (this file and `TOP20_final.json`). Every score has a one-line")
    w("justification in `scores_final.json` citing the inventory field, audit file, replay record or memory note it rests on.")
    w("This is the rescore with the final 93-row replay record; the earlier 71-row version is `SELECTION.md` / `TOP20.json`,")
    w("and the differences are listed in `RESCORE.md`.")
    w("")
    w("## 1. Candidates")
    w("")
    w("- **Zenodo:** all 144 records in `zenodo_inventory.json` (112 distinct titles) plus the N2 paper doi:10.5281/zenodo.23663551,")
    w("  which was published after the inventory was fetched (added from `papers/p3_zero_point_physical/`).")
    w("  The builder asserts that every record belongs to exactly one candidate.")
    w("- **GitHub:** all 57 science-relevant repositories. Test for 'represented': a Zenodo work *describes the repository's")
    w("  content* (its library, tool, programme or paper line). 24 repos pass and are attached to that work (listed in each")
    w("  candidate's `repos` and `merge_note`); the other 33 form 31 repository candidates.")
    w("- **Two judgement calls, stated because they decide picks:** AutoevolveAI (the ANSE harness) and rusty-SUNDIALS (the")
    w("  CVODE translation) host the code of many Zenodo works (the `autoevolve_*` bundles, the programme papers, qf-pgpe")
    w("  23269715) but no Zenodo work describes either repository itself, so both are candidates. They then fill the")
    w("  AI-methodology and numerics minimum slots. Counterfactual (computed in `score_build.py`, stored in `scores.json`")
    w("  as `counterfactual_harness_repos`): if both were treated as represented, " +
      ", ".join(SC["counterfactual_harness_repos"]["enter"]) + " would enter in place of " +
      ", ".join(SC["counterfactual_harness_repos"]["leave"]) + "; nothing else changes.")
    w(f"- **Result:** {SC['n_candidates']} candidates.")
    w("- **Mandatory merges:** duplicate deposits (e.g. WARS-CI-DFA x13, stellarator x7, PQC x7) and versions under one concept.")
    w("- **Declared research-line merges** (criterion: same research question, or an explicit 'supersedes/corrects'; decided")
    w("  before ranking): the dual-scale/K3 dark-sector hypothesis line (7 records + 6 repos) scored on its retraction")
    w("  22837842; Mathieu moonshine (22823720 + 22837835); Agora corpus papers 4-6; the gated-exciton-fluids series I-V plus")
    w("  23289027; vortex friction correction + transport v2.2; reticulate evolution 23604793 + its correction 23610116;")
    w("  QuantumFluids library under two concepts; GWAYA v3 + v3.1; Elenchus Trilogy I-III.")
    w("- **Aggregation of a merged line:** lesson lines are scored on the withdrawal/correction record (rubric exclusion rule);")
    w("  other research-line merges take the best member per criterion, and the justification names that member.")
    w("")
    w("## 2. Scoring key (thresholds applied identically to every candidate)")
    w("")
    w("- **C1 rigour** = the highest Elenchus tier reached by a claim the record itself states. 3 = Lean with axiom check *and* a")
    w("  recorded kernel replay (leanchecker / Comparator / a second kernel such as nanoda, or the 2026-10-26 replay record")
    w("  `results/kernel_replay_2026-10-26/replay.jsonl`), or an untrusted program's certificate re-checked by *different* code")
    w("  (the Lean kernel checking a solver's integer tables: P1, P2/P3). An auditor's recompilation is a compile, not a replay,")
    w("  so it does not lift 2 to 3. Re-running the *same* certificate code (Sandier-Serfaty reproduction, ball-arithmetic")
    w("  reruns) is not an independent checker. 2 = the record states a Lean axiom footprint within {propext, Classical.choice,")
    w("  Quot.sound} or 'zero sorryAx, zero custom axioms' (taken as recorded). 'Zero sorry' or 'exit 0' alone, and")
    w("  `native_decide`, do not reach 2 (a `sorry` compiles with exit 0). 1 = human argument, literature, or exact computation")
    w("  without a kernel. 0 = floating point only.")
    w("  Replay record used: the final `replay.jsonl` (tracked since commit 2b0dba1), 93 rows, all rc 0 (`result.json`:")
    w("  OK 93, SKIPPED 778, no failures). Not replayed: SandierSerfatyL1 (776 modules, still being generated), BAOCert,")
    w("  QuantumFluids H7/H8/P6. ED-20 and N2 cite the N2 paper's own `data/leanchecker_replay.json`; the final record agrees.")
    w("- **C2 independent check:** 3 = a verdict file by a separate agent (AUDIT.md, verification.md, manuscript_audit, referee")
    w("  rounds) *and* a record that its corrections were applied (REVISION.md, response files, or a memory note). 2 = such a")
    w("  verdict without a record of corrections. A review mentioned only in run notes, with no verdict file (ED-01, ED-02), is")
    w("  scored at the lower value. 1 = the author's own checks (preregistered gates, internal audits). The '5-Round")
    w("  Peer-Reviewed' label of the 19 October batch scores 1: AI-agent review with no audit artifact, and the same batch's")
    w("  review files were withdrawn as script-generated (23525655, 23468458). 0 = nothing.")
    w("- **C3 reproducibility:** 3 = re-run by an agent other than the producer with matching output, documented (audit")
    w("  recompile/rerun, verifier recompile, replay). 2 = the record ships code + data + commands (a reproduction bundle,")
    w("  MANIFEST, REPRODUCE.md, code.zip + dataset.zip). 1 = code available (record files or a public repository).")
    w("  0 = none, or the code sits only in a PRIVATE repository.")
    w("- **C4 synthesis** (mechanical, from inventory fields as found): physics/biology pillar = domain physics, cosmology,")
    w("  fusion/plasma or genetics/biology; formal pillar = `lean_component` yes (a mention, accepted for synthesis but not")
    w("  for rigour); mathematics pillar = domain mathematics or `lean_component` yes; numerics pillar =")
    w("  `numeric_or_simulation_component` yes. 1 pillar = 0 … 4 pillars = 3. For repos: Lean files, Rust/SUNDIALS/numerics")
    w("  and domain from `github_inventory.json`.")
    w("- **C5 honesty:** 3 = the record publishes a negative result, a self-correction of earlier work, or a refutation;")
    w("  2 = caveats stated; 1 = none; 0 = later retracted with no correction published.")
    w("- **C6 novelty:** 3 only when later work demonstrably reused it (reuse cited); 2 = new result or tool; 1 = incremental;")
    w("  0 = duplicate.")
    w("- **C7 value to people:** 3 = a non-specialist sees a concrete stake (health, energy, education, trust in AI); 2 =")
    w("  understandable; 1 = abstract; 0 = none.")
    w("- **Lesson** (for the '>= 3 lessons' rule) = the scored record's inventory kind is 'negative or null result', or the")
    w("  candidate is a withdrawal/correction line scored on its correction record. A positive paper that contains a")
    w("  refutation (ED-17) or an erratum fix (ED-10) is not counted as a lesson.")
    w("- **Domains** are the inventory's `classification.domain` as found (N2 given physics, like B2 and QU-1); cosmology,")
    w("  fusion/plasma, education/textbook and other count toward no minimum but are capped at 7. Repo labels were mapped")
    w("  by name only ('AI agents/methodology/verification' -> 'AI methodology/verification').")
    w("- **Ties:** total, then C1, then C2, then the earlier `created` timestamp (repo: creation date).")
    w("")
    w("## 3. Hard rules, applied in this order (code: `select()` in `score_build_final.py`, unchanged)")
    w("")
    w("1. Exclusions: works whose central claim was withdrawn or refuted are folded into lesson lines scored on the")
    w("   withdrawal paper (RunuX v1 -> 22879667; 22723078 -> 22773907; dual-scale physics -> 22837842; stellarator x7 ->")
    w("   23532458; PQC -> 23532601; scale-dual subgrid -> 23532595; POLE mechanism -> 23526783). Edition 1 of stochastic")
    w("   thermodynamics (23510019), enstrophy v2.0 (23458238) and vortex transport (23262143) withdrew a label or a reading,")
    w("   not their central claim, and are merged with their correction. Exclusion test on 23646117 (Bogoliubov): its")
    w("   envelope is refuted for real He-4 by 23653846, but its own central claims are Lean shape theorems and a test that")
    w("   stayed silent, so it stays eligible.")
    w("2. Domain minimums: the top 2 of mathematics, physics, genetics/biology, numerics/software and AI")
    w("   methodology/verification are reserved.")
    w("3. Lessons: if fewer than 3 reserved picks are lessons, the top-ranked lessons are added.")
    w("4. The remaining slots are filled in rank order, skipping any candidate whose domain already has 7.")
    w("")
    w("Selection log:")
    w("")
    for line in SC["selection_log"]:
        w(f"- {line}")
    w("")
    w("## 4. The 20 chosen")
    w("")
    w("| # | id | title | domain | date | C1 | C2 | C3 | C4 | C5 | C6 | C7 | total | lesson |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for t in top:
        s = list(t["score_breakdown"].values())
        w(f"| {t['pick']} | {t['id']} | {short(t['title'], 70)} | {t['domain']} | {t['date']} | "
          + " | ".join(str(x) for x in s) + f" | {t['total']} | {'yes' if t['lesson'] else ''} |")
    w("")
    w("Domain count: " + ", ".join(f"{d} {sum(1 for t in top if t['domain'] == d)}" for d in
                                    sorted({t['domain'] for t in top})) + f"; lessons {sum(1 for t in top if t['lesson'])}.")
    w("")
    pure = SC["pure_top20"]
    out_ = [c for c in pure if c not in sel]
    in_ = [c for c in sel if c not in pure]
    w("## 5. What the rules changed, said openly")
    w("")
    w("Compared with the pure top 20 by total score:")
    w("")
    for c in out_:
        r = ROWS[c]
        why = ("removed by the cap of 7 per domain (physics already had 7 higher-ranked picks)" if r["domain"] == "physics"
               else "displaced: the four slots reserved for the numerics/software and AI-methodology minimums pushed the lowest-ranked remaining picks out")
        w(f"- **Out:** {c} ({short(r['title'], 60)}; {r['domain']}; total {r['total']}; pure rank {r['rank']}): {why}.")
    for c in in_:
        r = ROWS[c]
        w(f"- **In:** {c} ({short(r['title'], 60)}; {r['domain']}; total {r['total']}; pure rank {r['rank']}): reserved by the")
        w(f"  minimum of 2 for {r['domain']}.")
    w("")
    w("- The lessons rule did not change the list: ED-15 and ED-20 were already in the pure top 20, and the numerics minimum")
    w("  brought in the stellarator lesson, which makes 3.")
    w("- The AI-methodology second place was a tie at 14 between G-AUTOEVOLVE and Z-CLAIMS-AUDIT: equal C1 (1) and C2 (1),")
    w("  broken by the earlier date (repo created 2026-09-19 vs record 2026-09-27).")
    w("- Numerics/software is thin: its second pick (L-STELLARATOR, 13) is a lesson, ranked 42nd overall. It counts as")
    w("  numerics/software because the rubric scores a lesson line on its withdrawal paper, and 23532458 is classified")
    w("  numerics/software; the seven merged stellarator deposits are classified fusion/plasma.")
    w("- The harness counterfactual (section 1): treating AutoevolveAI and rusty-SUNDIALS as represented would swap in "
      + ", ".join(SC["counterfactual_harness_repos"]["enter"]) + ".")
    priv = [t["id"] for t in top if t["private_repo_warning"]]
    w(f"- Private repositories among the 20: {', '.join(priv) if priv else 'none'}. Z-LABMETHOD (below rank 20) rests on the")
    w("  private Elenchus repo; the book must ask before summarising any private repository.")
    n_oct = sum(1 for t in top if "2026-10-08" <= t["date"] <= "2026-10-26")
    w(f"- Concentration: {n_oct} of the 20 are dated 8-26 October 2026, because the rubric rewards replay, independent audits with")
    w("  recorded revisions and published negative results, which the project only produced systematically from October.")
    w("  The earlier phases are told in `ARC.md` and enter the list mainly through the lessons and infrastructure picks.")
    w("")
    w("## 6. Full ranked table (all candidates)")
    w("")
    w("| rank | id | title | domain | date | C1 | C2 | C3 | C4 | C5 | C6 | C7 | total | lesson | selected |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in SC["candidates"]:
        s = [v["score"] for v in r["scores"].values()]
        w(f"| {r['rank']} | {r['id']} | {short(r['title'], 64)} | {r['domain']} | {r['created'][:10]} | "
          + " | ".join(str(x) for x in s)
          + f" | {r['total']} | {'yes' if r['lesson'] else ''} | {'**yes**' if r['selected'] else ''} |")
    w("")
    w("Per-criterion justifications, member DOIs, repos (with visibility), merge and exclusion notes: `scores_final.json`.")
    (OUT / "SELECTION_final.md").write_text("\n".join(L) + "\n")
    print("wrote TOP20_final.json and SELECTION_final.md;", len(top), "picks")


if __name__ == "__main__":
    main()
