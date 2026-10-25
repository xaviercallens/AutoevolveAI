# Kernel-Gated Evolution — extension roadmap across domains and repositories

**Status:** proposal, 2026-10-25. Built from a scan of 25 local repositories under `~/xdev`
and ~60 non-fork repositories on github.com/xaviercallens, then a read of the code at each
candidate attachment point. Every entry below states what was *verified in code*; first
readings that turned out wrong are recorded, because three of four initial readings overstated.

Foundation: Paper J, concept DOI [10.5281/zenodo.23635678](https://doi.org/10.5281/zenodo.23635678);
guide: [`KGE_GUIDELINES.md`](KGE_GUIDELINES.md).

## The four transferable ideas

| | idea | evidence it works |
|---|---|---|
| **P1** | **Kernel-gated acceptance** — the search may be heuristic, biological, even wrong; nothing is accepted unless the Lean kernel proves it (`#print axioms`, no `sorryAx`, whitelist only) | 31 ladder + 39 SRSD-Feynman + 40 lifetime-learning solutions all kernel-proved; the planted wrong candidate rejected in every batch |
| **P2** | **Exact lifetime learning** — constants solved by `v* = v + (want − out)/B` (Lean: `xav_required_value`) | never lost a solve on 1,200 paired seeds; at matched total work ahead on L3 and L5 |
| **P3** | **One-invocation gate** — a batch verified in one Lean call at any failure rate, by reading the per-declaration report rather than the exit code | 1 invocation at 0–8 failures of 8, no false acceptance, vs 50.88 s for eight |
| **P4** | **Variance-collapse monitoring** — H12 (Lean: `kal_increment_is_variance`): selection's progress is `Var(w)/w̄` | per-generation solve hazard falls after collapse, L3 p = 0.015, L5 p = 0.0019; random immigrants do not help |

## Where each idea attaches — verified

| repository | P1 | P2 | P3 | P4 | what was verified | action |
|---|:-:|:-:|:-:|:-:|---|---|
| **SocrateAI-Scientific-Agora-LeanMaster** | ● | | ○ | | `workflowphase2.py` gate = exit code + text scan for `sorry`; `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` compiled and passed. Library currently clean. | **PR [#5](https://github.com/xaviercallens/SocrateAI-Scientific-Agora-LeanMaster/pull/5)** — refuse all six; follow-up: per-theorem `#print axioms` audit |
| **GWAYA-GwenLayaOpenModel** | ✓ | | ● | | Lean oracle already kernel-gated correctly (axiom probe, audit count, escape regex). But `success = returncode == 0` first, and `verify_snippet` is one candidate per invocation — the repair loop and pass@k pay full fixed cost each time. | **PR [#33](https://github.com/xaviercallens/GWAYA-GwenLayaOpenModel/pull/33)** — design proposal for `verify_snippets_batch`; re-measure on its sandboxed toolchain |
| **SocrateAI-Scientific-AutoEvolve-K3xT2** | ○ | ○ | ✓ | ● | Truncation selection to top 10 each generation — the H12 regime. Lean oracle is a compiled *evaluator* (already batched), not a prover, so P1 does not map as-is. Phase-1 fitness `evaluate_k3_phenotype` is a labelled mock; `test_lean_gatekeeper.py` tests a Python stand-in (`_simulated_lean_verify`), not Lean. | **PR [#2](https://github.com/xaviercallens/SocrateAI-Scientific-AutoEvolve-K3xT2/pull/2)** — measure-only diversity monitor; label the simulated-verifier tests as such |
| **rusty-SUNDIALS** | ● | ● | ● | | BDF/Adams integrators (`crates/cvode/src/step.rs`, `crates/ida`) are defined by coefficient sets whose **order conditions are exact polynomial identities over ℚ** — KGE's home ground; Lean proofs already live in `formal_proofs/`. | **New domain (Phase 2):** Lean-gated synthesis/verification of integrator coefficient sets |
| **SocrateAI-Scientific-RajMathRecovery** | ● | ● | ● | | Exact q-series / eta-quotient identity discovery; `scripts/formal_lock.py` already talks to Lean. | **New domain (Phase 2):** discovered identities accepted only with a kernel proof, batched |
| **HiveMind** (sub-project + repo) | ✓ | | ● | | `verify_lean_print_axioms_coverage` exists; distributed contributors submit Lean specs. | **Phase 2:** batch contributor submissions per P3 |
| **SocrateAI-Scientific-QuantumFluids** | | ◐ | | | Fits (`phonon_branch`, `roton_branch`) are on **noisy** data: exact P2 does not apply. Only the affine-parameter closed-form least-squares that the dosage identity implies transfers. | **Phase 3 (optional)** |
| **SocrateAI-Lean-Lib**, Elenchus, Mathesis, SectorCausality, DualScaleSimulator | ◐ | | ◐ | | Lean is invoked by build scripts; no candidate-generation loop found. | Adopt the `#print axioms` gate only where acceptance is decided |
| physlib (vendored in LeanMaster) | | | ○ | | `check_golf.py` compiles one candidate per call, but it is **upstream** `leanprover-community/physlib` code. | **No PR** — not our repository |

● strong fit, action taken or planned · ◐ partial · ○ applies weakly · ✓ already does it right

### First readings that were wrong (kept for the record)

- *"GWAYA accepts Lean on exit code"* — false; its oracle is correctly kernel-gated. The real attachment is batching (P3).
- *"LeanMaster accepts `sorry`"* — false; it scans for `sorry`. What it missed are the five *other* escape hatches.
- *"Exact lifetime learning applies to AutoEvolve's constant fitting"* — false; those fits are on noisy observational data.
- *"check_golf.py should batch"* — it is upstream physlib code.

## Phased roadmap

**Phase 1 — land what is open (now).** Review/merge LeanMaster #5, AutoEvolve #2, GWAYA #33.
Each was opened with tests (or, for #33, the tests a future implementation must pass).

**Phase 2 — the strong new domains.**
1. *rusty-SUNDIALS — Lean-gated integrator coefficients.* Encode BDF/Adams (and Runge–Kutta
   Butcher) order conditions as exact identities over ℚ; let KGE search coefficient sets with
   exact lifetime learning of the free coefficients (P2 — the conditions are affine in each
   coefficient), batch-verify survivors (P3), accept only kernel-proved sets (P1). Positive
   control: recover the textbook BDF2/BDF3 and RK4 coefficients; negative control: a perturbed
   coefficient must be rejected by name.
2. *RajMathRecovery — kernel-proved identities.* Route every discovered eta-quotient identity
   through one batched `#print axioms` gate; report proved vs conjectured separately.
3. *GWAYA — implement `verify_snippets_batch`* per PR #33 once the measurement is reproduced on
   its toolchain.
4. *HiveMind — batch contributor Lean specs* through the same per-declaration reader.

**Phase 3 — the open science.**
1. *"Perturb the best, not inject the random"* (registered after random immigrants failed):
   on collapse, inject mutants of the elite and test the solve hazard against the edition-5 baseline.
2. *The H11 lower bound* — the absorption argument completing `xav_wf_fixation_by_time_le` to
   the fixation probability.
3. *Grammar growth with proofs* — division and powers, each with its dosage rule proved, ranked by
   the 79 + 10 SRSD-Feynman refusals they would unlock.
4. *A persistent Lean kernel* — removing the ~97% fixed cost per invocation.

## Disciplines every adoption must keep

From `LL.md` §29 and the KGE guidelines: plant a wrong candidate in every gate batch; run the
simplest control (restart hill-climber) on the same seeds and budget; report fitness evaluations
*and* total work; replay cross-implementation gaps on identical inputs; never let the generator
grade itself.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
