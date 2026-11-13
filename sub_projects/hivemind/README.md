# Sub-Project `hivemind` (`HiveMind`) — Decentralized Sparse MoE Training & Inference via Steam, BOINC, and DiLoCo

- **GitHub Repository**: [`https://github.com/xaviercallens/HiveMind`](https://github.com/xaviercallens/HiveMind)
- **Local Checkout**: [`sub_projects/hivemind/HiveMind/`](./HiveMind/README.md) (`origin` & `upstream` remotes configured)
- **Foundation Paper**: [`sub_projects/hivemind/HiveMind/paper/hivemind_foundation_article.pdf`](./HiveMind/paper/hivemind_foundation_article.pdf)
- **Lean 4 Specification**: [`sub_projects/hivemind/formal/HiveMindSpec.lean`](./formal/HiveMindSpec.lean) (`128` machine-checked `theorem` declarations, `0 sorry`, `0` custom axioms; Theorems 117–128 added for Decoupled DiLoCo, 3-Tier Hot-Cold MoE, Looped MoE, Lattice Quantizers & Heterogeneous $H_i$ Spot-Check)
- **Master Roadmap & Season 9/10 Community Tasks**: [`sub_projects/hivemind/HiveMind/ROADMAP.md`](./HiveMind/ROADMAP.md) (`55/55` Community PRs merged across Waves 1–6; Season 9 `Wave 8` & Season 10 `Wave 9` GPU + HiveMind Swarm Campaigns `CAMP-S9/S10 1..4` live in Issues `#119`–`#123`)
- **Architectural Vision & Non-Monetary Reciprocal Compute Points Model**: [`sub_projects/hivemind/HiveMind/vision.md`](./HiveMind/vision.md) (Zero financial payment `0.00 EUR/USD`; "points" grant computing processing benefits only when the live production Swarm is deployed and used by a large community)
- **Season 9 & 10 GPU + HiveMind Swarm Campaign Runner**: [`sub_projects/hivemind/HiveMind/scripts/run_season9_10_gpu_swarm_campaigns.py`](./HiveMind/scripts/run_season9_10_gpu_swarm_campaigns.py) (`tests/test_season9_10_gpu_swarm_campaigns.py`)
- **Opt-In Community GPU Benchmark Suite**: [`sub_projects/hivemind/HiveMind/scripts/run_community_gpu_benchmark.py`](./HiveMind/scripts/run_community_gpu_benchmark.py) (`tests/test_community_gpu_benchmark.py`)
- **Exact-$\mathbb{Q}$ / Lean 4 Bridge Harness**: [`sub_projects/hivemind/hivemind_swarm_bridge_harness.py`](./hivemind_swarm_bridge_harness.py)
- **6-Layer Hardness & 25-Vector Guardrail Engine**: [`sub_projects/hivemind/hivemind_hardness_engine.py`](./hivemind_hardness_engine.py)
- **Conversation Recorder & Episode Flywheel (`anse.v2`)**: [`sub_projects/hivemind/hivemind_conversation_recorder.py`](./hivemind_conversation_recorder.py)
- **MCP Contributor Server (`hivemind-contributor`)**: [`mcp_hivemind_server.py`](../../mcp_hivemind_server.py)
- **Contributor Agent Skill**: [`.agents/skills/hivemind-contributor/SKILL.md`](../../.agents/skills/hivemind-contributor/SKILL.md)
- **End-to-End Contribution Pipeline**: [`scripts/hivemind_contribution_pipeline.py`](../../scripts/hivemind_contribution_pipeline.py)

## 1. Overview & Mathematical Grounding

Project **HiveMind** aggregates consumer GPUs (`8 GB – 12 GB` VRAM, verified on NVIDIA GeForce RTX 2070) and local NVMe storage into a community-owned **Branch-Train-Mix (BTM) Sparse Mixture-of-Experts (MoE)** cluster with non-monetary reciprocal compute-power accounting (`$HIVE`):

1. **Pillar 1 — Zero-Copy 4-Bit NF4 Double Quantization & DiLoCo Wire Compression**:
   - NF4 block bit ratio: $\frac{1024}{264} = \frac{128}{33} \approx 3.8788\times$ compression over FP16 (`nf4_double_quant_compression_bound`).
   - Usable 8 GB RTX 2070 WDDM ceiling: $8192 - 1536 = 6656\text{ MiB}$, certifying both the 96-expert upcycled Qwen2.5-0.5B Sparse MoE ($1527\text{ MiB}$, leaving $5129 \ge 5120\text{ MiB}$ free) and the Qwen2.5-7B DiLoCo QLoRA worker ($6490 \le 6656\text{ MiB}$, `rtx2070_8gb_vram_envelope_verified`).
   - DiLoCo ($H=500$) + Top-$k$ ($20\%$) + FP8 wire compression: $\frac{5000}{3} \approx 1666.67\times$ bandwidth reduction (`diloco_topk_fp8_bandwidth_reduction`).
2. **Pillar 2 — Byzantine Fault Tolerance (10% Deterministic Micro-Checkpoint Spot-Check & Multi-Krum)**:
   - Deterministic single-segment spot-check ($s=50$ of $H=500$ steps) inspects $\frac{1}{10}$ ($10\%$) of inner steps, achieving a $20\times$ verification FLOP reduction vs. classic $2\times$ BOINC replication (`spot_check_10pct_and_20x_boinc_savings`).
   - Multi-Krum resilience ($n \ge 2f+3$): for $n=10, f=3$, neighborhood size $k = n - f - 2 = 5 \ge f + 1 = 4$ guarantees honest worker inclusion (`multikrum_neighborhood_contains_honest_worker`).
3. **Pillar 3 & 4 — Factored BTM Top-2 Sparse MoE Upcycling & PoUW Conservation**:
   - Top-2 routing over 8 domain branches activates $\frac{2}{8} = \frac{1}{4}$ ($25\%$) of expert compute per token (`top2_sparse_moe_quarter_active_compute`), while 3-tier hierarchical 128-expert gating reduces router FLOPs to $\frac{4+4+8}{128} = \frac{1}{8}$ (`hierarchical_128_expert_3tier_gating_savings`).
   - Exact $10{,}000\text{ bps}$ ($100\%$) 4-pool conservation ($6000 + 1500 + 1500 + 1000 = 10000$, `pouw_reward_pools_conserve_100pct`) and geometric halving supply bound $1{,}000{,}000 \le 21{,}000{,}000$ (`hive_geometric_halving_respects_21m_cap`).

## 2. 6-Layer Hardness, MCP Server, Conversation Record & Contribution Pipeline

```bash
# 1. Execute the full 5-stage contribution pipeline (status, 6-layer hardness, pytest, PR precheck, conversation record)
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py run-all

# 2. Run the 6-Layer Hardness & 25-Vector Guardrail Attack Simulator
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py harden

# 3. Audit a proposed Pull Request before submission
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py prepare-pr \
  --task-id HM-S6-01 \
  --title "feat(s6): add EF21-DiLoCo error feedback buffer" \
  --body "Implements HM-S6-01 EF21 residual contraction with Lean 4 Theorem 49 verification." \
  --files src/hivemind/swarm/strategy_optimizer.py tests/test_season5_strategy_and_bounties.py

# 4. Harvest and record conversation episodes into SQLite EpisodeStore (data/hivemind_episodes.db)
PYTHONPATH=. uv run python scripts/hivemind_contribution_pipeline.py record

# 5. Run the integration test suite
uv run pytest tests/integration/test_hivemind_contribution_pipeline.py tests/integration/test_manage_sub_project.py -v
```
