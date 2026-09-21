"""
Central configuration for ANSE.

All hyperparameters, model IDs, and runtime settings live here.
Modify this file (or override via .env) instead of scattering magic numbers
throughout the codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Project root ────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent


@dataclass
class ModelConfig:
    """LLM / encoder settings."""

    model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
    """HuggingFace model ID for the frozen System 1 backbone."""

    device: str = "auto"
    """Passed to `device_map` in `from_pretrained`. Use 'cpu' for CPU-only testing."""

    load_in_4bit: bool = False
    """Enable 4-bit quantisation via bitsandbytes (saves ~12 GB VRAM)."""

    hidden_state_layers: list[int] = field(default_factory=lambda: [-1, -2, -3, -4])
    """Which transformer layers to extract hidden states from (0-indexed from the end).
    Last 4 layers are empirically sufficient and keep the JEPA input tractable."""

    hidden_dim: int = 4096
    """LLM hidden dimension — must match `model_id` architecture."""

    max_new_tokens: int = 512
    """Maximum tokens to generate per LLM call."""

    temperature: float = 0.2
    """Sampling temperature — low for deterministic code generation."""

    # OpenAI-compatible API settings (used when running via Ollama / vLLM server)
    api_base_url: str = os.getenv("ANSE_API_BASE", "http://localhost:11434/v1")
    api_key: str = os.getenv("ANSE_API_KEY", "ollama")
    api_model_name: str = os.getenv("ANSE_API_MODEL", "qwen2.5-coder:7b")


@dataclass
class JEPAConfig:
    """JEPA World Model architecture settings."""

    latent_dim: int = 512
    """Down-projection from LLM hidden_dim. JEPA input dimension."""

    hidden_dim: int = 1024
    """Internal JEPA transformer hidden dimension."""

    num_heads: int = 8
    """Attention heads in the JEPA predictor block."""

    num_layers: int = 2
    """Number of transformer layers in the JEPA predictor."""

    dropout: float = 0.1
    """Dropout rate for JEPA regularisation."""

    checkpoint_path: Path = ROOT / "checkpoints" / "jepa_best.pt"
    """Where to save/load the best JEPA checkpoint."""

    contrastive_weight: float = 0.1
    """Weight of the contrastive regularisation term in JEPA training loss."""


@dataclass
class System2Config:
    """System 2 (inference-as-optimisation) settings."""

    soft_token_count: int = 16
    """Number of trainable soft-token vectors prepended to the prompt."""

    max_steps: int = 20
    """Maximum pondering steps before forced decode."""

    step_lr: float = 0.05
    """Adam learning rate for the soft-token thought optimiser."""

    energy_threshold: float = 5.0
    """Stop pondering once total energy drops below this value."""

    quick_decode_tokens: int = 20
    """Tokens for the fast syntax-check preview during pondering."""


@dataclass
class PlasticityConfig:
    """Continuous learning (LoRA fast-weights) settings."""

    lora_rank: int = 16
    """LoRA adapter rank — higher = more capacity, more VRAM."""

    lora_alpha: int = 32
    """LoRA alpha scaling factor (effective scale = alpha / rank)."""

    lora_target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    """Which attention projection matrices to apply LoRA to."""

    lora_layers: str = "last_8"
    """Which layers get LoRA adapters: 'all' | 'last_8' | 'last_4'."""

    plasticity_lr: float = 1e-4
    """AdamW learning rate for online LoRA updates (surprise updates)."""

    consolidation_lr: float = 1e-5
    """Lower LR for sleep-cycle distillation (stable consolidation)."""

    surprise_threshold: float = 10.0
    """Minimum |predicted_energy - actual_energy| to trigger a surprise update."""

    ewc_lambda: float = 0.4
    """Elastic Weight Consolidation penalty coefficient."""

    replay_every_n_updates: int = 10
    """Frequency of experience-replay mini-batches during online learning."""

    checkpoint_path: Path = ROOT / "checkpoints" / "lora_latest.pt"
    """Path to save/load the current LoRA adapter state."""


@dataclass
class SandboxConfig:
    """Symbolic engine / sandboxing settings."""

    timeout_seconds: float = 10.0
    """Wall-clock time limit for code execution before timeout penalty."""

    tier1_mem_limit_mb: int = 2048
    """Address-space cap (RLIMIT_AS, POSIX) for Tier-1 subprocesses."""

    docker_image: str = "anse-sandbox:latest"
    """Docker image used for Tier-2 isolated execution."""

    docker_mem_limit: str = "512m"
    """Memory cap for Docker sandbox containers."""

    docker_cpu_count: float = 2.0
    """CPU cores available to sandbox container."""

    dangerous_modules: list[str] = field(
        default_factory=lambda: [
            "os",
            "sys",
            "subprocess",
            "socket",
            "shutil",
            "pathlib",
            "glob",
            "importlib",
            "ctypes",
            "signal",
        ]
    )
    """Imports that trigger escalation from Tier-1 to Tier-2 (Docker) sandbox."""


@dataclass
class MemoryConfig:
    """ChromaDB episodic memory settings."""

    persist_directory: Path = ROOT / "data" / "chroma"
    """Local directory for ChromaDB persistence."""

    collection_name: str = "anse_episodes"
    """ChromaDB collection name."""

    embedding_model: str = "all-MiniLM-L6-v2"
    """Sentence-transformer model for semantic retrieval."""

    max_results: int = 10
    """Default number of memories to retrieve per query."""

    interactions_log: Path = ROOT / "data" / "interactions.jsonl"
    """JSONL log of all episodes — source of truth for JEPA training."""

    sleep_buffer: Path = ROOT / "data" / "sleep_buffer.jsonl"
    """Buffer of high-quality memories queued for consolidation."""


@dataclass
class SleepConfig:
    """Sleep-cycle (consolidation) settings."""

    idle_trigger_seconds: float = 300.0
    """Trigger sleep after this many seconds of inactivity."""

    surprise_buffer_trigger: int = 1000
    """Also trigger sleep when surprise buffer reaches this size."""

    consolidation_batch_size: int = 16
    """Memories per consolidation step."""

    consolidation_steps: int = 200
    """Total gradient steps per sleep cycle."""

    diversity_fetch_count: int = 200
    """How many diverse memories to fetch from ChromaDB for consolidation."""


@dataclass
class AutopoiesisConfig:
    """Self-architectural evolution settings."""

    enabled: bool = False
    """Master switch — must be explicitly set to True to allow self-modification."""

    workspace: Path = ROOT / "workspace"
    """Isolated directory where child instances are spawned."""

    benchmark_pass_threshold: float = 0.95
    """Child must score ≥ 95% of parent on benchmarks to be approved."""

    vram_improvement_threshold: float = 0.90
    """Child must use ≤ 90% of parent VRAM to be approved."""

    evolution_log: Path = ROOT / "evolution_log.jsonl"
    """JSONL record of all proposed + approved/rejected architectural changes."""


@dataclass
class PerformanceConfig:
    """Algorithmic performance engineering & computational physics settings."""

    weight_time_ms: float = 1.0
    """Weight w_t for execution duration (ms) in the energy function."""

    weight_peak_ram_mb: float = 1.0
    """Weight w_m for peak RAM consumption (MB) in the energy function."""

    penalty_infinite_energy: float = 1e6
    """Energy penalty assigned to crashes, syntax errors, timeouts, or output mismatches (proxy for ∞)."""

    warmup_runs: int = 1
    """Number of unmeasured warmup iterations before profiling."""

    repeat_runs: int = 3
    """Number of profiling repeats (minimum execution time is recorded for stability)."""

    target_speedup_ratio: float = 0.10
    """Desired ratio of candidate execution time to baseline (e.g. 0.10 = 90% speedup)."""


@dataclass
class ANSEConfig:
    """Top-level configuration — compose all sub-configs here."""

    model: ModelConfig = field(default_factory=ModelConfig)
    jepa: JEPAConfig = field(default_factory=JEPAConfig)
    system2: System2Config = field(default_factory=System2Config)
    plasticity: PlasticityConfig = field(default_factory=PlasticityConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    sleep: SleepConfig = field(default_factory=SleepConfig)
    autopoiesis: AutopoiesisConfig = field(default_factory=AutopoiesisConfig)

    # Runtime mode
    use_local_llm: bool = True
    """If True, load LLM weights locally via transformers. If False, use API (Ollama/vLLM)."""

    log_level: str = "INFO"
    seed: int = 42


# ─── Singleton ───────────────────────────────────────────────────────────────
_default_config: ANSEConfig | None = None


def get_config() -> ANSEConfig:
    """Return the global default config (lazy-initialised)."""
    global _default_config
    if _default_config is None:
        _default_config = ANSEConfig()
    return _default_config


def set_config(cfg: ANSEConfig) -> None:
    """Override the global config (useful in tests)."""
    global _default_config
    _default_config = cfg
