---
name: hivemind-contributor
description: Autonomous contributor skill for Project HiveMind (https://github.com/xaviercallens/HiveMind). Enforces the 4 Golden Engineering Invariants (8 GB VRAM ceiling, bitwise CUDA determinism, Multi-Krum & ZK-OPoI Byzantine resilience, <1.5s game preemption), 5-Layer Anti-"Code Boubou" PR Security Scanner, 25-Vector Guardrail Attack Simulator, 64-Theorem Lean 4 Formal Spec verification, MCP server tools, and conversation episode recording.
---

# Project HiveMind Contributor Skill (`hivemind-contributor`)

Use this skill whenever contributing features, bug fixes, Hugging Face QLoRA domain experts, QUIC/STUN/TURN transport upgrades, Lean 4 formal proofs, or security hardening to **Project HiveMind** ([`https://github.com/xaviercallens/HiveMind`](https://github.com/xaviercallens/HiveMind), checked out at [`sub_projects/hivemind/HiveMind/`](file:///home/xavkal/xdev/AutoevolveAI/sub_projects/hivemind/HiveMind)).

---

## 1. Binding Non-Monetary Charter & Anti-"Code Boubou" Security Rules

1. **Zero Money Involved (`LEGAL_DISCLAIMER_AND_COMPUTE_RECIPROCITY.md`)**:
   - Project HiveMind is a strictly non-commercial, voluntary open-source scientific project (`0.00 EUR / USD`).
   - All `$HIVE` amounts, "Bounties", and PoUW credits are symbolic, non-monetary reciprocal compute-power accounting units.
   - **Never** include payment URLs (`paypal.me`, `ko-fi.com`, `patreon.com`, `buymeacoffee.com`), payment solicitation text (`PAY-01`, `PAY-02`), or cryptocurrency wallet addresses (`PAY-03`) in code, docs, commits, or PR descriptions.
2. **Anti-"Code Boubou" Enforcement (`CB-01` .. `CB-04`)**:
   - Every PR claiming an issue/bounty closure (`fixes #N`, `closes #N`, `HM-S6-XX`) **must** modify functional files in `src/hivemind/`, `lean4/`, or `tests/` with $\ge 5$ functional lines added (`CB-02`, `CB-03`).
   - **Never** commit binary/cache blobs (`.coverage`, `.pkl`, `.exe`, `.dll`, `__pycache__/`, `.env`) (`CB-01`).
3. **AST & Trojan Source Safety (`SEC-01` .. `SEC-05`)**:
   - Never use `eval()`, `exec()`, `os.system()`, `subprocess(..., shell=True)`, or `pickle.load()` (`use torch.load(..., weights_only=True)`).
   - Zero bidirectional Unicode control characters (`U+202A`–`U+2069`) or hardcoded tokens.

---

## 2. The 4 Golden Engineering Invariants

1. **The 8 GB Consumer GPU VRAM Ceiling ($\le 6656\text{ MiB}$ usable WDDM ceiling)**:
   - Use `stream_load_hf_causal_lm()` (meta-device init + streaming 4-bit NF4 double quantization, $\frac{128}{33} \approx 3.88\times$ compression).
   - Peak allocated VRAM on `Qwen/Qwen2.5-0.5B` (96 MoE experts) must stay $\le 1527\text{ MiB}$ ($< 2.0\text{ GB}$), and `Qwen/Qwen2.5-7B` worker footprints must stay $\le 6490\text{ MiB}$ ($\le 6656\text{ MiB}$).
2. **Bitwise / Bounded CUDA Determinism ($\epsilon \le 10^{-4}$)**:
   - Inner training loops must remain deterministic under `configure_deterministic_runtime()` (`CUBLAS_WORKSPACE_CONFIG=:4096:8`) so `DeterministicSpotCheckValidator` can replay any 10% micro-segment ($s=50$ of $H=500$ steps, $20\times$ FLOP savings vs $2\times$ BOINC).
3. **Byzantine Resilience (`Multi-Krum` + `ZK-OPoI`)**:
   - Outer-loop aggregation preserves Multi-Krum ($n \ge 2f + 3 \implies k = n - f - 2 \ge f + 1$), Adaptive Median-$L_2$ clipping ($\le 2.0 \cdot \text{median}$), and $O(\log_2 L)$ `ZK-OPoI` interactive bisection.
4. **Zero-Intrusion Gamer Respect ($< 1.5\text{ s}$ Preemption & $500\text{ ms}$ WDDM Margin)**:
   - Foreground game launch triggers emergency NVMe checkpointing and VRAM eviction in $< 1500\text{ ms}$ ($500\text{ ms}$ below the $2000\text{ ms}$ Windows WDDM TDR reset timeout).

---

## 3. MCP Tools (`mcp_hivemind_server.py` / Server: `hivemind-contributor`)

- `hivemind_status_and_bounties()`: Lists repository status, the 4 Golden Rules, exact-$\mathbb{Q}$ certificates, and Season 6 (`Wave 5`, `HM-S6-01`..`HM-S6-05`) open milestones.
- `hivemind_scan_pr_security(pr_title, pr_body, author, changed_filenames)`: Runs the 5-Layer `PRSecurityScanner` + `AntiStubGuard` on a proposed PR.
- `hivemind_run_hardness_gate(include_redteam_25_vectors=True)`: Runs all 6 hardness layers (Anti-Stub + 5-Layer Repo Audit + S-2/S-3/S-4 Runtime Self-Tests + 25-Vector Attack Simulator + 64-Theorem Lean 4 Spec + Execution Attestation).
- `hivemind_verify_lean4_spec()`: Verifies all 64 machine-checked Lean 4 theorems (`0 sorry`, `0` axioms) in `sub_projects/hivemind/formal/HiveMindSpec.lean`.
- `hivemind_record_conversation_episode(prompt, files_edited, code_or_summary, passed, task_id)`: Scrubs PII/secrets and records the contribution episode to `results/hivemind_conversation_spool.jsonl` and `data/hivemind_episodes.db`.

---

## 4. End-to-End Contribution Pipeline Commands

```bash
# 1. Run the full HiveMind contribution pipeline (status + 6-layer hardness + Lean 4 + pytest + conversation record)
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py run-all

# 2. Check Season 6 (Wave 5) open contributor tasks and branch prefixes
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py status

# 3. Run the 6-layer Hardness & 25-Vector Red-Team Gate
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py harden

# 4. Validate a candidate PR title, body, and modified file list before opening a PR
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py prepare-pr \
  --task-id HM-S6-01 \
  --title "feat(s6): implement EF21-DiLoCo error-feedback residual buffer" \
  --body "Implements HM-S6-01 EF21-DiLoCo residual contraction with Lean 4 Theorem 49 verification." \
  --files src/hivemind/swarm/strategy_optimizer.py tests/test_season5_strategy_and_bounties.py

# 5. Harvest & record conversation episodes into SQLite EpisodeStore (data/hivemind_episodes.db)
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py record
```
