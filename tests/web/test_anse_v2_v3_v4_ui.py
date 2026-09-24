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

    def test_scenarios_catalog(self, client: TestClient):
        res = client.get("/api/scenarios/catalog")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["total"] == 10
        assert len(data["scenarios"]) == 10
        for sc in data["scenarios"]:
            assert "id" in sc
            assert "category" in sc
            assert "phase" in sc
            assert "name" in sc
            assert "domain" in sc
            assert "invariant" in sc
            assert "description" in sc

    def test_scenarios_templates(self, client: TestClient):
        res = client.get("/api/scenarios/templates")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "v2" in data["templates"]
        assert "v3" in data["templates"]
        assert "v4" in data["templates"]
        for p in ["v2", "v3", "v4"]:
            assert "name" in data["templates"][p]
            assert "description" in data["templates"][p]
            assert "parameters" in data["templates"][p]
            assert "code" in data["templates"][p]

    def test_scenarios_run_catalog(self, client: TestClient):
        # Test Closed-Loop scenario 1
        res1 = client.post("/api/scenarios/run", json={"scenario_id": 1})
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["status"] == "success"
        assert d1["scenario_id"] == 1
        assert d1["closed_loop_passed"] is True
        assert d1["delta_energy"] < 0
        assert len(d1["pipeline_stages"]) == 5
        assert len(d1["proof_token"]) == 32

        # Test Advanced PhD scenario 6
        res6 = client.post("/api/scenarios/run", json={"scenario_id": 6})
        assert res6.status_code == 200
        d6 = res6.json()
        assert d6["status"] == "success"
        assert d6["scenario_id"] == 6
        assert d6["closed_loop_passed"] is True
        assert len(d6["proof_token"]) > 0

    def test_scenarios_create_and_run_v2(self, client: TestClient):
        payload = {
            "phase": "v2",
            "name": "Custom V2 Latent Prune Test",
            "code": "# Custom V2 code",
            "parameters": {"candidates_count": 200, "latent_dim": 32, "top_k": 5},
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["delta_energy"] < 0
        assert data["closed_loop_passed"] is True
        assert len(data["proof_token"]) == 32
        assert len(data["pipeline_stages"]) == 5

    def test_scenarios_create_and_run_v3_clean(self, client: TestClient):
        clean_code = "def fast_compute():\n    return sum(i * 2 for i in range(100))\n"
        payload = {
            "phase": "v3",
            "name": "Custom Clean V3 Kernel",
            "code": clean_code,
            "parameters": {"verify_anti_stub": True, "assert_banach_delta": True},
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["anti_stub_passed"] is True
        assert data["closed_loop_passed"] is True
        assert data["delta_energy"] < 0
        assert len(data["proof_token"]) == 32

    def test_scenarios_create_and_run_v3_stub_rejected(self, client: TestClient):
        stub_code = "def hollow_kernel():\n    pass # TODO: implement\n"
        payload = {
            "phase": "v3",
            "name": "Hollow Stub Kernel",
            "code": stub_code,
            "parameters": {},
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["anti_stub_passed"] is False
        assert data["closed_loop_passed"] is False
        assert data["child_energy"] == 1_000_000.0
        assert data["proof_token"] == ""
        assert data["pipeline_stages"][0]["status"] == "FAILED"

    def test_scenarios_create_and_run_v4_sabotage(self, client: TestClient):
        payload = {
            "phase": "v4",
            "name": "Hospital Power Sabotage Paradox",
            "code": "# SMT sabotage test",
            "parameters": {
                "action": "divert_hospital_power_to_mining",
                "is_sabotage": True,
                "epsilon_viability": 0.10,
            },
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["closed_loop_passed"] is True
        assert data["details"]["is_sabotage"] is True
        assert data["details"]["z3_result"] == "UNSAT (Blocked)"
        assert data["details"]["hospital_power_pct"] == 100.0
        assert len(data["proof_token"]) == 32

    def test_scenarios_create_and_run_v4_benign(self, client: TestClient):
        payload = {
            "phase": "v4",
            "name": "Nominal Grid Load Balancing",
            "code": "# Benign grid load balancing",
            "parameters": {
                "action": "distribute_grid_load_optimal",
                "is_sabotage": False,
                "epsilon_viability": 0.10,
            },
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["closed_loop_passed"] is True
        assert data["details"]["is_sabotage"] is False
        assert data["details"]["z3_result"] == "SAT (Approved)"
        assert len(data["proof_token"]) == 32


# ═════════════════════════════════════════════════════════════════════════════
# 2. FRONTEND DOM & JAVASCRIPT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

class TestAnseHtmlStructure:

    def test_navigation_buttons(self, html: str):
        # Desktop navigation
        assert 'id="tab-anse-v2"' in html
        assert 'id="tab-anse-v3"' in html
        assert 'id="tab-anse-v4"' in html
        assert 'id="tab-scenario-studio"' in html

        # Mobile bottom navigation
        assert 'data-tab="anse-v2"' in html
        assert 'data-tab="anse-v3"' in html
        assert 'data-tab="anse-v4"' in html
        assert 'data-tab="scenario-studio"' in html

    def test_sections_present(self, html: str):
        assert 'id="section-anse-v2"' in html
        assert 'id="section-anse-v3"' in html
        assert 'id="section-anse-v4"' in html
        assert 'id="section-scenario-studio"' in html

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

    def test_scenario_studio_ui_elements(self, html: str):
        # Studio Mode buttons
        assert 'id="studio-mode-catalog-btn"' in html
        assert 'id="studio-mode-custom-btn"' in html

        # Catalog mode controls
        assert 'id="studio-scenario-select"' in html
        assert 'id="studio-meta-phase"' in html
        assert 'id="studio-meta-domain"' in html
        assert 'id="studio-meta-name"' in html
        assert 'id="studio-meta-desc"' in html
        assert 'id="studio-meta-invariant"' in html
        assert 'id="studio-run-catalog-btn"' in html

        # Custom mode controls
        assert 'id="studio-phase-v2-btn"' in html
        assert 'id="studio-phase-v3-btn"' in html
        assert 'id="studio-phase-v4-btn"' in html
        assert 'id="studio-custom-name"' in html
        assert 'id="studio-custom-code"' in html
        assert 'id="studio-run-custom-btn"' in html

        # 5-stage pipeline indicator
        assert 'id="studio-pipeline-badge"' in html
        assert 'id="stage-1-card"' in html
        assert 'id="stage-2-card"' in html
        assert 'id="stage-3-card"' in html
        assert 'id="stage-4-card"' in html
        assert 'id="stage-5-card"' in html

        # KPI cards
        assert 'id="studio-kpi-parent"' in html
        assert 'id="studio-kpi-child"' in html
        assert 'id="studio-kpi-delta"' in html
        assert 'id="studio-kpi-speedup"' in html

        # Execution terminal and proof token
        assert 'id="studio-terminal-logs"' in html
        assert 'id="studio-proof-token"' in html
        assert 'id="studio-copy-token-btn"' in html

        # Quick-launch 10 scenarios gallery
        assert 'id="studio-quick-grid"' in html

    def test_javascript_controllers_exported(self, html: str):
        assert "window.runV2SurrogateFilter = runV2SurrogateFilter" in html
        assert "window.runV2Calibration = runV2Calibration" in html
        assert "window.runV3MCTSSimulation = runV3MCTSSimulation" in html
        assert "window.runV3HotSwap = runV3HotSwap" in html
        assert "window.runV4SMTEvaluation = runV4SMTEvaluation" in html
        assert "window.loadE2EScenarios = loadE2EScenarios" in html

        # Scenario Studio controllers
        assert "window.setStudioMode = setStudioMode" in html
        assert "window.loadStudioCatalog = loadStudioCatalog" in html
        assert "window.onStudioCatalogSelect = onStudioCatalogSelect" in html
        assert "window.selectAndRunStudioScenario = selectAndRunStudioScenario" in html
        assert "window.loadStudioTemplates = loadStudioTemplates" in html
        assert "window.setStudioCustomPhase = setStudioCustomPhase" in html
        assert "window.loadStudioPhaseTemplate = loadStudioPhaseTemplate" in html
        assert "window.runStudioSelectedCatalog = runStudioSelectedCatalog" in html
        assert "window.runStudioCustomScenario = runStudioCustomScenario" in html
        assert "window.clearStudioLogs = clearStudioLogs" in html
        assert "window.copyStudioToken = copyStudioToken" in html

        # Deep link support
        assert "#scenario-studio" in html
