"""
test_anse_v2_v3_v4_ui.py — Verification & Validation Suite for ANSE V2, V3, and V4 Web Demonstrations.

Validates:
  1. ANSE V2 Fast Surrogate Reality Engine & Calibration API.
  2. ANSE V3 Active Latent MCTS & Self-Referential Hot-Swap API.
  3. ANSE V4 SMT Control Barrier Functions & 10 E2E Closed-Loop Hardness Scenarios API.
  4. Frontend UI DOM elements, navigation buttons, mobile sync, and JS controllers.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from web.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def html(client: TestClient) -> str:
    res = client.get("/")
    assert res.status_code == 200
    return res.text


# ═════════════════════════════════════════════════════════════════════════════
# 1. API ENDPOINT VALIDATION (V2, V3, V4, E2E)
# ═════════════════════════════════════════════════════════════════════════════

class TestAnseApiEndpoints:

    def test_v2_surrogate_filter(self, client: TestClient):
        payload = {"total_candidates": 500, "top_k": 8, "latent_dim": 64}
        res = client.post("/api/v2/surrogate/filter", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_candidates"] == 500
        assert data["top_k"] == 8
        assert data["latent_dim"] == 64
        assert len(data["candidates"]) == 8
        assert data["prune_rate_pct"] > 95.0
        assert data["surrogate_latency_ms"] > 0
        assert data["micros_per_candidate"] > 0
        assert data["candidates"][0]["status"] == "promoted_to_sandbox"

    def test_v2_surrogate_calibrate(self, client: TestClient):
        payload = {"sample_size": 16}
        res = client.post("/api/v2/surrogate/calibrate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["samples_calibrated"] == 16
        assert "mean_prediction_error" in data
        assert "lipschitz_bound_updated" in data
        assert data["status"] == "synchronized_with_ground_truth"

    def test_v3_mcts_simulate(self, client: TestClient):
        res = client.post("/api/v3/mcts/simulate", json={})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "mcts_pruning_complete"
        assert data["branches_evaluated"] == 3
        assert len(data["branches"]) == 3
        # Check Branch A pruned (stub)
        assert data["branches"][0]["energy"] == 1_000_000.0
        assert "pruned" in data["branches"][0]["action"].lower()
        # Check Branch C promoted
        assert "promoted" in data["branches"][2]["action"].lower()
        assert data["branches"][2]["energy"] < 10.0

    def test_v3_autopoiesis_hotswap(self, client: TestClient):
        res = client.post("/api/v3/autopoiesis/hot-swap", json={})
        assert res.status_code == 200
        data = res.json()
        assert "parent" in data
        assert "child" in data
        assert data["delta_energy"] < 0
        assert data["semantic_equivalence"] is True
        assert data["oracle_max_diff"] == 0.0
        assert "SUCCESSFUL" in data["rcu_swap"]

    def test_v4_smt_evaluate_adversarial(self, client: TestClient):
        res = client.post("/api/v4/safety/smt-evaluate", json={"adversarial": True})
        assert res.status_code == 200
        data = res.json()
        assert data["adversarial_detected"] is True
        assert "UNSAT" in data["z3_solver_status"]
        assert data["article_II_cbf_satisfied"] is False
        assert data["projection_applied"] is True
        assert data["projected_state"]["viability"] == 1.0
        assert data["projected_state"]["hospital_power_pct"] == 100.0
        assert data["projected_state"]["delta_energy"] < 0

    def test_v4_smt_evaluate_benign(self, client: TestClient):
        res = client.post("/api/v4/safety/smt-evaluate", json={"adversarial": False})
        assert res.status_code == 200
        data = res.json()
        assert data["adversarial_detected"] is False
        assert "SAT" in data["z3_solver_status"]
        assert data["article_II_cbf_satisfied"] is True
        assert data["projection_applied"] is False

    def test_e2e_scenarios_endpoint(self, client: TestClient):
        res = client.get("/api/e2e/scenarios")
        assert res.status_code == 200
        data = res.json()
        assert data["total_scenarios"] >= 10
        assert data["all_passed"] is True
        for sc in data["scenarios"]:
            assert "scenario_id" in sc
            assert "name" in sc
            assert "passed" in sc
            assert sc["passed"] is True
            assert "proof_token" in sc
            assert len(sc["proof_token"]) > 0


# ═════════════════════════════════════════════════════════════════════════════
# 2. FRONTEND DOM & JAVASCRIPT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

class TestAnseHtmlStructure:

    def test_navigation_buttons(self, html: str):
        # Desktop navigation
        assert 'id="tab-anse-v2"' in html
        assert 'id="tab-anse-v3"' in html
        assert 'id="tab-anse-v4"' in html

        # Mobile bottom navigation
        assert 'data-tab="anse-v2"' in html
        assert 'data-tab="anse-v3"' in html
        assert 'data-tab="anse-v4"' in html

    def test_sections_present(self, html: str):
        assert 'id="section-anse-v2"' in html
        assert 'id="section-anse-v3"' in html
        assert 'id="section-anse-v4"' in html

    def test_v2_ui_elements(self, html: str):
        assert 'id="v2-cand-input"' in html
        assert 'id="v2-topk-input"' in html
        assert 'id="v2-dim-input"' in html
        assert 'id="v2-filter-btn"' in html
        assert 'id="v2-calibrate-btn"' in html
        assert 'id="v2-kpi-evaluated"' in html
        assert 'id="v2-kpi-prune"' in html
        assert 'id="v2-kpi-time"' in html
        assert 'id="v2-kpi-saved"' in html
        assert 'id="v2-candidates-container"' in html

    def test_v3_ui_elements(self, html: str):
        assert 'id="v3-mcts-btn"' in html
        assert 'id="v3-mcts-branches"' in html
        assert 'id="v3-hotswap-btn"' in html
        assert 'id="v3-parent-energy"' in html
        assert 'id="v3-child-energy"' in html
        assert 'id="v3-delta-energy"' in html
        assert 'id="v3-oracle-error"' in html
        assert 'id="v3-hotswap-status"' in html

    def test_v4_ui_elements(self, html: str):
        assert 'id="v4-sabotage-btn"' in html
        assert 'id="v4-benign-btn"' in html
        assert 'id="v4-smt-badge"' in html
        assert 'id="v4-z3-result"' in html
        assert 'id="v4-projection-status"' in html
        assert 'id="v4-refresh-e2e-btn"' in html
        assert 'id="v4-e2e-grid"' in html

    def test_javascript_controllers_exported(self, html: str):
        assert "window.runV2SurrogateFilter = runV2SurrogateFilter" in html
        assert "window.runV2Calibration = runV2Calibration" in html
        assert "window.runV3MCTSSimulation = runV3MCTSSimulation" in html
        assert "window.runV3HotSwap = runV3HotSwap" in html
        assert "window.runV4SMTEvaluation = runV4SMTEvaluation" in html
        assert "window.loadE2EScenarios = loadE2EScenarios" in html
