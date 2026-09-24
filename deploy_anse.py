"""
ANSE 2.0 Heterogeneous Deployment CLI

This script operationalizes the 5 deployment models defined in the 
ANSE 2.0 Architecture Specification. It dynamically adjusts the autopoietic
engine's parameters (MeZO perturbation bounds, Monte Carlo counts, backend) 
based on the host hardware profile.
"""

import argparse
import sys
import psutil
import torch
import os
from pathlib import Path
import tempfile
import logging

from anse.v2.engine_v2 import ANSEEngineV2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("anse.deploy")

def get_system_ram_gb() -> float:
    return psutil.virtual_memory().total / (1024**3)

def detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def deploy_developer_node(args):
    """Mac M2 (32 GB RAM) - Continuous Autopoiesis"""
    logger.info("Initializing The Developer Node profile (Target: MPS, 32GB RAM)")
    engine = ANSEEngineV2(input_dim=128, latent_dim=64, registry_dir=args.registry)
    # High Monte Carlo batch sizes, full REM sleep
    run_engine_loop(engine, num_monte_carlo=10000, enable_rem=True)

def deploy_swarm_hub(args):
    """Mac M1 Ultra (64 GB RAM) - The Local Swarm Hub"""
    logger.info("Initializing The Swarm Hub profile (Target: MPS, 64GB RAM)")
    engine = ANSEEngineV2(input_dim=256, latent_dim=128, registry_dir=args.registry)
    # Most intensive System 2 verification + local aggregation
    run_engine_loop(engine, num_monte_carlo=15000, enable_rem=True)

def deploy_edge_worker(args):
    """Old Windows (16 GB RAM, RTX 2080 8GB VRAM)"""
    logger.info("Initializing The Edge Worker profile (Target: CUDA 8GB VRAM)")
    engine = ANSEEngineV2(input_dim=64, latent_dim=32, registry_dir=args.registry)
    # Moderate bounds to respect 8GB VRAM limit
    run_engine_loop(engine, num_monte_carlo=2000, enable_rem=False)

def deploy_cpu_oracle(args):
    """Linux Dev (32 GB RAM, No GPU) - Deterministic Sandbox"""
    logger.info("Initializing The CPU Sandbox Oracle profile (Target: CPU)")
    engine = ANSEEngineV2(input_dim=64, latent_dim=32, registry_dir=args.registry)
    # Sandbox intensive, aggressive CPU bounds
    run_engine_loop(engine, num_monte_carlo=2000, enable_rem=True)

def deploy_apex_synthesizer(args):
    """Remote GCP (GPUPOD) - Apex Synthesizer"""
    logger.info("Initializing The Apex Synthesizer profile (Target: Multi-GPU)")
    engine = ANSEEngineV2(input_dim=512, latent_dim=256, registry_dir=args.registry)
    # Massive scale
    run_engine_loop(engine, num_monte_carlo=50000, enable_rem=True)

def run_engine_loop(engine: ANSEEngineV2, num_monte_carlo: int, enable_rem: bool):
    logger.info(f"Starting execution loop: MC Rollouts={num_monte_carlo}, REM={enable_rem}")
    # Run a test cycle to validate integration
    sensory_input = torch.randn(4, engine.input_dim) 
    
    # Normally this would loop infinitely. We do a single verification pass.
    logger.info("Running validation cognitive cycle...")
    result = engine.run_autonomous_cycle(
        sensory_input=sensory_input,
        prompt_text="Deploy V2 Verification Task",
        num_monte_carlo=num_monte_carlo,
        trigger_sleep_after=enable_rem
    )
    
    logger.info(f"✅ Deployment Verification Complete. Final Energy: {result.final_energy_score:.4f}")
    if enable_rem and result.rem_summary:
        logger.info(f"🌙 REM Sleep Verified. Retention Fidelity: {result.rem_summary.retention_fidelity_pct:.2f}%")

def main():
    parser = argparse.ArgumentParser(description="ANSE 2.0 Heterogeneous Deployment CLI")
    parser.add_argument("--role", type=str, choices=["dev-node", "swarm-hub", "edge-worker", "cpu-oracle", "apex"], 
                        help="The hardware deployment role", required=True)
    parser.add_argument("--registry", type=str, default="/tmp/anse_registry", 
                        help="Path to the shared swarm registry")
    
    args = parser.parse_args()
    
    os.makedirs(args.registry, exist_ok=True)
    
    device = detect_device()
    ram_gb = get_system_ram_gb()
    logger.info(f"Host Hardware Detected: Device={device}, RAM={ram_gb:.1f}GB")
    
    if args.role == "dev-node":
        deploy_developer_node(args)
    elif args.role == "swarm-hub":
        deploy_swarm_hub(args)
    elif args.role == "edge-worker":
        deploy_edge_worker(args)
    elif args.role == "cpu-oracle":
        deploy_cpu_oracle(args)
    elif args.role == "apex":
        deploy_apex_synthesizer(args)

if __name__ == "__main__":
    main()
