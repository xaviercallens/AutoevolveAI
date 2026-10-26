# GitHub inventory: xaviercallens, window 2025-10-26 to 2026-10-26

Source: `gh repo list` plus per-repo API calls, collected 2026-10-26. Read-only. Private repos are described at high level only (no code, no README quotes). Summaries are one-sentence readings of the README/description by the collector, not verified claims; see each repo's own caveats.

## Counts

- total: 420
- forks: 317
- non_forks: 103
- private_total: 21
- non_fork_outside_window: 21
- kept: 82
- kept_public: 63
- kept_private: 19
- science_relevant: 57
- empty_or_placeholder_repos: 12
- criteria: created OR pushed on/after window start; isFork=false

Caveat: `pushedAt`/`createdAt` come from the GitHub API; commit counts are commits reachable from the default branch since 2025-10-26. Several repos were created before the window (e.g. amcp, 2025-09) but pushed within it. Duplicates: SocrateAI-Scientific-Agora and SocrateAI-Scientific-NewDiscoveries report identical metrics and are probably one repo under two names.

## By domain

### personal/other (17)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenAI4F | PUBLIC | 2026-09-24 | 2026-09-24 | TypeScript | 2 | 0 | 0 | 0 | 0 | 0 |
| OpenSourceAI4Finance-ControlCenter | PUBLIC | 2026-09-24 | 2026-09-24 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| PersonaShield | PRIVATE | 2026-01-24 | 2026-01-24 | None | None | 0 | None | None | None | 0 |
| ReadyPlayerTogether | PUBLIC | 2026-08-06 | 2026-08-23 | GDScript | 81 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-Scientific-LLeanM | PUBLIC | 2026-08-10 | 2026-08-10 | None | None | 0 | None | None | None | 0 |
| VibeSpec | PUBLIC | 2026-03-22 | 2026-03-22 | TypeScript | 10 | 0 | 0 | 0 | 0 | 0 |
| WebWebLightv4 | PRIVATE | 2026-03-21 | 2026-03-21 | TypeScript | 3 | 0 | 0 | 0 | 0 | 0 |
| macmagicbrush | PRIVATE | 2025-12-29 | 2026-01-08 | TypeScript | 1 | 0 | 0 | 0 | 0 | 0 |
| mopga | PRIVATE | 2026-02-15 | 2026-02-15 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| scribemed | PUBLIC | 2025-11-29 | 2025-12-02 | Python | 4 | 0 | 0 | 0 | 0 | 0 |
| symbioticfactory | PUBLIC | 2026-02-22 | 2026-02-22 | Python | 20 | 0 | 0 | 0 | 0 | 0 |
| videomorph | PRIVATE | 2026-01-24 | 2026-01-24 | None | None | 0 | None | None | None | 0 |
| wazair | PUBLIC | 2025-12-18 | 2026-10-24 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| webwarcybergame | PUBLIC | 2026-03-13 | 2026-09-05 | Python | 26 | 0 | 0 | 0 | 0 | 0 |
| xPersonaShield | PRIVATE | 2026-01-24 | 2026-10-08 | Python | 57 | 1 | 0 | 0 | 0 | 0 |
| xprivateremoteaccess | PRIVATE | 2026-05-10 | 2026-05-10 | PowerShell | 1 | 0 | 0 | 0 | 0 | 0 |
| xvideomorph | PRIVATE | 2026-01-24 | 2026-01-25 | None | 1 | 0 | 0 | 0 | 0 | 0 |

### AI agents/methodology/verification (16)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| AutoevolveAI | PUBLIC | 2026-09-19 | 2026-10-26 | Python | 352 | 7 | 164 | 57 | 0 | 1 |
| GWAYA-GwenLayaOpenModel | PUBLIC | 2026-10-03 | 2026-10-25 | Python | 217 | 29 | 0 | 0 | 0 | 0 |
| HiveMind | PUBLIC | 2026-10-18 | 2026-10-26 | Python | 474 | 127 | 3 | 0 | 0 | 4 |
| SocrateAI-Scientific-Agora | PRIVATE | 2026-05-31 | 2026-06-26 | TeX | 36 | 7 | 200 | 43 | 1 | 0 |
| SocrateAI-Scientific-Communication | PUBLIC | 2026-09-06 | 2026-09-10 | TeX | 20 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-Scientific-Elenchus | PRIVATE | 2026-09-18 | 2026-09-20 | Python | 24 | 0 | 9 | 1 | 0 | 0 |
| SocrateAI-Scientific-Mathesis | PUBLIC | 2026-08-13 | 2026-08-25 | Python | 24 | 0 | 13 | 3 | 0 | 0 |
| SocrateAI-Scientific-NewDiscoveries | PRIVATE | 2026-06-18 | 2026-10-26 | TeX | 36 | 0 | 200 | 43 | 1 | 0 |
| SocrateAI-Scientific-TNN-UniversModel | PUBLIC | 2026-08-12 | 2026-08-28 | Python | 68 | 0 | 13 | 1 | 0 | 0 |
| SocrateAI-thesisautoresearch | PRIVATE | 2026-05-21 | 2026-05-24 | HTML | 86 | 1 | 18 | 0 | 0 | 0 |
| SuperGravity | PUBLIC | 2026-09-20 | 2026-09-20 | Python | 12 | 0 | 11 | 0 | 0 | 0 |
| amcp | PUBLIC | 2025-09-24 | 2026-10-25 | Java | 2 | 7 | 0 | 0 | 0 | 0 |
| amcp-v1.5-opensource | PUBLIC | 2025-09-27 | 2026-10-25 | Java | 0 | 2 | 0 | 0 | 0 | 0 |
| attentionmatter | PRIVATE | 2026-06-25 | 2026-06-25 | Python | 12 | 0 | 0 | 0 | 0 | 0 |
| nSymboCoder | PRIVATE | 2026-05-10 | 2026-05-10 | Python | 1 | 0 | 0 | 0 | 0 | 0 |
| xAuraOS | PUBLIC | 2026-08-06 | 2026-08-06 | Python | 2157 | 0 | 0 | 7 | 0 | 0 |

### physics (12)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenAI-NSE-Epistemic-Audit | PUBLIC | 2026-09-10 | 2026-09-19 | Python | 132 | 0 | 22 | 20 | 5 | 4 |
| SocrateAI-Scientific-Agora-LeanMaster | PUBLIC | 2026-09-12 | 2026-10-25 | Lean | 191 | 5 | 887 | 1 | 1 | 0 |
| SocrateAI-Scientific-Agora-Physique-Cinetique | PUBLIC | 2026-06-22 | 2026-09-27 | Jupyter Notebook | 57 | 4 | 6 | 2 | 4 | 0 |
| SocrateAI-Scientific-CondensedMatterTheory | PUBLIC | 2026-09-27 | 2026-10-10 | Python | 158 | 3 | 5 | 0 | 0 | 0 |
| SocrateAI-Scientific-DualScaleSimulator | PUBLIC | 2026-09-10 | 2026-10-10 | Python | 321 | 1 | 26 | 9 | 1 | 0 |
| SocrateAI-Scientific-LeanMaster-CoreStringTheoryFormalization | PUBLIC | 2026-09-16 | 2026-09-16 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-Scientific-QuantumComputing | PUBLIC | 2026-10-11 | 2026-10-11 | Python | 4 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-Scientific-QuantumFluids | PUBLIC | 2026-08-14 | 2026-10-18 | Python | 511 | 3 | 95 | 39 | 0 | 2 |
| SocrateAI-Scientific-SectorCausalityTheory | PUBLIC | 2026-09-27 | 2026-09-28 | Jupyter Notebook | 10 | 0 | 30 | 0 | 3 | 0 |
| xaviercallens-SocrateAI-Scientific-Agora-K3-Quatum | PUBLIC | 2026-08-04 | 2026-08-10 | Python | 10 | 0 | 1 | 0 | 0 | 0 |
| xaviercallens-SocrateAI-Scientific-FluidMecanism | PUBLIC | 2026-08-12 | 2026-08-12 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| xaviercallens-SocrateAI-Scientific-LeanMaster-StringTheoryFormalization | PUBLIC | 2026-09-14 | 2026-09-14 | HTML | 3 | 0 | 32 | 0 | 0 | 0 |

### mathematics (11)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| Mirror-Map-Sieve | PUBLIC | 2026-06-18 | 2026-07-12 | Python | 101 | 1 | 18 | 0 | 1 | 0 |
| OptimalEnergyAI | PRIVATE | 2026-10-12 | 2026-10-17 | TeX | 38 | 10 | 10 | 0 | 0 | 0 |
| SocrateAI-CohnKumar-8D-Numeric | PUBLIC | 2026-10-11 | 2026-10-11 | None | None | 0 | None | None | None | 0 |
| SocrateAI-Lean-Lib | PUBLIC | 2026-09-05 | 2026-09-10 | Lean | 12 | 1 | 114 | 0 | 0 | 0 |
| SocrateAI-Lean-Verification | PRIVATE | 2026-06-13 | 2026-06-13 | Lean | 1 | 0 | 56 | 0 | 1 | 0 |
| SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic | PUBLIC | 2026-08-09 | 2026-08-28 | Lean | 91 | 0 | 4471 | 0 | 0 | 0 |
| SocrateAI-Scientific-AlienMathematics-Foundation | PUBLIC | 2026-06-08 | 2026-06-13 | Python | 2 | 0 | 16 | 0 | 0 | 0 |
| SocrateAI-Scientific-MechanicaFluidorum | PUBLIC | 2026-08-12 | 2026-10-25 | Python | 177 | 1 | 16 | 3 | 0 | 0 |
| SocrateAI-Scientific-Mensura | PUBLIC | 2026-08-14 | 2026-08-25 | Python | 38 | 0 | 3 | 1 | 0 | 0 |
| SocrateAI-Scientific-Poly-Algebraic-Calculus | PUBLIC | 2026-08-11 | 2026-08-11 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| triangular-universal-optimality-lean | PUBLIC | 2026-10-11 | 2026-10-22 | TeX | 18 | 3 | 9 | 0 | 0 | 0 |

### cosmology (8)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| DarkMatterK3-Home.github.io | PUBLIC | 2026-07-04 | 2026-10-11 | Python | 380 | 22 | 0 | 0 | 0 | 0 |
| SocrateAI-Dual-Scale-Agora-Lab | PUBLIC | 2026-08-14 | 2026-08-15 | None | 2 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal | PUBLIC | 2026-07-15 | 2026-10-10 | Lean | 196 | 7 | 47 | 0 | 1 | 0 |
| SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2 | PUBLIC | 2026-07-28 | 2026-07-28 | Python | 9 | 0 | 4 | 0 | 0 | 0 |
| SocrateAI-Scientific-Agora-K3-DarkMatter | PUBLIC | 2026-06-25 | 2026-10-10 | Python | 485 | 62 | 64 | 0 | 3 | 0 |
| SocrateAI-Scientific-AutoEvolve-K3xT2 | PUBLIC | 2026-07-29 | 2026-10-25 | Python | 144 | 1 | 7 | 0 | 0 | 0 |
| SocrateAI-Wolfram-Hypergraph | PUBLIC | 2026-07-28 | 2026-08-03 | Python | 41 | 0 | 13 | 3 | 0 | 0 |
| TIC4206066-Exoplanet-Verification | PUBLIC | 2026-10-11 | 2026-10-11 | Python | 12 | 0 | 2 | 0 | 0 | 0 |

### numerics/software (7)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| SocrateAI-Numeric-DualScale-Solver | PUBLIC | 2026-08-30 | 2026-09-22 | Python | 51 | 0 | 40 | 23 | 0 | 0 |
| SocrateAI-Numeric-DualScale-Solver-Enterprise | PRIVATE | 2026-08-31 | 2026-09-18 | Python | 58 | 3 | 40 | 69 | 0 | 0 |
| SocrateAI-Scientific-Agora-LeanFlow | PRIVATE | 2026-09-19 | 2026-10-26 | TeX | 4 | 0 | 3 | 1 | 0 | 0 |
| Universcraft | PUBLIC | 2026-08-25 | 2026-09-20 | Rust | 43 | 0 | 0 | 67 | 0 | 0 |
| rusty-Fenris-CMRR | PUBLIC | 2026-10-11 | 2026-10-11 | Rust | 2 | 1 | 0 | 8 | 0 | 0 |
| rusty-SUNDIALS | PUBLIC | 2026-05-11 | 2026-10-26 | Rust | 272 | 75 | 75 | 157 | 1 | 1 |
| rusty-leveldb | PUBLIC | 2026-05-11 | 2026-05-11 | Rust | 3 | 0 | 0 | 85 | 0 | 0 |

### infrastructure/devops (6)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| HiveMind-home.github.ui | PUBLIC | 2026-10-24 | 2026-10-24 | None | 1 | 0 | 0 | 0 | 0 | 0 |
| HiveMindatHome.github.io | PUBLIC | 2026-10-24 | 2026-10-26 | HTML | 9 | 0 | 0 | 0 | 0 | 0 |
| runux-ai-runtime | PRIVATE | 2026-05-23 | 2026-09-27 | Python | 153 | 12 | 16 | 37 | 0 | 0 |
| rust-linux-mini-kernel | PUBLIC | 2026-05-15 | 2026-10-14 | HTML | 377 | 60 | 45 | 354 | 0 | 0 |
| xaviercallens.github.io | PUBLIC | 2026-10-25 | 2026-10-25 | HTML | 8 | 0 | 0 | 0 | 0 | 0 |
| xavuntu-AIRustLinux | PUBLIC | 2026-10-03 | 2026-10-03 | HTML | 5 | 0 | 50 | 355 | 0 | 0 |

### genetics/biology (2)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenCycloInitiative | PUBLIC | 2026-02-20 | 2026-02-21 | Python | 25 | 0 | 0 | 0 | 0 | 0 |
| SocrateAI-Scientific-Genetic | PUBLIC | 2026-10-20 | 2026-10-26 | TeX | 57 | 0 | 26 | 15 | 0 | 0 |

### education (2)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| liaspeaking | PUBLIC | 2025-11-01 | 2026-02-22 | Python | 1 | 0 | 0 | 0 | 0 | 0 |
| scikit-runux-tribute | PUBLIC | 2026-05-25 | 2026-09-22 | Python | 11 | 0 | 0 | 0 | 0 | 0 |

### fusion/plasma (1)

| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |
|---|---|---|---|---|---|---|---|---|---|---|
| SocrateAI-Scientific-FusionEnergy | PUBLIC | 2026-10-19 | 2026-10-19 | None | None | 0 | None | None | None | 0 |

## Science-relevant repositories

### AutoevolveAI [PUBLIC] (AI agents/methodology/verification)

Verification-first harness (ANSE) for LLM-agent science: gates must be able to fail, claims must trace to artifacts; hosts the local-LLM/Lean/GPU tooling used by the other projects. README says an internal audit found 14 components reporting success without doing the work; not peer reviewed.

- Created 2026-09-19, last push 2026-10-26; 352 commits and 7 merged PRs in window; disk 189959 KB; language Python.
- Lean 4: 164 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 57 .rs files, 3 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 688; TeX files: 118.
- Honesty/audit/status files: `docs/remediation/AUDIT_2026-09-25.md`, `docs/remediation/AUDIT_2026-09-26.md`, `docs/remediation/P0-7-status.md`, `docs/roadmap/RUNUX_HARDWARE_AUDIT_REPORT.md`
  - `docs/remediation/AUDIT_2026-09-25.md`: "**Scope:** commissioned as "analyse, audit and provide implementation plan" covering Claude Code hardening, MCP, ANSE v12, T4 model deployment, night dream training, Redis long-term memory with GCS backup, and GCP T4 deployment of the DeepSeek Lean solver + op"
  - `docs/remediation/AUDIT_2026-09-25.md`: "nvidia-smi -L    → NVIDIA-SMI has failed... couldn't communicate with the NVIDIA driver (exit 9)"
  - `docs/remediation/AUDIT_2026-09-25.md`: "**Fix package exists:** `linux-modules-nvidia-580-server-6.8.0-1067-gcp` (exact) and `linux-modules-nvidia-580-server-gcp` (candidate `6.8.0-1067.75~22.04.1+2`, **tracks the kernel**). Use the flavour metapackage — the version-pinned one guarantees the GPU dis"
  - `docs/remediation/AUDIT_2026-09-26.md`: "**Scope:** requested as "ensure the system is fully deployed and working" (GCP T4 VM, 2 disks, LTM, VectorDB, RAG, ANSE), followed by "commit, push, merge and release," followed by this audit. This document is the honest reconciliation of what actually happene"
  - `docs/remediation/AUDIT_2026-09-26.md`: "**Status: this audit supersedes and extends `AUDIT_2026-09-25.md`.** That document is still substantially correct and is not restated in full here — read both. This one adds: a self-reported release-integrity incident, reproduced gate failures, a card-ledger r"
  - `docs/remediation/AUDIT_2026-09-26.md`: "The 14 commits containing P1-1 through P4-1 exist **only** on `night/remediation-2026-09-25`. The `release/v12.4.0` branch was cut from `main` (post PR #1), not from `night/...`, and only added a version bump, `CHANGELOG.md`, and `DEPLOYMENT_REPORT.md`. **The "

### GWAYA-GwenLayaOpenModel [PUBLIC] (AI agents/methodology/verification)

Fail-closed verification gate for LLM-generated code (real compilers + sandboxed tests, AST stub auditing) with a paper and per-claim audits of its own numbers.

- Created 2026-10-03, last push 2026-10-25; 217 commits and 29 merged PRs in window; disk 18792 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 210; TeX files: 32.
- Honesty/audit/status files: `docs/CLAIM_AUDIT.md`, `docs/CLAIM_AUDIT_3100.md`, `docs/CLAIM_AUDIT_3120.md`, `docs/CLAIM_AUDIT_3120_author.md`, `docs/CLAIM_AUDIT_3130.md`, `docs/CLAIM_AUDIT_340.md`
  - `docs/CLAIM_AUDIT.md`: "Scope: `papers/gwenlaya_v4.tex` (line numbers below refer to it), `papers/gwenlaya_v4.bib`,"
  - `docs/CLAIM_AUDIT.md`: "- **C (external/citations), 19 rows.** Every cited work exists and its arXiv id, authors and year match. One bib entry is wrong: the gwayav3 title does not match the Zenodo record. One README badge is overstated."
  - `docs/CLAIM_AUDIT.md`: "**Fix:** either update to "7 lines, \$1.98 (sum of `usd_estimate` = 1.9809)" and add the two rows to the spend table, or pin the snapshot: "Read from `spend_ledger.jsonl` as of 2026-10-08 08:04 (its first 5 lines, \$1.54); two later lines (\$0.441, a post-v3.3"
  - `docs/CLAIM_AUDIT_3100.md`: "| A6 | hidden suites: LeetCode mean 98 assertions, FSB 3.4, BCB 5.6 test methods; 149 references did not verify | `manifest_F.json` `counts.python.hidden_tests_per_task_by_source`, `reports.python.sources.*.sanity_drops` | V. Hidden-suite means 98.0 / 3.4 / 5."
  - `docs/CLAIM_AUDIT_3100.md`: "| B6 | visible vs not visible CWR: 4B 0.124 vs 0.128, 9B 0.135 vs 0.135, 2B 0.067 vs 0.184 | `numbers_F_pm.json` `per_slice.python/gate_{visible,not_visible}` | X. Numbers V (0.124/0.128, 0.135/0.135, 0.067/0.184); **the reading is wrong (S1):** "does not show"
  - `docs/CLAIM_AUDIT_3120.md`: "`docs/CLAIM_AUDIT_3120_author.md` (same ids). V = recomputed and matches to printed precision; VN = verified with a stated caveat or only partly verifiable; X = mismatch or unsupported statement (correct value given)."
  - `docs/CLAIM_AUDIT_3120.md`: "| D6 | 1,968 steps, 1,522 s, router 581 s; 154 hard negatives in train | V. status.jsonl 1522 / 581 s; `feedback_report.json` 154 train, 46 held out; manifest 1,968 steps (train wall 1,458 s inside the 1,522 s step). The plan's "183 of 2,724" is the Python cou"
  - `docs/CLAIM_AUDIT_3120.md`: "| S8 | Section p2-bok, caveat on truncation | "(plan text)" for 690 / 26 / 1 / 85 | recomputed from rows: same values | sentence says recomputed by the audit; 2B and 4B truncation rates given |"

### HiveMind [PUBLIC] (AI agents/methodology/verification)

Decentralised sparse-MoE training/inference over volunteer GPUs (Steam/BOINC/DiLoCo style). README states the legacy scientific-swarm paths are synthetic simulations and the only real-token evidence is a tiny CPU smoke test.

- Created 2026-10-18, last push 2026-10-26; 474 commits and 127 merged PRs in window; disk 17713 KB; language Python.
- Lean 4: 3 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 144; TeX files: 2.
- Honesty/audit/status files: `docs/STEAM_STATUS.md`
  - `docs/STEAM_STATUS.md`: "The legacy `3133700` App ID and `3133701` Depot ID constants remain in runtime code and test fixtures as local development defaults so all unit and integration tests pass deterministically. Do not use `3133700` to publish to SteamPipe; replace it with your own"

### SocrateAI-Scientific-Agora [PRIVATE] (AI agents/methodology/verification)

Private multi-agent infrastructure/workspace of the SocrateAI Agora (large Lean+Rust+TeX tree); identical metrics to NewDiscoveries, probably the same repository under a former name.

- Created 2026-05-31, last push 2026-06-26; 36 commits and 7 merged PRs in window; disk 184610 KB; language TeX.
- Lean 4: 200 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 43 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 1; data files (csv/json/etc): 251; TeX files: 95.

### SocrateAI-Scientific-Communication [PUBLIC] (AI agents/methodology/verification)

Papers plus the reviews that examined them, organised by claim strength, including claims that did not survive.

- Created 2026-09-06, last push 2026-09-10; 20 commits and 0 merged PRs in window; disk 2847 KB; language TeX.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 6.

### SocrateAI-Scientific-Elenchus [PRIVATE] (AI agents/methodology/verification)

Private laboratory method + harness for AI-assisted science: cross-examine claims with tiers and refuting gates ('it removes false confidence, and that is all').

- Created 2026-09-18, last push 2026-09-20; 24 commits and 0 merged PRs in window; disk 635 KB; language Python.
- Lean 4: 9 .lean files, lakefile=no, lean-toolchain=yes. Rust: 1 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 80; TeX files: 0.

### SocrateAI-Scientific-Mathesis [PUBLIC] (AI agents/methodology/verification)

Stream 0 shared notation, verification kernel and epistemic ledger for the other streams; audit pack warns non-vacuous witnessed theorems can still be the wrong statement.

- Created 2026-08-13, last push 2026-08-25; 24 commits and 0 merged PRs in window; disk 751 KB; language Python.
- Lean 4: 13 .lean files, lakefile=no, lean-toolchain=yes. Rust: 3 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 3; TeX files: 1.
- Honesty/audit/status files: `docs/AUDIT_PACK.md`
  - `docs/AUDIT_PACK.md`: "non-vacuous, carry witnesses in both polarities, and still be the wrong statement — about a"
  - `docs/AUDIT_PACK.md`: "degenerate case, with a quantifier in the wrong order, or named after a theorem it does not"
  - `docs/AUDIT_PACK.md`: "**Does not say:** that these five tiers are the right five, or that "Literature" belongs"

### SocrateAI-Scientific-NewDiscoveries [PRIVATE] (AI agents/methodology/verification)

Private; same content/metrics as SocrateAI-Scientific-Agora (likely rename/duplicate).

- Created 2026-06-18, last push 2026-10-26; 36 commits and 0 merged PRs in window; disk 110548 KB; language TeX.
- Lean 4: 200 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 43 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 1; data files (csv/json/etc): 251; TeX files: 95.

### SocrateAI-Scientific-TNN-UniversModel [PUBLIC] (AI agents/methodology/verification)

Thermodynamic/topological tensor-NN 'Univers Model' with real-data registry; a certified audit renamed overclaimed items (e.g. 'Live Sonic Horizon Simulator' became a 1D advection-diffusion proxy).

- Created 2026-08-12, last push 2026-08-28; 68 commits and 0 merged PRs in window; disk 20727 KB; language Python.
- Lean 4: 13 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 1 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 42; TeX files: 13.
- Honesty/audit/status files: `specs/CERTIFIED_SCIENTIFIC_AUDIT_LAB1.md`, `specs/Lab-5_Audit_Memo.md`, `specs/REAL_DATA_AUDIT_LEDGER_AND_MODEL_REGISTRY.md`, `specs/Scientific_Audit_Ledger.md`, `specs/Scientific_Rigor_Audit.md`
  - `specs/CERTIFIED_SCIENTIFIC_AUDIT_LAB1.md`: "| **P1** | "Live Sonic Horizon Simulator" / "analogous to Hawking white hole" | Renamed "1D Advection-Diffusion Proxy". Honesty note in all files. | ✅ |"
  - `specs/CERTIFIED_SCIENTIFIC_AUDIT_LAB1.md`: "| **P4** | "Hamiltonian drift" misuses symplectic vocabulary | Renamed to **L2-Norm Drift** everywhere. Dissipative caveat added. | ✅ |"
  - `specs/CERTIFIED_SCIENTIFIC_AUDIT_LAB1.md`: "### Negative Control (Fr < 1, No Horizon)"
  - `specs/Lab-5_Audit_Memo.md`: "4. **Macroscopic Isometry (Scale-Invariance):** The formal proof that the P4 mechanism acts as a perfect isometry in the macroscopic regime, guaranteeing that the TDA pipeline does not artificially distort the large-scale structures of the physical datasets."
  - `specs/REAL_DATA_AUDIT_LEDGER_AND_MODEL_REGISTRY.md`: "| **1** | **Cosmologie & Matière Noire** | DESI DR1 (Télescope Mayall) | `scripts/real_data/desi_3d_coords.npy` | **12.0 Mo** | NumPy Tensor float32 | 10 000 galaxies $(X, Y, Z)$ | Coordonnées cartésiennes tridimensionnelles issues des décalages vers le rouge "
  - `specs/REAL_DATA_AUDIT_LEDGER_AND_MODEL_REGISTRY.md`: "| **4** | **Relevé Spatial Profond** | Télescope Spatial ESA Euclid | `/mnt/disks/disk-socrateai-local-1/SocrateAI-stream3-realdata/euclid/` | **944 Ko** | Tableaux CSV astronomiques | Champs profonds Fornax, North, South | Cartographie de lentillage gravitati"
  - `specs/REAL_DATA_AUDIT_LEDGER_AND_MODEL_REGISTRY.md`: "| **23** | **Sismologie & Failles** | IRIS EarthScope / USGS | 400 Hypocentres & Magnitudes | `RateAndStateSeismicTNN` | $\\beta_1 = 39$ | Friction Dieterich-Ruina | $3.09 \\times 10^{-4}$ | ✅ CONVERGED |"

### SocrateAI-thesisautoresearch [PRIVATE] (AI agents/methodology/verification)

Private autonomous research / DBA thesis copilot with Lean 4, Z3 and RAG tracks (high-level only).

- Created 2026-05-21, last push 2026-05-24; 86 commits and 1 merged PRs in window; disk 202661 KB; language HTML.
- Lean 4: 18 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 117; TeX files: 9.

### SuperGravity [PUBLIC] (AI agents/methodology/verification)

Zero-trust gateway and continuous self-improvement framework for agentic coding, built on AutoevolveAI/ANSE and Lean.

- Created 2026-09-20, last push 2026-09-20; 12 commits and 0 merged PRs in window; disk 2500 KB; language Python.
- Lean 4: 11 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 18; TeX files: 0.

### amcp [PUBLIC] (AI agents/methodology/verification)

Agent Mesh Communication Protocol v1.5 enterprise edition: Java framework for mobile agents with LLM orchestration.

- Created 2025-09-24, last push 2026-10-25; 2 commits and 7 merged PRs in window; disk 1367 KB; language Java.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.
- Honesty/audit/status files: `PROJECT_STATUS.md`

### amcp-v1.5-opensource [PUBLIC] (AI agents/methodology/verification)

Open-source edition of the AMCP Java agent framework; status file reports 14 tests, 0 failures.

- Created 2025-09-27, last push 2026-10-25; 0 commits and 2 merged PRs in window; disk 25172 KB; language Java.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.
- Honesty/audit/status files: `AMCP_DEPLOYMENT_STATUS.md`, `COMPILATION_TEST_STATUS_REPORT.md`, `GITHUB_ACTIONS_DEPLOYMENT_STATUS.md`, `PROJECT_STATUS.md`
  - `COMPILATION_TEST_STATUS_REPORT.md`: "Tests run: 14, Failures: 0, Errors: 0, Skipped: 0"
  - `COMPILATION_TEST_STATUS_REPORT.md`: "- ✅ **Examples Module**: 14 tests run, 0 failures, 0 errors"
  - `COMPILATION_TEST_STATUS_REPORT.md`: "- ✅ **CLI Module**: No test failures"

### attentionmatter [PRIVATE] (AI agents/methodology/verification)

Private proof of concept for attention-inspired prompt token reduction (README claims 30-56% reduction; not independently checked here).

- Created 2026-06-25, last push 2026-06-25; 12 commits and 0 merged PRs in window; disk 736 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 1; TeX files: 1.

### nSymboCoder [PRIVATE] (AI agents/methodology/verification)

Private sub-1B neuro-symbolic code-model concept.

- Created 2026-05-10, last push 2026-05-10; 1 commits and 0 merged PRs in window; disk 28 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### xAuraOS [PUBLIC] (AI agents/methodology/verification)

Local-first 'cognitive operating substrate' (AuraOS): governed agent runtime with verifiers and capability leases; huge commit count (2,157), includes its own deep audit.

- Created 2026-08-06, last push 2026-08-06; 2157 commits and 0 merged PRs in window; disk 343980 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 7 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 157; TeX files: 1.
- Honesty/audit/status files: `DEEP_AUDIT_REPORT.md`, `PHASE_C3_STATUS.md`, `docs/AURA_MODEL_COGNOME_MR0_MR1_STATUS.md`, `docs/AURA_PHASE_AND_AUDIT_COCKPIT.md`, `docs/AURA_PHASE_C2_IMPLEMENTATION_STATUS.md`, `forged_roots_audit.md`
  - `DEEP_AUDIT_REPORT.md`: "self.log_error("DB_WRITE_FAIL", str(e))"
  - `DEEP_AUDIT_REPORT.md`: "**Impact:** Inconsistent error handling makes debugging difficult and can lead to silent failures"
  - `DEEP_AUDIT_REPORT.md`: "2. **Add Circuit Breakers**: For cloud API calls to prevent cascading failures"
  - `PHASE_C3_STATUS.md`: "Current implementation scope:"

### DarkMatterK3-Home.github.io [PUBLIC] (cosmology)

Proposed distributed-computing project to test whether cosmic-web topology matches K3 moduli-space (Picard-Fuchs) structure; repo also holds the self-audits that gate-failed the laboratory-scale re-scope.

- Created 2026-07-04, last push 2026-10-11; 380 commits and 22 merged PRs in window; disk 279491 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 159; TeX files: 20.
- Honesty/audit/status files: `DATA_INTEGRITY_AUDIT.md`, `LESSONS_LEARNED.md`, `WP_A2_CIRCULARITY_AUDIT.md`, `briefs/D0_VERIFICATION/D0C_ENV_AUDIT.md`, `briefs/DEEPTHINK_DEBRIEF_AUDIT_2026_07_28.md`, `briefs/DEEPTHINK_DEBRIEF_AUDIT_2026_07_29.md`
  - `LESSONS_LEARNED.md`: "# Lessons Learned: V5 Deep Review & Pivot (2026-07-14)"
  - `LESSONS_LEARNED.md`: "**Lesson**: Every numeric constant must be verified against an external"
  - `LESSONS_LEARNED.md`: "- No hardcoding of raw values from unverified sources"
  - `DATA_INTEGRITY_AUDIT.md`: "- Latest Q1 2026 data from Euclid space telescope"
  - `DATA_INTEGRITY_AUDIT.md`: "- **Euclid Q1 Mission Data** (48.6%) — Latest space telescope observations"
  - `WP_A2_CIRCULARITY_AUDIT.md`: "# WP_A2_CIRCULARITY_AUDIT.md — Gate 0 of the Laboratory-Scale Re-Scope: FAIL"
  - `WP_A2_CIRCULARITY_AUDIT.md`: "**Honest outcome up front:** **FAIL.** No region of the B1 window is simultaneously"
  - `WP_A2_CIRCULARITY_AUDIT.md`: "hypothesis; a clean negative, reported with the same prominence as a positive."

### SocrateAI-Dual-Scale-Agora-Lab [PUBLIC] (cosmology)

Near-empty README-level repo describing the Dual-Scale Agora lab aim; no code.

- Created 2026-08-14, last push 2026-08-15; 2 commits and 0 merged PRs in window; disk 255 KB; language None.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal [PUBLIC] (cosmology)

Stream 1 of the Dual-Scale Topological Universe Model: Lean 4 formalisation of arithmetic/lattice claims (Tier A kernel-checked, Tier B conjectural); several early headline claims were retracted in July 2026.

- Created 2026-07-15, last push 2026-10-10; 196 commits and 7 merged PRs in window; disk 16776 KB; language Lean.
- Lean 4: 47 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 1; data files (csv/json/etc): 19; TeX files: 41.
- Honesty/audit/status files: `STATUS_2026-07-24_PHASE_SETUP_COMPLETE.md`, `briefs/P1_DRAFT_STATUS_2026_07_29.md`, `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`, `briefs/STREAM2_EFT_ESCALATION_STATUS.md`, `briefs/WP_B_LEAN_ORACLE_AUDIT_2026_07_31.md`
  - `STATUS_2026-07-24_PHASE_SETUP_COMPLETE.md`: "> verified, geometry predictable) were retracted on 2026-07-25 — see"
  - `STATUS_2026-07-24_PHASE_SETUP_COMPLETE.md`: "| **S1-07 (Vacuous axioms)** | ✅ CLOSED | Completed | No |"
  - `STATUS_2026-07-24_PHASE_SETUP_COMPLETE.md`: "- Review brief with scope & directives"
  - `briefs/P1_DRAFT_STATUS_2026_07_29.md`: "- **(iii) U1, T ≅ U⊕⟨14⟩, Tier B** — `06-lattice.tex` Proposition `prop:usplit` (unconditional"
  - `briefs/P1_DRAFT_STATUS_2026_07_29.md`: "statement about the exhibited Gram matrix) + `08-dolgachev-doran.tex` (conditional"
  - `briefs/P1_DRAFT_STATUS_2026_07_29.md`: "either wrong would be a real overclaim:"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "| S1-11 | s10/s18 partner series **NOT integral** — complete proofs, witnesses `17/2`, `45/2` at n=2. s7 partner integrality: **PASS(7) only**, general case = named open goal. Two vacuous S1-03 "integrality" theorems disclosed (F6, README). | A / PASS(7) |"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "The candidate-separation picture, stated with its honest asymmetry: **s10/s18 partners are"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "s7 avoiding it is the anomaly and is verified PASS(7)/PASS(81-CAS), not proved.**"

### SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2 [PUBLIC] (cosmology)

Small prototype linking Python tensor optimisation to a Lean 4 JSON-RPC daemon for K3 x T^2 compactification search.

- Created 2026-07-28, last push 2026-07-28; 9 commits and 0 merged PRs in window; disk 210 KB; language Python.
- Lean 4: 4 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 36; TeX files: 0.

### SocrateAI-Scientific-Agora-K3-DarkMatter [PUBLIC] (cosmology)

Dual-scale topological universe model repo: Cooper s7/s10 operator identities proved in Lean, attempted K3/dark-matter links; README discloses that C1/C2 lattice numbers were retracted.

- Created 2026-06-25, last push 2026-10-10; 485 commits and 62 merged PRs in window; disk 57301 KB; language Python.
- Lean 4: 64 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 3; data files (csv/json/etc): 123; TeX files: 33.
- Honesty/audit/status files: `PROOF_STATUS.txt`, `archive/pre-ledger/CAVEATS.md`, `archive/pre-ledger/CURRENT_SESSION_CONTINUATION_STATUS.md`, `archive/pre-ledger/PROJECT_STATUS_TRACKER.md`, `briefs/EXTERNAL_REVIEW_FABLE51_AUDIT_AND_DIRECTIONS_2026_09_27.md`, `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`
  - `PROOF_STATUS.txt`: "Scope:  Cooper s7 (bulk A183204, partner A279619) and s10 (bulk A005260, rational partner)."
  - `PROOF_STATUS.txt`: "Epistemic scope (VISION §2): This is a MATHEMATICAL operator identity only."
  - `PROOF_STATUS.txt`: "It does NOT establish any bulk<->brane physical coupling; that interpretation"
  - `briefs/EXTERNAL_REVIEW_FABLE51_AUDIT_AND_DIRECTIONS_2026_09_27.md`: "- The review's own caveat: "literature identifiers below are from memory and should be pinned before"
  - `briefs/EXTERNAL_REVIEW_FABLE51_AUDIT_AND_DIRECTIONS_2026_09_27.md`: "| # | review clause (Stream-2 scope) | source of confirmation |"
  - `briefs/EXTERNAL_REVIEW_FABLE51_AUDIT_AND_DIRECTIONS_2026_09_27.md`: "**Findings in band (not failures of the review):**"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "| S1-11 | s10/s18 partner series **NOT integral** — complete proofs, witnesses `17/2`, `45/2` at n=2. s7 partner integrality: **PASS(7) only**, general case = named open goal. Two vacuous S1-03 "integrality" theorems disclosed (F6, README). | A / PASS(7) |"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "The candidate-separation picture, stated with its honest asymmetry: **s10/s18 partners are"
  - `briefs/STREAM1_S1_10_11_12_STATUS_AND_UNBLOCK_2026_07_26.md`: "s7 avoiding it is the anomaly and is verified PASS(7)/PASS(81-CAS), not proved.**"

### SocrateAI-Scientific-AutoEvolve-K3xT2 [PUBLIC] (cosmology)

AlphaEvolve-style evolutionary search for K3 x T^2 cosmology models with DESI BAO likelihood and nested sampling; docs say no definitive empirical discovery claimed and record a decisive NANOGrav refutation of one spectrum.

- Created 2026-07-29, last push 2026-10-25; 144 commits and 1 merged PRs in window; disk 41998 KB; language Python.
- Lean 4: 7 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 408; TeX files: 22.
- Honesty/audit/status files: `brief/euclid_q1_data_audit_certificate.md`, `docs/EPISTEMIC_STATUS_AND_EVIDENCE_SYNTHESIS.md`, `docs/PEER_REVIEW_AUDIT_REPORT.md`, `specs/phase10_math_physics_audit.md`, `specs/phase10_physics_audit_and_lowtier_plan.md`, `specs/phase11_scientific_rigor_audit.md`
  - `docs/EPISTEMIC_STATUS_AND_EVIDENCE_SYNTHESIS.md`: "> - **We do not yet claim definitive empirical *discovery* in the strict laboratory sense** (definitive physical confirmation requires primary measurements from LiteBIRD, DUNE, or HERA)."
  - `docs/EPISTEMIC_STATUS_AND_EVIDENCE_SYNTHESIS.md`: "3. **NANOGrav 15-Year Refutation Check (Self-Correction)**:"
  - `docs/EPISTEMIC_STATUS_AND_EVIDENCE_SYNTHESIS.md`: "- The framework demonstrated self-correcting rigor: testing an unconstrained steep primordial axion spectrum ($\gamma = 4.847$) against NANOGrav 15-year PTA data resulted in decisive refutation ($\ln B = -51.58$), confirming that the observed nHz stochastic ba"

### SocrateAI-Wolfram-Hypergraph [PUBLIC] (cosmology)

Computation-augmented-generation proof of concept for Wolfram-hypergraph dark-matter cosmology; brief says it does not claim to have discovered particles.

- Created 2026-07-28, last push 2026-08-03; 41 commits and 0 merged PRs in window; disk 24524 KB; language Python.
- Lean 4: 13 .lean files, lakefile=yes, lean-toolchain=no. Rust: 3 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 354; TeX files: 2.
- Honesty/audit/status files: `brief/deepmind_scientific_audit_brief.md`
  - `brief/deepmind_scientific_audit_brief.md`: "- We do not claim to have "discovered" physical particles."
  - `brief/deepmind_scientific_audit_brief.md`: "- $K_3$: Evaporates completely to $0$ edges (sub-threshold dispersion / "failed halo")."

### TIC4206066-Exoplanet-Verification [PUBLIC] (cosmology)

Independent adversarial re-analysis (refutation gates with positive/negative controls) of a third party's TESS exoplanet candidate TIC 4206066 b, with Lean checks and a Zenodo data package.

- Created 2026-10-11, last push 2026-10-11; 12 commits and 0 merged PRs in window; disk 18653 KB; language Python.
- Lean 4: 2 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 1021; TeX files: 0.
- Honesty/audit/status files: `data/zenodo/part2/07_signal_B/from_T5_signal_B/audit_final_params_B_dump.txt`, `data/zenodo/part3/10_environment/pip_freeze_audit_env.txt`, `data/zenodo/part3/13_supporting_pipelines/PUBLICATION_AUDIT/METHOD_AUDIT.md`, `data/zenodo/part3/13_supporting_pipelines/PUBLICATION_AUDIT/logs/audit_env_freeze.txt`, `data/zenodo/part3/13_supporting_pipelines/pubprep/METHOD_AUDIT.md`, `data/zenodo/part3/13_supporting_pipelines/pubprep/UNRESOLVED_LIMITATIONS.md`
  - `data/zenodo/part3/13_supporting_pipelines/PUBLICATION_AUDIT/METHOD_AUDIT.md`: "| Teff | TIC 8.2 4010 ± 120; Mann+2015 erratum Table 2 V−J relation 4048 ± 86 (3984 with [Fe/H] = −0.27); ARIADNE 4012 +45/−40; Gaia DR2 Apsis 4069. GSP-Spec 4182 rejected (extrapolation flag, logg 5.01). | **4030 ± 90 K** | 4080 ± 100 | CORRECTED |"
  - `data/zenodo/part3/13_supporting_pipelines/PUBLICATION_AUDIT/METHOD_AUDIT.md`: "injection σ to ~10 %, which does not change any conclusion (all excluded stars are ≥ 8σ away). Neighbour hypotheses: fixed-position fits and"
  - `data/zenodo/part3/13_supporting_pipelines/PUBLICATION_AUDIT/METHOD_AUDIT.md`: "page (no TOI/CTOI/files/notes), NASA toi by TIC (0 rows), exo.MAST TCEs (`{"TCE":[]}`) — all negative. arXiv API and"

### SocrateAI-Scientific-FusionEnergy [PUBLIC] (fusion/plasma)

Empty repository (created 2026-10-19) reserved for fusion work; no content in the repo itself.

- Created 2026-10-19, last push 2026-10-19; None commits and 0 merged PRs in window; disk 0 KB; language None.
- Lean 4: None .lean files, lakefile=no, lean-toolchain=no. Rust: None .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: None; data files (csv/json/etc): None; TeX files: None.

### OpenCycloInitiative [PUBLIC] (genetics/biology)

Design documents for an open-source algae photobioreactor unit (cyclo-vortex hydrodynamics); documentation-level, 25 commits over two days.

- Created 2026-02-20, last push 2026-02-21; 25 commits and 0 merged PRs in window; disk 414 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 7; TeX files: 0.

### SocrateAI-Scientific-Genetic [PUBLIC] (genetics/biology)

Lean 4 + Python/Rust hub for reverse transcription, chromatin remodelling and E8 dicodon ideas; AUDIT_2026-10-21 records a model-output (POLE P286R TMB) as not an observation and a refuted stage-removal model class.

- Created 2026-10-20, last push 2026-10-26; 57 commits and 0 merged PRs in window; disk 25236 KB; language TeX.
- Lean 4: 26 .lean files, lakefile=no, lean-toolchain=no. Rust: 15 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 73; TeX files: 26.
- Honesty/audit/status files: `docs/AUDIT_2026-10-21.md`, `docs/CONTROVERSY_AND_EPISTEMIC_AUDIT.md`
  - `docs/AUDIT_2026-10-21.md`: "Scope: Papers D and E, University Textbook, Lean files, `data/*peer_review.json`."
  - `docs/AUDIT_2026-10-21.md`: "4. **POLE P286R TMB 12500/9 mut/Mb** is a model output, not an observation. *Labelled, then tested and refuted — see below.*"
  - `docs/AUDIT_2026-10-21.md`: "6. **GAR.H15's mechanism for POLE P286R is refuted** (edition 3). Not a parameter problem: the whole stage-removal model class fails. See below."
  - `docs/CONTROVERSY_AND_EPISTEMIC_AUDIT.md`: "Every mathematical and biological claim in **`SocrateAI-Scientific-Genetic`** undergoes a 5-round adversarial peer-review tribunal led by **`claude-opus-4-6`** (co-synthesized with **`gemini-4-argon`**) enforcing the 6 external referee hardness gates (`ARGOS-P"
  - `docs/CONTROVERSY_AND_EPISTEMIC_AUDIT.md`: "- **`ARGOS-PEER-009` (Mathematical Honesty & Precise Naming):** Every theorem title matches the exact algebraic/analytic object proved in Lean 4."

### Mirror-Map-Sieve [PUBLIC] (mathematics)

Exploratory preprint and pipeline studying one weight-5 Apery-like binomial sum S20(n) and its possible Calabi-Yau-operator interpretation; README says explicitly 'We do not claim a discovery'.

- Created 2026-06-18, last push 2026-07-12; 101 commits and 1 merged PRs in window; disk 49380 KB; language Python.
- Lean 4: 18 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 1; data files (csv/json/etc): 52; TeX files: 18.

### OptimalEnergyAI [PRIVATE] (mathematics)

Applies the triangular-lattice universal-optimality result as a design idea for latent geometry in ML: Lean 4 spec, three CPU proof-of-concept experiments (hexagonal vs square grid, E8 vs Z^8 quantiser), plus business/IP planning docs. Private; no real-data PoC yet per README.

- Created 2026-10-12, last push 2026-10-17; 38 commits and 10 merged PRs in window; disk 4177 KB; language TeX.
- Lean 4: 10 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 101; TeX files: 21.

### SocrateAI-CohnKumar-8D-Numeric [PUBLIC] (mathematics)

Empty repo (created 2026-10-11) reserved for 8D Cohn-Kumar numerics; no content.

- Created 2026-10-11, last push 2026-10-11; None commits and 0 merged PRs in window; disk 0 KB; language None.
- Lean 4: None .lean files, lakefile=no, lean-toolchain=no. Rust: None .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: None; data files (csv/json/etc): None; TeX files: None.

### SocrateAI-Lean-Lib [PUBLIC] (mathematics)

Lean 4 library of 14 'domains' / 40+ modules claimed zero-sorry with an axiom-audit report; 'computational zero axioms' checks are theorems about specific numbers.

- Created 2026-09-05, last push 2026-09-10; 12 commits and 1 merged PRs in window; disk 1343 KB; language Lean.
- Lean 4: 114 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 2; TeX files: 0.
- Honesty/audit/status files: `docs/AXIOM_AUDIT_REPORT.md`
  - `docs/AXIOM_AUDIT_REPORT.md`: "| `SocrateAI.AlienMath.KalChargingMatrix` | `charging_potential_nonnegative` | `COMPUTATIONAL_ZERO_AXIOMS` | `None (0)` | ✅ PASS |"
  - `docs/AXIOM_AUDIT_REPORT.md`: "| `SocrateAI.ChameleonGravity.DACModel` | `regime_II_mass_negative` | `COMPUTATIONAL_ZERO_AXIOMS` | `None (0)` | ✅ PASS |"
  - `docs/AXIOM_AUDIT_REPORT.md`: "| `SocrateAI.Core.ReferenceTheorems` | `desi_wa_is_negative` | `COMPUTATIONAL_ZERO_AXIOMS` | `None (0)` | ✅ PASS |"

### SocrateAI-Lean-Verification [PRIVATE] (mathematics)

Private Lean 4 library on tensor rank / asymptotic algebra / 'Kal Alien Mathematics' (high-level only).

- Created 2026-06-13, last push 2026-06-13; 1 commits and 0 merged PRs in window; disk 5012 KB; language Lean.
- Lean 4: 56 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 1; data files (csv/json/etc): 4; TeX files: 11.

### SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic [PUBLIC] (mathematics)

Automated pipeline on K3xT^2, mock modular forms and hydrodynamic limits; huge Lean tree (4,471 .lean files, likely generated).

- Created 2026-08-09, last push 2026-08-28; 91 commits and 0 merged PRs in window; disk 100620 KB; language Lean.
- Lean 4: 4471 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 38; TeX files: 99.

### SocrateAI-Scientific-AlienMathematics-Foundation [PUBLIC] (mathematics)

Retrospective of a June 2026 AI-driven 'alien mathematics' exploration: self-described failures, one claimed publishable result, lessons.

- Created 2026-06-08, last push 2026-06-13; 2 commits and 0 merged PRs in window; disk 2841 KB; language Python.
- Lean 4: 16 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 7; TeX files: 3.

### SocrateAI-Scientific-MechanicaFluidorum [PUBLIC] (mathematics)

Staged verifier-in-the-loop programme on 3D Navier-Stokes regularity around 'Hypothesis U' (enstrophy control of truncated system); audit packet says a 'no' answer or killed track counts as success; Hypothesis U not proved.

- Created 2026-08-12, last push 2026-10-25; 177 commits and 1 merged PRs in window; disk 10501 KB; language Python.
- Lean 4: 16 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 3 .rs files, 3 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 59; TeX files: 3.
- Honesty/audit/status files: `docs/AUDIT_PACKET.md`, `docs/designs/DOOR2_MEMO_SIGN_AUDIT.md`, `docs/escalations/2026-09-12-E3-stray-premature-audit-error.txt`, `docs/harness/agent-claim-auditor.md`, `docs/harness/agent-manuscript-auditor.md`, `docs/proposals/openai-audit-PROVENANCE.md`
  - `docs/AUDIT_PACKET.md`: "> the executed pivot in `PLAN.md` §10. Do not audit against this packet's commit again —"
  - `docs/AUDIT_PACKET.md`: "commits are outside this packet's scope."
  - `docs/AUDIT_PACKET.md`: "**A "no" answer is a success, not a failure.** This programme's Definition of Done explicitly"
  - `docs/designs/DOOR2_MEMO_SIGN_AUDIT.md`: "With `uₙ(0) ≥ 0` and `gₙ ≥ 0`, every term is non-negative and positivity is preserved. The"
  - `docs/designs/DOOR2_MEMO_SIGN_AUDIT.md`: "**S2 — the interpolation is a case analysis on orderings of non-negative reals.** The text"
  - `docs/designs/DOOR2_MEMO_SIGN_AUDIT.md`: "`c₂ > 0`. For non-negative data the cross term is `≥ 0`, so `H ≥ ‖u‖²_γ`: **`H` dominates the"
  - `docs/escalations/2026-09-12-E3-stray-premature-audit-error.txt`: "/home/xavkal/xdev/SocrateAI-Scientific-MechanicaFluidorum/docs/proposals/openai-axiom-audit.lean:21:0: error: object file '/home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler/.lake/build/lib/lean/NavierStokes/ComparatorR3Theorem.olean' of module Nav"

### SocrateAI-Scientific-Mensura [PUBLIC] (mathematics)

Tier-B exact-arithmetic and numerical companion to the Navier-Stokes Lean programme.

- Created 2026-08-14, last push 2026-08-25; 38 commits and 0 merged PRs in window; disk 4511 KB; language Python.
- Lean 4: 3 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 1 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 37; TeX files: 4.

### SocrateAI-Scientific-Poly-Algebraic-Calculus [PUBLIC] (mathematics)

Single-commit placeholder with only an abstract of a proposed 'Poly-Algebraic Calculus'.

- Created 2026-08-11, last push 2026-08-11; 1 commits and 0 merged PRs in window; disk 1 KB; language None.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### triangular-universal-optimality-lean [PUBLIC] (mathematics)

Kernel-checked Lean 4 corollaries of the upstream openai/math triangular-lattice universal-optimality theorem, opened for red-team review; LIMITATIONS.md says it is not a proof of the conjecture and uses a weaker optimality notion.

- Created 2026-10-11, last push 2026-10-22; 18 commits and 3 merged PRs in window; disk 1641 KB; language TeX.
- Lean 4: 9 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 32; TeX files: 4.
- Honesty/audit/status files: `LIMITATIONS.md`, `verification/manuscript_audit_2026-10-11.md`
  - `LIMITATIONS.md`: "| # | Limitation | Consequence |"
  - `LIMITATIONS.md`: "| L2 | `UniversallyOptimal` (D3) uses lower energy (liminf). CKMRV Def. 1.2–1.3 also require the energy to exist as a limit. | Our notion is weaker than CKMRV's. We do not claim it is *strictly* weaker, because we have no witness. |"
  - `LIMITATIONS.md`: "| L3 | Upstream does not claim the per-potential form of Cohn–Kumar (a sharp auxiliary function for each potential). | Neither do we. |"

### SocrateAI-Numeric-DualScale-Solver [PUBLIC] (numerics/software)

LeanFlow: pseudo-spectral 2D/3D Navier-Stokes solver with a dyadic shell sub-grid model, Rust crates + Lean 4 certificates, and a codebase audit that fixed tautological negative controls.

- Created 2026-08-30, last push 2026-09-22; 51 commits and 0 merged PRs in window; disk 43038 KB; language Python.
- Lean 4: 40 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 23 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 52; TeX files: 20.
- Honesty/audit/status files: `.agents/agents/fsi_multiphysics_auditor.md`, `.agents/agents/licensing_audit_agent.md`, `.agents/agents/qa_scientific_auditor.md`, `reports/codebase_audit_and_improvement_plan.md`
  - `reports/codebase_audit_and_improvement_plan.md`: "**Scope:** Full Codebase Inspection (`lean4/`, `crates/`, `src/dualscale_solver/`, `tests/`, `scripts/verify.sh`, Governance & Documentation)"
  - `reports/codebase_audit_and_improvement_plan.md`: "1. **Remediated Epistemic Vulnerabilities (Phase 8 Negative Controls):** Tautological local literal checks were replaced by an authoritative validation engine (`AuditGateEnforcer`), properly rejecting corrupted payloads for HIL latency, CAD non-manifold topolo"
  - `reports/codebase_audit_and_improvement_plan.md`: "5. **Scientific Report & Nomenclature Alignment:** Resolved inline formula contradictions in the LaTeX abstract ($\Omega(t) \le 1/\alpha'$ removed in favor of exact $\Omega(t) \le \Omega(0)$) and renamed VAD performance claims to "Surrogate Optimization / Dire"

### SocrateAI-Numeric-DualScale-Solver-Enterprise [PRIVATE] (numerics/software)

Private near-copy of the LeanFlow NS solver repository (high-level only).

- Created 2026-08-31, last push 2026-09-18; 58 commits and 3 merged PRs in window; disk 43224 KB; language Python.
- Lean 4: 40 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 69 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 54; TeX files: 20.

### SocrateAI-Scientific-Agora-LeanFlow [PRIVATE] (numerics/software)

Private planning repository for a general MCP server for stiff solvers, TDA and Lean-checked data certificates; README: 'There is no server code yet'.

- Created 2026-09-19, last push 2026-10-26; 4 commits and 0 merged PRs in window; disk 799 KB; language TeX.
- Lean 4: 3 .lean files, lakefile=no, lean-toolchain=no. Rust: 1 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 1.

### Universcraft [PUBLIC] (numerics/software)

Rust procedural-engine (HoloEngine) for multi-scale world rendering; software project with physics-flavoured claims, not a research result.

- Created 2026-08-25, last push 2026-09-20; 43 commits and 0 merged PRs in window; disk 114129 KB; language Rust.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 67 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 13; TeX files: 0.
- Honesty/audit/status files: `specs/Lab-5_Audit_Memo.md`
  - `specs/Lab-5_Audit_Memo.md`: "4. **Macroscopic Isometry (Scale-Invariance):** The formal proof that the P4 mechanism acts as a perfect isometry in the macroscopic regime, guaranteeing that the TDA pipeline does not artificially distort the large-scale structures of the physical datasets."

### rusty-Fenris-CMRR [PUBLIC] (numerics/software)

Small Rust crate relaxing 2D mesh nodes under a Yukawa repulsion using the local rusty-SUNDIALS CVODE; README status says early version.

- Created 2026-10-11, last push 2026-10-11; 2 commits and 1 merged PRs in window; disk 20 KB; language Rust.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 8 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### rusty-SUNDIALS [PUBLIC] (numerics/software)

AI-assisted pure-Rust translation of SUNDIALS CVODE (ODE/stiff solver, ~500 MB tree) with Lean specification files; used as the numerics backbone for other projects.

- Created 2026-05-11, last push 2026-10-26; 272 commits and 75 merged PRs in window; disk 502637 KB; language Rust.
- Lean 4: 75 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 157 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 1; data files (csv/json/etc): 281; TeX files: 14.

### rusty-leveldb [PUBLIC] (numerics/software)

Rust LevelDB port derived from a fork of dermesser/leveldb-rs; not science.

- Created 2026-05-11, last push 2026-05-11; 3 commits and 0 merged PRs in window; disk 614 KB; language Rust.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 85 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 1; TeX files: 0.

### OpenAI-NSE-Epistemic-Audit [PUBLIC] (physics)

Audit of the OpenAI Navier-Stokes/Euler Lean 4 blow-up proof read physically (Knudsen-number / continuum-assumption analysis) plus follow-up improvement plan; a later note withdraws earlier 'physical vacuity/censorship' wording.

- Created 2026-09-10, last push 2026-09-19; 132 commits and 0 merged PRs in window; disk 33975 KB; language Python.
- Lean 4: 22 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 20 .rs files, 3 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 5; data files (csv/json/etc): 40; TeX files: 9.
- Honesty/audit/status files: `02_Empirical_Observation/SECTION_1_INVESTIGATION_PHYSICS_AUDIT.md`, `05_Community_Research_Directions/DUALSCALE_ASSESSMENT_AND_NEXT_DIRECTIONS.md`, `AUDIT_AND_IMPROVEMENT_PLAN.md`
  - `AUDIT_AND_IMPROVEMENT_PLAN.md`: "> proofs are correct and this project reads them physically rather than refuting them. Withdrawn, wherever"
  - `AUDIT_AND_IMPROVEMENT_PLAN.md`: "> they appear below: "physical vacuity", thermodynamic/topological "censorship" (including the Lean files"
  - `AUDIT_AND_IMPROVEMENT_PLAN.md`: "- In `PhysLibThermodynamicCensorship.lean` (line 136), the proposition `physlib_admissible_non_vacuous` is declared as an `axiom`, despite the file header stating "0 custom axioms"."
  - `02_Empirical_Observation/SECTION_1_INVESTIGATION_PHYSICS_AUDIT.md`: "> "interception" theorem rested on an underived global enstrophy bound and is an unverified draft. OpenAI's proofs"
  - `02_Empirical_Observation/SECTION_1_INVESTIGATION_PHYSICS_AUDIT.md`: "that model describes a real fluid. It is a physical reading of a correct theorem, not a refutation, and it says"
  - `02_Empirical_Observation/SECTION_1_INVESTIGATION_PHYSICS_AUDIT.md`: "| `directive2_thermodynamic_paradox.py` | local energy density | $e_{\text{local}}\sim\tau^{-1.010}\to\infty$ | the decoupled-temperature assumption fails |"
  - `05_Community_Research_Directions/DUALSCALE_ASSESSMENT_AND_NEXT_DIRECTIONS.md`: "**Scope:** `~/xdev/SocrateAI-Numeric-DualScale-Solver`, `~/xdev/runux-ai-runtime`,"
  - `05_Community_Research_Directions/DUALSCALE_ASSESSMENT_AND_NEXT_DIRECTIONS.md`: "deconstruction" points fail)"
  - `05_Community_Research_Directions/DUALSCALE_ASSESSMENT_AND_NEXT_DIRECTIONS.md`: "### 1.2 Physical claims that are overclaims"

### SocrateAI-Scientific-Agora-LeanMaster [PUBLIC] (physics)

Lean 4 + Mathlib formalisation of T-duality, double field theory, K3 x T^2 lattices and Mathieu-moonshine arithmetic; README revised after an audit found over-claims ('first fully certified String Theory' withdrawn).

- Created 2026-09-12, last push 2026-10-25; 191 commits and 5 merged PRs in window; disk 95383 KB; language Lean.
- Lean 4: 887 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 1 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 1; data files (csv/json/etc): 1010; TeX files: 79.
- Honesty/audit/status files: `contrib/openai_math_corollaries/audit/autoresearch_2026-10-25/H9/AUDIT.md`, `contrib/openai_math_corollaries/audit/triangular/ledger/manuscript_audit_2026-10-11.md`, `contrib/openai_math_corollaries/papers/ar_bogoliubov_sk/AUDIT.md`, `contrib/openai_math_corollaries/papers/ar_dipolar_exciton/AUDIT.md`, `contrib/openai_math_corollaries/papers/ar_keldysh_tmd/AUDIT.md`, `contrib/openai_math_corollaries/papers/ar_sigma3_enstrophy/AUDIT.md`
  - `papers/publication/axiom_audit_log.txt`: "'DoubleFieldTheory.K3Topology.k3_euler_characteristic' does not depend on any axioms"
  - `papers/publication/axiom_audit_log.txt`: "'DoubleFieldTheory.K3Topology.k3_atiyah_singer_dirac_index' does not depend on any axioms"
  - `papers/publication/axiom_audit_log.txt`: "'DualScaleValidation.Observables.tensor_to_scalar_ratio_reduction' does not depend on any axioms"
  - `contrib/openai_math_corollaries/papers/ar_bogoliubov_sk/AUDIT.md`: "Date: 2026-10-25. Scope: `main.tex`/`main.pdf`, `gen_numbers.tex`, `gen_inputs.py`, `ledger/`, `publication_meta.json`, `data/`,"
  - `contrib/openai_math_corollaries/papers/ar_bogoliubov_sk/AUDIT.md`: "comes from a result file. The tiers are honest, and the citations are real and quoted faithfully. The"
  - `contrib/openai_math_corollaries/papers/ar_bogoliubov_sk/AUDIT.md`: "- `s4_strict : sBog 1 1 2 < √(2/(2·1))`. The bound is strict away from `k = ks`, so it does not hold trivially as an equality."
  - `contrib/openai_math_corollaries/papers/ar_dipolar_exciton/AUDIT.md`: "Scope: `main.tex`/`main.pdf`, `ledger/`, `publication_meta.json`, `data/`, `results/autoresearch/2026-10-25/H1/contribution/`,"
  - `contrib/openai_math_corollaries/papers/ar_dipolar_exciton/AUDIT.md`: "- `papers/ar_dipolar_exciton/audit/audit_epstein_check.py`: an independent numerical check that does not use Ewald"
  - `contrib/openai_math_corollaries/papers/ar_dipolar_exciton/AUDIT.md`: "This is C^∞ (not analytic), nonnegative and completely monotone, which matches §Setting."

### SocrateAI-Scientific-Agora-Physique-Cinetique [PUBLIC] (physics)

Exact-rational kinetic response-function engine with Lean proofs and comparison to published data; carries RETRACTIONS and two audits that found phantom simulation output and stub kernels.

- Created 2026-06-22, last push 2026-09-27; 57 commits and 4 merged PRs in window; disk 5095 KB; language Jupyter Notebook.
- Lean 4: 6 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 2 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 4; data files (csv/json/etc): 16; TeX files: 4.
- Honesty/audit/status files: `AUDIT_SUMMARY.md`, `SCIENTIFIC_AUDIT_REPORT.md`
  - `AUDIT_SUMMARY.md`: "**Audit Scope:** Verify alignment between documented claims and actual implementation"
  - `AUDIT_SUMMARY.md`: "This repository had undergone one prior audit (recorded in `RETRACTIONS.md`), with corrections applied to the codebase. A comprehensive secondary audit revealed:"
  - `AUDIT_SUMMARY.md`: "This is exactly the fabricated phantom simulation that `RETRACTIONS.md` §R2 identifies as "not produced by any code in this repository." The commit message claiming to "remove floating point JSON" (217f94a) **never touched this file** — it only added an unrela"
  - `SCIENTIFIC_AUDIT_REPORT.md`: "- **Status:** **FAIL (Corrected)**"
  - `SCIENTIFIC_AUDIT_REPORT.md`: "2. **Phenomenological Stub (Rule 5 / Unvalidated Applications):** The Godfrin agent extracted a roton scattering kernel that was merely a parameterized polynomial `1 + 0.8 * cos(theta)^2` rather than empirical ILL IN5 data. Claiming this as "data extraction" v"
  - `SCIENTIFIC_AUDIT_REPORT.md`: "- **Honest Data Labeling:** All phenomenological polynomials are explicitly labeled as "Algebraic Stubs (Pending ILL IN5 data ingestion)"."

### SocrateAI-Scientific-CondensedMatterTheory [PUBLIC] (physics)

AdS/CMT literature review (73 arXiv papers, RAG on AutoevolveAI's vector store) plus Lean offsets file with an explicit 'not proved' section.

- Created 2026-09-27, last push 2026-10-10; 158 commits and 3 merged PRs in window; disk 7406 KB; language Python.
- Lean 4: 5 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 291; TeX files: 15.
- Honesty/audit/status files: `lean/dtn_offsets/STATUS.md`
  - `lean/dtn_offsets/STATUS.md`: "## What is not proved, and what this does not show"

### SocrateAI-Scientific-DualScaleSimulator [PUBLIC] (physics)

T-duality / string-dynamics simulator on K3 x T^2 with LeanFlow, TDA and Lean certification; no README.

- Created 2026-09-10, last push 2026-10-10; 321 commits and 1 merged PRs in window; disk 43326 KB; language Python.
- Lean 4: 26 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 9 .rs files, 1 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 1; data files (csv/json/etc): 724; TeX files: 7.

### SocrateAI-Scientific-LeanMaster-CoreStringTheoryFormalization [PUBLIC] (physics)

Placeholder with one commit ('First string theory formalization').

- Created 2026-09-16, last push 2026-09-16; 1 commits and 0 merged PRs in window; disk 1 KB; language None.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### SocrateAI-Scientific-QuantumComputing [PUBLIC] (physics)

Quantum-hardware verification stream; README: 'prepared, not implemented', not peer reviewed.

- Created 2026-10-11, last push 2026-10-11; 4 commits and 0 merged PRs in window; disk 158 KB; language Python.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 74; TeX files: 0.

### SocrateAI-Scientific-QuantumFluids [PUBLIC] (physics)

Machine-checked Lean 4 library of quantum-fluid structure (257 theorems) with a textbook tribute to Godfrin's work; RETRACTIONS.md and pre-registered criteria, one hypothesis refuted as written.

- Created 2026-08-14, last push 2026-10-18; 511 commits and 3 merged PRs in window; disk 129334 KB; language Python.
- Lean 4: 95 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 39 .rs files, 5 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 0; data files (csv/json/etc): 1451; TeX files: 68.
- Honesty/audit/status files: `book/facts/lean_audit.md`
  - `book/facts/lean_audit.md`: "## Deliberate negative controls among the book's Lean files (compiled expecting errors; never counted as failures or as theorem files)"
  - `book/facts/lean_audit.md`: "| file | exit | errors | failed as intended | first error | audited |"
  - `book/facts/lean_audit.md`: "| Ch02_NegativeControl | 1 | 2 | yes | ring failed, ring expressions not equal | 2026-10-10 01:30:17 |"

### SocrateAI-Scientific-SectorCausalityTheory [PUBLIC] (physics)

Criterion for when self-duality has physical consequences, with Lean formalisation, notebooks and an MCP server; tested on sixteen candidate systems; README has a 'what this theory does not claim' section.

- Created 2026-09-27, last push 2026-09-28; 10 commits and 0 merged PRs in window; disk 3266 KB; language Jupyter Notebook.
- Lean 4: 30 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=yes. Notebooks: 3; data files (csv/json/etc): 33; TeX files: 3.

### xaviercallens-SocrateAI-Scientific-Agora-K3-Quatum [PUBLIC] (physics)

Architecture notes for quantum simulation of K3 x T^2 models; small, mostly TeX.

- Created 2026-08-04, last push 2026-08-10; 10 commits and 0 merged PRs in window; disk 1618 KB; language Python.
- Lean 4: 1 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 2; TeX files: 10.

### xaviercallens-SocrateAI-Scientific-FluidMecanism [PUBLIC] (physics)

Empty placeholder (1 commit).

- Created 2026-08-12, last push 2026-08-12; 1 commits and 0 merged PRs in window; disk 1 KB; language None.
- Lean 4: 0 .lean files, lakefile=no, lean-toolchain=no. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 0; TeX files: 0.

### xaviercallens-SocrateAI-Scientific-LeanMaster-StringTheoryFormalization [PUBLIC] (physics)

Earlier public copy of the string-theory Lean formalisation; claims 'first machine-verified formalisation', a claim the main LeanMaster repo later withdrew.

- Created 2026-09-14, last push 2026-09-14; 3 commits and 0 merged PRs in window; disk 144 KB; language HTML.
- Lean 4: 32 .lean files, lakefile=yes, lean-toolchain=yes. Rust: 0 .rs files, 0 Cargo.toml (first 5 counted), SUNDIALS mention=no. Notebooks: 0; data files (csv/json/etc): 5; TeX files: 0.

## Lessons learnt across repos (quotes)

- **AutoevolveAI**: Every quantitative claim must be traceable to an artifact, and every gate must be able to fail. A gate that has never rejected anything is not a gate.
- **AutoevolveAI**: An internal audit found 14 components reporting success without doing the work (README, 'Measured status').
- **SocrateAI-Scientific-Agora-LeanMaster**: Earlier README described the project as 'the first fully certified String Theory' ... An audit found that several headline claims held only for a much narrower Lean statement than the one described in prose (e.g. a bound over N presented as holding over R) ... one Lean theorem contained a real bug (a non-unique 'unique minimum' caused by Nat truncation, now fixed).
- **SocrateAI-Scientific-Agora-K3-DarkMatter**: F6 disclosure (2026-07-24): C1/C2 lattice numbers retracted ... mislabeled them as z-space singular points, with hardcoded exponents ... The resulting ... numbers rho=4, T=18 ... are NOT valid and are retracted.
- **SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal**: Two vacuous S1-03 'integrality' theorems discovered; s10/s18 partner series NOT integral (witnesses 17/2, 45/2 at n=2); s7 integrality 'PASS(7) only, general case = named open goal'.
- **DarkMatterK3-Home.github.io**: WP_A2_CIRCULARITY_AUDIT: 'Gate 0 of the Laboratory-Scale Re-Scope: FAIL ... a clean negative, reported with the same prominence as a positive.'
- **DarkMatterK3-Home.github.io**: Lesson: every numeric constant must be verified against an external source; no hardcoding of raw values from unverified sources (LESSONS_LEARNED.md).
- **Mirror-Map-Sieve**: 'Status: exploratory preprint seeking expert review. We do not claim a discovery.' A fixed CY positional bias first failed (+10% ppl); a learnable bias passed (+8.1%) but the gain is learnability, not Calabi-Yau structure.
- **SocrateAI-Scientific-AlienMathematics-Foundation**: 'An honest account of an AI-driven mathematical exploration, its failures, its one genuine contribution' - 6 independent computational methods failed to find any exact decomposition even at R = 48 where one is known to exist.
- **SocrateAI-Scientific-Agora-Physique-Cinetique**: Secondary audit found a 'fabricated phantom simulation ... not produced by any code in this repository' and a Bakry-Emery routine that built a SymPy Ricci tensor then discarded it and returned 2*d; roton kernel was a parameterised polynomial relabelled 'Algebraic Stubs'; status FAIL (Corrected).
- **SocrateAI-Scientific-AutoEvolve-K3xT2**: 'We do not yet claim definitive empirical discovery'; an unconstrained steep axion spectrum was decisively refuted by NANOGrav 15-yr (lnB = -51.58).
- **SocrateAI-Scientific-Genetic**: AUDIT_2026-10-21: 'POLE P286R TMB 12500/9 mut/Mb is a model output, not an observation'; 'GAR.H15's mechanism for POLE P286R is refuted ... the whole stage-removal model class fails.'
- **SocrateAI-Scientific-QuantumFluids**: Pre-registered criterion 'refutes the hypothesis as written'; two hypotheses refuted for one reason; some criteria 'failed through my own design' (README).
- **SocrateAI-Scientific-Communication**: A claim of being the first Lean 4 formalization of this material 'was false, and it was refuted' (README, 'honest status of the current paper').
- **SocrateAI-Scientific-TNN-UniversModel**: Certified audit renamed 'Live Sonic Horizon Simulator / analogous to Hawking white hole' to '1D Advection-Diffusion Proxy' and 'Hamiltonian drift' to 'L2-Norm Drift'.
- **OpenAI-NSE-Epistemic-Audit**: 'A Physical Reading, Not a Physical Refutation'; later note withdraws 'physical vacuity' and 'censorship' wording; found an axiom declared in a file whose header claimed '0 custom axioms'.
- **triangular-universal-optimality-lean**: Open red-team review, 'Not peer reviewed'; LIMITATIONS: our UniversallyOptimal uses lower energy (liminf), weaker than CKMRV's definition; upstream does not claim the per-potential Cohn-Kumar form and neither do we.
- **SocrateAI-Scientific-MechanicaFluidorum**: 'A "no" answer is a success, not a failure' - Definition of Done does not include proving Hypothesis U; a negative verdict or a killed track counts.
- **SocrateAI-Numeric-DualScale-Solver**: Tautological local literal negative controls replaced by an authoritative validation engine; LaTeX abstract inequality contradicting the exact bound was corrected.
- **GWAYA-GwenLayaOpenModel**: CLAIM_AUDIT: 'One bib entry is wrong ... One README badge is overstated'; recomputed numbers marked V (verified), VN (caveat) or X (mismatch).
- **HiveMind**: 'The legacy scientific swarm and domain-trainer paths are synthetic Gaussian-regression/game simulations, not language benchmarks. Their MSE is not perplexity ... [the smoke test] does not validate the broader hardware, WAN, frontier-capability or performance claims.'
- **SocrateAI-Scientific-Agora-LeanFlow**: 'Status (2026-09-19): planning repository. There is no server code yet.'
- **SocrateAI-Scientific-QuantumComputing**: 'Status (2026-10-11): prepared, not implemented. Not peer reviewed.'
- **SocrateAI-Scientific-Mathesis**: A statement can be non-vacuous, carry witnesses in both polarities, and still be the wrong statement (AUDIT_PACK.md).
- **SocrateAI-Scientific-Elenchus**: 'The elenchus ... never establishes a positive truth. It removes false confidence, and that is all it does.'
- **TIC4206066-Exoplanet-Verification**: Positive control recovered 100%; eclipsing-binary, secondary-occultation and centroid-shift negative controls all REFUTED as intended.

## Non-science kept repositories (one line each)

- liaspeaking [PUBLIC] (education): Local voice-based educational companion app for children aged 8-13.
- scikit-runux-tribute [PUBLIC] (education): Tribute / teaching-style scikit-learn-like library dedicated to two professors.
- HiveMind-home.github.ui [PUBLIC] (infrastructure/devops): Near-empty placeholder repo for the HiveMind@home front end (1 commit).
- HiveMindatHome.github.io [PUBLIC] (infrastructure/devops): Static project site for HiveMind@home / La Ruche (compute-reciprocity charter, no money involved).
- runux-ai-runtime [PRIVATE] (infrastructure/devops): Private proprietary RISC-V LLM runtime (KV-cache compression, integer attention); Rust + some Lean.
- rust-linux-mini-kernel [PUBLIC] (infrastructure/devops): RunuX: no_std Rust kernel / Linux-subsystem reimplementation with Lean verification of parts, boots under QEMU and cloud VMs; build-status files record failed container builds.
- xaviercallens.github.io [PUBLIC] (infrastructure/devops): Static site mirror of the HiveMind@home page.
- xavuntu-AIRustLinux [PUBLIC] (infrastructure/devops): AI-native Rust Linux distribution concept built on the RunuX kernel; failed-build status files included.
- OpenAI4F [PUBLIC] (personal/other): Stub repo (OpenSource AI for Finance), 2 commits.
- OpenSourceAI4Finance-ControlCenter [PUBLIC] (personal/other): Empty placeholder repo.
- PersonaShield [PRIVATE] (personal/other): Private empty repo.
- ReadyPlayerTogether [PUBLIC] (personal/other): Godot 4 VR/desktop metaverse game project; not scientific.
- SocrateAI-Scientific-LLeanM [PUBLIC] (personal/other): Empty repository.
- VibeSpec [PUBLIC] (personal/other): Mockup-to-formal-spec-to-code pipeline for front-end generation; software tooling.
- WebWebLightv4 [PRIVATE] (personal/other): AI Studio web app scaffold.
- macmagicbrush [PRIVATE] (personal/other): Private local web UI for the MagicBrush image-editing model.
- mopga [PRIVATE] (personal/other): Private manifesto note on planetary CO2 removal; no README.
- scribemed [PUBLIC] (personal/other): Local medical-scribe AI assistant (French); not research.
- symbioticfactory [PUBLIC] (personal/other): Open blueprint documents for a carbon-negative water-energy-food-carbon biorefinery; design-level, no experiments.
- videomorph [PRIVATE] (personal/other): Private empty repo.
- wazair [PUBLIC] (personal/other): Empty repo.
- webwarcybergame [PUBLIC] (personal/other): Browser cyber-warfare strategy game.
- xPersonaShield [PRIVATE] (personal/other): Private GPU adversarial-perturbation tool to protect portraits from AI manipulation.
- xprivateremoteaccess [PRIVATE] (personal/other): Private SSH remote-access notes.
- xvideomorph [PRIVATE] (personal/other): Private empty repo.
