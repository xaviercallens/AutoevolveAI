"""
tests/test_serverless_laya_endpoint.py
======================================
Tests for Laya Serverless Scale-to-Zero Endpoint & HTTP Autoscaler.
"""
import pytest
from fastapi.testclient import TestClient

from anse.gateway.serverless_laya_endpoint import app, manager


@pytest.fixture(autouse=True)
def ensure_dormant_state():
    """Ensure manager is in a known state before each test."""
    if manager.is_active():
        manager.unload_model()
    yield
    if manager.is_active():
        manager.unload_model()


def test_health_dormant_state():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["state"] == "DORMANT"
    assert data["is_model_loaded"] is False
    assert data["min_replicas"] == 0
    assert data["cost_state"] == "$0.00 (dormant, scale-to-zero active)"


def test_cost_telemetry():
    client = TestClient(app)
    resp = client.get("/v1/cost")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "zero_cost_dormant"
    assert data["scale_to_zero_enforced"] is True
    assert data["idle_compute_cost"] == "$0.00"


def test_http_autoscaler_metrics():
    client = TestClient(app)
    resp = client.get("/v1/scale")
    assert resp.status_code == 200
    data = resp.json()
    assert data["autoscaler_policy"] == "http_concurrency_autoscaler"
    assert data["min_replicas"] == 0
    assert data["recommended_replica_count"] == 0
    assert data["scaling_action"] == "SCALE_DOWN_TO_ZERO"


def test_laya_decision_cold_start_and_warm():
    client = TestClient(app)
    
    # 1. First request triggers Cold Start
    assert manager.state == "DORMANT"
    resp1 = client.post("/v1/laya/decision", json={"code": "def solve(): pass"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "decision" in data1
    assert "serverless_telemetry" in data1
    assert resp1.headers.get("X-Cold-Start") == "true"
    assert manager.state == "ACTIVE"

    # 2. Second request is Warm
    resp2 = client.post("/v1/laya/decision", json={"code": "def binary_search(): return 0"})
    assert resp2.status_code == 200
    assert resp2.headers.get("X-Cold-Start") == "false"


def test_chat_completions_endpoint():
    client = TestClient(app)
    payload = {
        "messages": [
            {"role": "system", "content": "You are a coding assistant."},
            {"role": "user", "content": "theorem nat_add_comm : a + b = b + a := by omega"},
        ]
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "Laya Decision" in data["choices"][0]["message"]["content"]


def test_manual_unload_scale_to_zero():
    client = TestClient(app)
    
    # Warm up first
    client.post("/v1/laya/decision", json={"code": "def foo(): return 1"})
    assert manager.state == "ACTIVE"

    # Unload
    resp = client.post("/v1/unload")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unloaded"
    assert manager.state == "DORMANT"
