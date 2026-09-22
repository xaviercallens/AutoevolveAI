"""
test_factory_api.py — Unit tests for the PR Factory API endpoints.

Tests mission dispatch, listing, CI status, reviews, and history.
Uses FastAPI TestClient (no running server needed).
"""

from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _factory_db_tmp(tmp_path, monkeypatch):
    """Use a temporary SQLite database for each test."""
    db_path = tmp_path / "test_missions.db"
    monkeypatch.setenv("FACTORY_DB_PATH", str(db_path))
    # Force the module to pick up the new path
    from web import factory
    factory.DB_PATH = db_path


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from web.server import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestDispatchEndpoint:
    def test_dispatch_valid_performance(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "performance",
            "target": "anse/symbolic/sandbox.py",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("dispatched", "queued")
        assert data["mission_type"] == "performance"
        assert data["target"] == "anse/symbolic/sandbox.py"
        assert len(data["id"]) > 0

    def test_dispatch_valid_qa_fuzzing(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "qa_fuzzing",
            "target": "anse/jepa",
        })
        assert resp.status_code == 200
        assert resp.json()["mission_type"] == "qa_fuzzing"

    def test_dispatch_valid_security(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "security",
            "target": "gateway.py",
        })
        assert resp.status_code == 200

    def test_dispatch_valid_lean_proof(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "lean_proof",
            "target": "formal/ANSE/Autopoiesis.lean",
        })
        assert resp.status_code == 200

    def test_dispatch_valid_custom(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "custom",
            "target": "README.md",
            "description": "Update the README with deployment instructions",
        })
        assert resp.status_code == 200
        assert resp.json()["mission_type"] == "custom"

    def test_dispatch_invalid_type(self, client):
        resp = client.post("/api/factory/dispatch", json={
            "mission_type": "nonexistent",
            "target": "foo.py",
        })
        assert resp.status_code == 422  # Pydantic validation error

    def test_dispatch_creates_record_in_db(self, client):
        # Dispatch a mission
        resp1 = client.post("/api/factory/dispatch", json={
            "mission_type": "performance",
            "target": "test.py",
        })
        mission_id = resp1.json()["id"]

        # Verify it appears in the missions list
        resp2 = client.get("/api/factory/missions")
        all_ids = [
            m["id"]
            for m in resp2.json()["active"] + resp2.json()["completed"]
        ]
        assert mission_id in all_ids


class TestMissionsEndpoint:
    def test_empty_missions(self, client):
        resp = client.get("/api/factory/missions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["active"] == []
        assert data["completed"] == []

    def test_missions_after_dispatch(self, client):
        client.post("/api/factory/dispatch", json={
            "mission_type": "security",
            "target": "gateway.py",
        })
        resp = client.get("/api/factory/missions")
        data = resp.json()
        assert data["total"] == 1


class TestCIStatusEndpoint:
    def test_ci_status_no_pr(self, client):
        """Without a GitHub token, CI status returns no_pr or pending."""
        resp = client.get("/api/factory/ci-status")
        assert resp.status_code == 200
        data = resp.json()
        # Without GitHub token, we expect no_pr or empty pillars
        assert data["overall"] in ("no_pr", "pending")


class TestHistoryEndpoint:
    def test_empty_history(self, client):
        resp = client.get("/api/factory/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["total"] == 0
        assert data["missions"] == []

    def test_history_pagination(self, client):
        # Dispatch 3 missions
        for i in range(3):
            client.post("/api/factory/dispatch", json={
                "mission_type": "performance",
                "target": f"module_{i}.py",
            })

        # Page 1 with per_page=2
        resp = client.get("/api/factory/history?page=1&per_page=2")
        data = resp.json()
        assert len(data["missions"]) == 2
        assert data["total"] == 3
        assert data["total_pages"] == 2

        # Page 2
        resp2 = client.get("/api/factory/history?page=2&per_page=2")
        data2 = resp2.json()
        assert len(data2["missions"]) == 1


class TestReviewsEndpoint:
    def test_reviews_without_token(self, client):
        """Without a GitHub token, reviews should return empty or gracefully fail."""
        resp = client.get("/api/factory/reviews")
        assert resp.status_code == 200
        data = resp.json()
        assert "reviews" in data
