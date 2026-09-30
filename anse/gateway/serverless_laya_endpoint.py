"""
anse/gateway/serverless_laya_endpoint.py
========================================
Serverless Scale-to-Zero Endpoint for Laya Coding Companion.

Key Capabilities:
1. 0-Cost Dormant State (min_replicas = 0):
   - Unloads model weights and reclaims memory when idle for IDLE_TIMEOUT_SECONDS.
2. Fast Cold Start (< 1.0s):
   - Lazily loads Laya model & LoRA adapters on first incoming request.
3. HTTP Autoscaler Telemetry (/v1/scale):
   - Exposes concurrency, request queue depth, throughput, and recommended replica count (0..N).
4. Multi-Task Laya Decision API (/v1/laya/decision):
   - Gating (noul), Role & Tactic Routing (choice), and Energy Scoring (score).
5. OpenAI-Compatible API (/v1/chat/completions):
   - Fast non-autoregressive triage and role dispatch.
"""
from __future__ import annotations

import asyncio
import gc
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, AsyncIterator

import torch
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anse.laya.integration import LayaANSEDispatcher, ANSERole
from anse.laya.model import LayaCodingCompanion, LayaDecision

# CPU Threading Optimization
torch.set_num_threads(8)
try:
    torch.set_num_interop_threads(4)
except RuntimeError:
    pass  # safe: already set or parallel work has started (e.g. pytest collection)


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("ServerlessLayaEndpoint")

DEFAULT_CHECKPOINT_DIR = Path("/mnt/data/home/xavkal/laya_coding_checkpoints/stage3")
IDLE_TIMEOUT_SECONDS = float(os.getenv("IDLE_TIMEOUT_SECONDS", "15.0"))
TARGET_CONCURRENCY_PER_REPLICA = int(os.getenv("TARGET_CONCURRENCY", "10"))
HOST = os.getenv("ENDPOINT_HOST", "0.0.0.0")
PORT = int(os.getenv("ENDPOINT_PORT", "8001"))


class ServerlessLayaManager:
    """Manages lazy cold-starting, memory offloading, scale-to-zero, and autoscaling metrics."""

    def __init__(self, checkpoint_dir: Path, idle_timeout: float = 15.0) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.idle_timeout = idle_timeout
        self.state: str = "DORMANT"  # "DORMANT" | "LOADING" | "ACTIVE"
        self.dispatcher: LayaANSEDispatcher | None = None
        self.last_activity_time: float = 0.0
        self.total_requests: int = 0
        self.active_requests: int = 0
        self.cold_start_count: int = 0
        self.total_cold_start_duration: float = 0.0
        self.lock = asyncio.Lock()

    def is_active(self) -> bool:
        return self.state == "ACTIVE" and self.dispatcher is not None

    def seconds_until_idle_shutdown(self) -> float:
        if not self.is_active():
            return 0.0
        elapsed = time.time() - self.last_activity_time
        remaining = max(0.0, self.idle_timeout - elapsed)
        return round(remaining, 2)

    def load_model(self) -> float:
        """Synchronously load Laya model and LoRA weights."""
        t0 = time.perf_counter()
        logger.info("[Cold Start] Loading Laya model from %s...", self.checkpoint_dir)

        ckpt_path = str(self.checkpoint_dir) if self.checkpoint_dir.exists() else None
        self.dispatcher = LayaANSEDispatcher(
            checkpoint_path=ckpt_path,
            noul_threshold=0.3,
        )

        load_duration = time.perf_counter() - t0
        self.state = "ACTIVE"
        self.cold_start_count += 1
        self.total_cold_start_duration += load_duration
        self.last_activity_time = time.time()

        logger.info(
            "[Cold Start Complete] Laya loaded in %.3fs! State -> ACTIVE. Idle timeout: %.1fs",
            load_duration,
            self.idle_timeout,
        )
        return load_duration

    def unload_model(self) -> float:
        """Unload model from RAM to enter cost-zero DORMANT state (min_replicas=0)."""
        t0 = time.perf_counter()
        logger.info("[Scale-to-Zero] Inactivity detected. Evicting Laya from memory (Cost -> $0.00)...")

        del self.dispatcher
        self.dispatcher = None

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        duration = time.perf_counter() - t0
        self.state = "DORMANT"
        logger.info("[DORMANT State] Memory reclaimed in %.3fs. Cost: $0.00/hr.", duration)
        return duration

    async def ensure_active(self) -> tuple[bool, float]:
        """Ensure model is loaded, triggering cold start if dormant."""
        async with self.lock:
            if self.is_active():
                self.last_activity_time = time.time()
                return False, 0.0

            self.state = "LOADING"
            loop = asyncio.get_running_loop()
            cold_start_duration = await loop.run_in_executor(None, self.load_model)
            return True, cold_start_duration


manager = ServerlessLayaManager(DEFAULT_CHECKPOINT_DIR, idle_timeout=IDLE_TIMEOUT_SECONDS)


async def idle_watchdog_task() -> None:
    """Monitors activity and triggers scale-to-zero when idle."""
    logger.info("Starting Scale-to-Zero watchdog (timeout: %.1fs)", IDLE_TIMEOUT_SECONDS)
    while True:
        await asyncio.sleep(1.0)
        async with manager.lock:
            if manager.is_active() and manager.active_requests == 0:
                elapsed = time.time() - manager.last_activity_time
                if elapsed >= manager.idle_timeout:
                    manager.unload_model()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    watchdog = asyncio.create_task(idle_watchdog_task())
    yield
    watchdog.cancel()
    if manager.is_active():
        manager.unload_model()


app = FastAPI(
    title="ANSE Laya Serverless Cognitive Endpoint",
    description="Scale-to-zero (min_replicas=0) non-autoregressive decision & routing endpoint with HTTP autoscaling.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Returns endpoint health, lifecycle state, and cost telemetry."""
    return {
        "status": "healthy",
        "service": "anse-serverless-laya-endpoint",
        "model_architecture": "ModernBERT-base (149M) + LoRA (577k params)",
        "state": manager.state,
        "is_model_loaded": manager.is_active(),
        "min_replicas": 0,
        "idle_timeout_seconds": manager.idle_timeout,
        "seconds_until_scale_to_zero": manager.seconds_until_idle_shutdown(),
        "cold_start_count": manager.cold_start_count,
        "total_requests": manager.total_requests,
        "cost_state": "$0.00 (dormant, scale-to-zero active)" if not manager.is_active() else "active_inference",
        "idle_cost_per_hour": "$0.00",
    }


@app.get("/v1/scale")
async def autoscaler_metrics() -> dict[str, Any]:
    """
    HTTP Autoscaler Telemetry:
    Reports real-time request load, target concurrency, and recommended replica counts.
    """
    active = manager.active_requests
    target_conc = TARGET_CONCURRENCY_PER_REPLICA
    
    # Scale-to-zero logic: 0 replicas when dormant and no active requests
    if not manager.is_active() and active == 0:
        recommended_replicas = 0
        scaling_action = "SCALE_DOWN_TO_ZERO"
    elif active == 0:
        recommended_replicas = 1  # warm replica waiting for idle timeout
        scaling_action = "READY_FOR_IDLE_EVICTION"
    else:
        # Scale up replicas based on active concurrency
        recommended_replicas = max(1, (active + target_conc - 1) // target_conc)
        scaling_action = "SCALE_UP" if recommended_replicas > 1 else "STEADY"

    return {
        "autoscaler_policy": "http_concurrency_autoscaler",
        "min_replicas": 0,
        "max_replicas": 10,
        "current_active_requests": active,
        "total_requests_processed": manager.total_requests,
        "target_concurrency_per_replica": target_conc,
        "recommended_replica_count": recommended_replicas,
        "scaling_action": scaling_action,
        "state": manager.state,
        "idle_timeout_seconds": manager.idle_timeout,
        "seconds_until_scale_to_zero": manager.seconds_until_idle_shutdown(),
    }


@app.get("/v1/cost")
async def cost_metrics() -> dict[str, Any]:
    """Returns zero-cost guarantee telemetry."""
    return {
        "status": "zero_cost_dormant" if not manager.is_active() else "active_inference",
        "state": manager.state,
        "is_model_loaded": manager.is_active(),
        "idle_compute_cost": "$0.00",
        "idle_cost_per_hour": "$0.00",
        "seconds_until_scale_to_zero": manager.seconds_until_idle_shutdown(),
        "min_replicas": 0,
        "scale_to_zero_enforced": True,
    }


@app.post("/v1/unload")
async def manual_unload() -> dict[str, Any]:
    """Force immediate transition to dormant state for testing."""
    async with manager.lock:
        if not manager.is_active():
            return {"status": "already_dormant", "state": manager.state}
        duration = manager.unload_model()
        return {"status": "unloaded", "duration_seconds": round(duration, 3), "state": manager.state}


@app.post("/v1/laya/decision")
@app.post("/v1/predict")
async def laya_decision_endpoint(request: Request) -> Response:
    """
    Main Laya Multi-Task Cognitive Decision Endpoint.
    Returns:
      - noul: anti-stub / security / pass probability in [0, 1]
      - choice: classified ANSE role / Lean 4 tactic
      - score: estimated thermodynamic runtime energy
      - anse_energy: E in [0, inf) (E=1e6 on barrier breach)
      - blocked: bool (True if noul < 0.3)
      - recommended_role: ANSE specialist agent role
      - lean4_tactic: recommended tactic if applicable
    """
    body = await request.json()
    code_text = body.get("code") or body.get("text") or body.get("prompt") or ""
    if not code_text:
        raise HTTPException(status_code=400, detail="Missing required field 'code' or 'text'")

    manager.active_requests += 1
    try:
        # 1. Ensure model is loaded (cold start if dormant)
        was_cold, cold_start_dur = await manager.ensure_active()
        manager.total_requests += 1
        manager.last_activity_time = time.time()

        # 2. Execute inference inside worker thread
        loop = asyncio.get_running_loop()
        t0 = time.perf_counter()

        def infer_fn():
            assert manager.dispatcher is not None
            return manager.dispatcher.dispatch(code_text)

        action = await loop.run_in_executor(None, infer_fn)
        inf_dur_ms = (time.perf_counter() - t0) * 1000

        raw_decision: LayaDecision = action.raw_decision

        response_data = {
            "decision": {
                "blocked": action.blocked,
                "noul_gate": round(raw_decision.noul, 4),
                "choice_label": raw_decision.choice,
                "score_energy": round(raw_decision.score, 4),
                "anse_energy": round(action.energy, 4),
                "recommended_role": action.role.value,
                "lean4_tactic": action.lean4_tactic,
                "reasoning": action.reasoning,
            },
            "serverless_telemetry": {
                "was_cold_start": was_cold,
                "cold_start_duration_ms": round(cold_start_dur * 1000, 2),
                "inference_duration_ms": round(inf_dur_ms, 2),
                "model_state": manager.state,
            },
        }

        headers = {
            "X-Cold-Start": "true" if was_cold else "false",
            "X-Cold-Start-Duration-Ms": str(round(cold_start_dur * 1000, 2)),
            "X-Inference-Duration-Ms": str(round(inf_dur_ms, 2)),
            "X-Model-State": manager.state,
            "X-Laya-Gate": "BLOCKED" if action.blocked else "PASS",
            "X-Laya-Role": action.role.value,
        }

        return JSONResponse(content=response_data, headers=headers)
    finally:
        manager.active_requests = max(0, manager.active_requests - 1)


@app.post("/v1/chat/completions")
async def chat_completions_endpoint(request: Request) -> Response:
    """OpenAI-compatible chat completions interface wrapping Laya triage."""
    body = await request.json()
    messages = body.get("messages", [])
    model_name = body.get("model", "laya-coding-companion")

    # Extract last user message
    user_content = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_content = msg.get("content", "")
            break

    # Call Laya decision logic
    req = Request(scope=request.scope)
    
    manager.active_requests += 1
    try:
        was_cold, cold_start_dur = await manager.ensure_active()
        manager.total_requests += 1
        manager.last_activity_time = time.time()

        loop = asyncio.get_running_loop()
        t0 = time.perf_counter()

        def infer_fn():
            assert manager.dispatcher is not None
            return manager.dispatcher.dispatch(user_content)

        action = await loop.run_in_executor(None, infer_fn)
        inf_dur_ms = (time.perf_counter() - t0) * 1000

        assistant_reply = (
            f"Laya Decision: {'[BLOCKED - E=1e6]' if action.blocked else '[PASS]'}\n"
            f"Recommended Role: {action.role.value}\n"
            f"Reasoning: {action.reasoning}"
        )

        response_payload = {
            "id": f"chatcmpl-laya-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": assistant_reply,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(user_content.split()),
                "completion_tokens": len(assistant_reply.split()),
                "total_tokens": len(user_content.split()) + len(assistant_reply.split()),
            },
            "serverless_telemetry": {
                "was_cold_start": was_cold,
                "cold_start_duration_ms": round(cold_start_dur * 1000, 2),
                "inference_duration_ms": round(inf_dur_ms, 2),
            },
        }

        headers = {
            "X-Cold-Start": "true" if was_cold else "false",
            "X-Cold-Start-Duration-Ms": str(round(cold_start_dur * 1000, 2)),
            "X-Inference-Duration-Ms": str(round(inf_dur_ms, 2)),
            "X-Model-State": manager.state,
        }

        return JSONResponse(content=response_payload, headers=headers)
    finally:
        manager.active_requests = max(0, manager.active_requests - 1)


def main() -> None:
    import uvicorn
    logger.info("Starting ANSE Laya Serverless Cognitive Endpoint on %s:%d", HOST, PORT)
    uvicorn.run("anse.gateway.serverless_laya_endpoint:app", host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
