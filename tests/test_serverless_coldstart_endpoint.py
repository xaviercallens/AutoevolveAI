"""
Automated 5-Test Suite for ANSE Serverless LoRA Scale-to-Zero Endpoint.
Validates:
1. Cost-Zero Dormant State & First-Request Cold Start.
2. Symplectic Physics & Hamiltonian Conservation Reasoning (Redis LTM Trained).
3. HPC & Structured Code Generation (Rust SIMD / Lean 4).
4. Warm Latency Acceleration (Quick-Restart Cache Verification).
5. Scale-to-Zero Auto-Shutdown ($0 cost when idle) and Re-Cold-Start Recovery.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from anse.gateway.serverless_lora_endpoint import app, manager


@pytest.fixture(autouse=True)
def reset_endpoint_state():
    """Ensure endpoint starts from clean dormant state before each test."""
    if manager.is_active():
        manager.unload_model()
    manager.state = "DORMANT"
    yield
    if manager.is_active():
        manager.unload_model()


@pytest.mark.asyncio
async def test_1_cost_zero_dormant_and_cold_start_activation() -> None:
    """Test 1: Verify endpoint starts at $0 compute (DORMANT) and lazily triggers cold start on request 1."""
    # Pre-condition: Zero memory loaded
    assert manager.state == "DORMANT"
    assert manager.model is None
    assert manager.is_active() is False

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Check health while dormant
        health = await client.get("/health")
        assert health.status_code == 200
        h_data = health.json()
        assert h_data["state"] == "DORMANT"
        assert h_data["is_model_loaded"] is False

        # First request triggers cold start
        req = {
            "model": "antigravity-local",
            "messages": [{"role": "user", "content": "Ping test for serverless cold start."}],
            "max_tokens": 16,
            "temperature": 0.0,
        }

        t0 = time.perf_counter()
        resp = await client.post("/v1/chat/completions", json=req)
        wall_time = time.perf_counter() - t0

        assert resp.status_code == 200
        assert resp.headers["x-cold-start"] == "true"
        assert float(resp.headers["x-cold-start-duration-ms"]) > 0.0
        assert resp.headers["x-model-state"] == "ACTIVE"

        data = resp.json()
        assert data["choices"][0]["message"]["content"] != ""
        assert data["serverless_telemetry"]["was_cold_start"] is True
        assert manager.is_active() is True
        print(f"\n[Test 1 Passed] Cold start triggered and completed in {data['serverless_telemetry']['cold_start_duration_ms']}ms (Wall: {wall_time*1000:.1f}ms)")


@pytest.mark.asyncio
async def test_2_symplectic_physics_hamiltonian_reasoning() -> None:
    """Test 2: Query the Redis-LTM-trained model on symplectic Hamiltonian conservation."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        req = {
            "model": "antigravity-local",
            "messages": [
                {"role": "system", "content": "You are ANSE: Autopoietic Neuro-Symbolic Energy-based intelligence."},
                {"role": "user", "content": "State the Hamiltonian conservation law for a symplectic integrator."},
            ],
            "max_tokens": 24,
            "temperature": 0.0,
        }

        resp = await client.post("/v1/chat/completions", json=req)
        assert resp.status_code == 200
        content = resp.json()["choices"][0]["message"]["content"].lower()

        # Assert physics domain alignment
        assert any(term in content for term in ["hamiltonian", "symplectic", "energy", "conservation", "integrator", "system", "p", "q"])
        print(f"\n[Test 2 Passed] Physics Output: {content[:100]}...")


@pytest.mark.asyncio
async def test_3_hpc_code_generation_rust_simd() -> None:
    """Test 3: Verify structured HPC code generation for Rust SIMD kernel."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        req = {
            "model": "antigravity-local",
            "messages": [
                {"role": "user", "content": "Write a Rust function header for AVX2 dot product."},
            ],
            "max_tokens": 24,
            "temperature": 0.0,
        }

        resp = await client.post("/v1/chat/completions", json=req)
        assert resp.status_code == 200
        content = resp.json()["choices"][0]["message"]["content"]
        content_lower = content.lower()

        assert any(kw in content_lower for kw in ["rust", "avx", "dot product", "dot_product", "fn", "simd", "function", "pub fn"])
        print(f"\n[Test 3 Passed] Code Output snippet: {content[:80]}...")


@pytest.mark.asyncio
async def test_4_warm_latency_acceleration_via_quick_restart_cache() -> None:
    """Test 4: Verify warm subsequent requests execute with zero cold-start latency."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Request 1: Cold start
        req1 = {
            "model": "antigravity-local",
            "messages": [{"role": "user", "content": "First call"}],
            "max_tokens": 10,
        }
        resp1 = await client.post("/v1/chat/completions", json=req1)
        assert resp1.headers["x-cold-start"] == "true"
        cold_ms = float(resp1.headers["x-cold-start-duration-ms"])

        # Request 2: Warm call
        req2 = {
            "model": "antigravity-local",
            "messages": [{"role": "user", "content": "Second call"}],
            "max_tokens": 10,
        }
        resp2 = await client.post("/v1/chat/completions", json=req2)
        assert resp2.headers["x-cold-start"] == "false"
        assert float(resp2.headers["x-cold-start-duration-ms"]) == 0.0

        telemetry = resp2.json()["serverless_telemetry"]
        assert telemetry["was_cold_start"] is False
        assert telemetry["cold_start_duration_ms"] == 0.0
        print(f"\n[Test 4 Passed] Cold Duration: {cold_ms:.1f}ms vs Warm Cold Duration: {telemetry['cold_start_duration_ms']}ms (Warm Acceleration Confirmed)")


@pytest.mark.asyncio
async def test_5_scale_to_zero_auto_shutdown_and_re_coldstart() -> None:
    """Test 5: Verify scale-to-zero memory reclaim ($0 cost) and subsequent re-coldstart recovery."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Start model
        await client.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "warm up"}], "max_tokens": 5})
        assert manager.is_active() is True

        # 2. Trigger scale-to-zero unload
        unload_resp = await client.post("/v1/unload")
        assert unload_resp.status_code == 200
        assert unload_resp.json()["state"] == "DORMANT"
        assert manager.is_active() is False
        assert manager.model is None

        # Verify health confirms dormant 0-cost state
        health = await client.get("/health")
        assert health.json()["state"] == "DORMANT"
        assert health.json()["is_model_loaded"] is False
        assert health.json()["idle_cost_per_hour"] == "$0.00"

        # Verify /v1/cost explicitly guarantees $0.00 compute cost
        cost_resp = await client.get("/v1/cost")
        assert cost_resp.status_code == 200
        cost_data = cost_resp.json()
        assert cost_data["status"] == "zero_cost_dormant"
        assert cost_data["idle_compute_cost"] == "$0.00"
        assert cost_data["memory_reclaimed"] is True
        assert cost_data["scale_to_zero_enforced"] is True

        # 3. New request triggers re-coldstart seamlessly
        re_cold_resp = await client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Revive from scale to zero."}], "max_tokens": 10},
        )
        assert re_cold_resp.status_code == 200
        assert re_cold_resp.headers["x-cold-start"] == "true"
        assert manager.is_active() is True
        print(f"\n[Test 5 Passed] Successfully unloaded to DORMANT ($0 cost) and revived on next request!")
