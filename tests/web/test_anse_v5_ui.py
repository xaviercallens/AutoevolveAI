"""
test_anse_v5_ui.py — Verification Suite for ANSE V5 Web Endpoints & UI Demonstration.

Validates:
  1. ANSE V5 Autonomous Science Curricula API (/api/v5/curricula).
  2. ANSE V5 Laya System 1 Non-Autoregressive Triage API (/api/v5/laya/triage).
  3. ANSE V5 Rosetta Stone Triplet Verification API (/api/v5/rosetta/verify).
  4. ANSE V5 GRPO Test-Time Compute Explorer API (/api/v5/grpo/explore).
  5. Scenario Studio V5 template and execution (/api/scenarios/templates, /api/scenarios/create-and-run).
  6. Frontend UI DOM elements, navigation buttons, and JavaScript exports in index.html.
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
# 1. API ENDPOINT VALIDATION (V5)
# ═════════════════════════════════════════════════════════════════════════════

class TestAnseV5ApiEndpoints:

    def test_get_curricula(self, client: TestClient):
        res = client.get("/api/v5/curricula")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert len(data["curricula"]) >= 3
        ids = [c["id"] for c in data["curricula"]]
        assert "kdv_soliton_momentum" in ids
        assert "yang_mills_instanton" in ids
        assert "chern_number_quantum_hall" in ids

    def test_laya_triage_choice(self, client: TestClient):
        payload = {
            "text": "Theorem: The exterior derivative satisfies d(d(omega)) = 0. The L2 norm is conserved.",
            "decision_type": "choice",
            "criteria": "sound, unsound, needs_proof"
        }
        res = client.post("/api/v5/laya/triage", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["decision_type"] == "choice"
        assert data["choice"] in ["sound", "unsound", "needs_proof"]
        assert "probabilities" in data
        assert sum(data["probabilities"].values()) == pytest.approx(1.0, rel=1e-2)
        assert data["latency_ms"] > 0

    def test_laya_triage_score(self, client: TestClient):
        payload = {
            "text": "Hypothesis: Topological invariants are preserved across continuous deformation.",
            "decision_type": "score",
            "criteria": "1-5 rating"
        }
        res = client.post("/api/v5/laya/triage", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["decision_type"] == "score"
        assert 1.0 <= data["score"] <= 5.0
        assert data["latency_ms"] > 0

    def test_laya_triage_noul(self, client: TestClient):
        payload = {
            "text": "Hypothesis: Invariant energy conservation holds.",
            "decision_type": "noul",
            "criteria": "assertion truth"
        }
        res = client.post("/api/v5/laya/triage", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["decision_type"] == "noul"
        assert 0.0 <= data["truth_probability"] <= 1.0
        assert data["latency_ms"] > 0

    def test_rosetta_verify_kdv(self, client: TestClient):
        payload = {"problem_id": "kdv_soliton_momentum"}
        res = client.post("/api/v5/rosetta/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["problem_id"] == "kdv_soliton_momentum"
        assert data["theorist_lean4"]["status"] == "SOUND"
        assert data["physicist_prototype"]["status"] == "CONSERVED"
        assert data["physicist_prototype"]["invariant_conserved"] is True
        assert data["engineer_kernel"]["status"] == "OPTIMIZED"
        assert data["engineer_kernel"]["delta_energy"] < 0
        assert data["engineer_kernel"]["speedup"] > 1.0
        assert data["triplet_verified"] is True
        assert len(data["proof_token"]) == 32

    def test_rosetta_verify_yang_mills(self, client: TestClient):
        payload = {"problem_id": "yang_mills_instanton"}
        res = client.post("/api/v5/rosetta/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["theorist_lean4"]["status"] == "SOUND"
        assert data["physicist_prototype"]["invariant_conserved"] is True
        assert data["triplet_verified"] is True
        assert len(data["proof_token"]) == 32

    def test_rosetta_verify_chern(self, client: TestClient):
        payload = {"problem_id": "chern_number_quantum_hall"}
        res = client.post("/api/v5/rosetta/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["theorist_lean4"]["status"] == "SOUND"
        assert data["triplet_verified"] is True
        assert len(data["proof_token"]) == 32

    def test_grpo_explore(self, client: TestClient):
        payload = {"hypothesis_id": "kdv_soliton_momentum"}
        res = client.post("/api/v5/grpo/explore", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert len(data["trajectories"]) == 8
        assert 0 <= data["best_index"] < 8
        assert data["best_trajectory"]["closed_loop_passed"] is True
        # Check advantages normalize with zero mean
        advantages = [t["advantage"] for t in data["trajectories"]]
        assert pytest.approx(sum(advantages), abs=1e-3) == 0.0

    def test_scenario_studio_v5_template(self, client: TestClient):
        res = client.get("/api/scenarios/templates")
        assert res.status_code == 200
        data = res.json()
        assert "v5" in data["templates"]
        v5_tpl = data["templates"]["v5"]
        assert "Rosetta" in v5_tpl["name"]
        assert "The Theorist" in v5_tpl["code"]
        assert "hypothesis_id" in v5_tpl["parameters"]

    def test_scenario_studio_v5_create_and_run(self, client: TestClient):
        payload = {
            "phase": "v5",
            "name": "E2E Rosetta Stone Invariant Test",
            "code": "def compute_conserved_invariant(u):\n    return float(sum(x**2 for x in u))\nres = compute_conserved_invariant([1.0, 2.0, 3.0])\n",
            "parameters": {
                "hypothesis_id": "kdv_soliton_momentum",
                "tolerance": 0.0001,
                "trajectories_count": 8
            }
        }
        res = client.post("/api/scenarios/create-and-run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "V5" in data["phase"]
        assert data["closed_loop_passed"] is True
        assert data["delta_energy"] < 0
        assert data["speedup"] > 1.0
        assert len(data["proof_token"]) == 32
        assert len(data["pipeline_stages"]) == 5
        for stage in data["pipeline_stages"]:
            assert stage["status"] in ["PASSED", "ATTESTED"]


# ═════════════════════════════════════════════════════════════════════════════
# 2. FRONTEND HTML DOM & JAVASCRIPT VALIDATION (V5)
# ═════════════════════════════════════════════════════════════════════════════

class TestAnseV5FrontendUI:

    def test_v5_navigation_tabs(self, html: str):
        # Desktop Nav
        assert 'id="tab-anse-v5"' in html
        assert 'ANSE V5: Science &amp; Rosetta' in html or 'ANSE V5: Science & Rosetta' in html
        # Mobile Nav
        assert 'data-tab="anse-v5"' in html

    def test_v5_section_exists(self, html: str):
        assert 'id="section-anse-v5"' in html
        assert 'ANSE V5: Cross-Domain Rosetta Stone &amp; System 1 Laya (CPU)' in html or 'ANSE V5: Cross-Domain Rosetta Stone & System 1 Laya (CPU)' in html

    def test_v5_deck1_laya_dom(self, html: str):
        assert 'id="v5-laya-input"' in html
        assert 'id="v5-laya-type"' in html
        assert 'id="v5-laya-criteria"' in html
        assert 'id="v5-laya-triage-btn"' in html
        assert 'id="v5-laya-decision-badge"' in html
        assert 'id="v5-laya-latency"' in html
        assert 'id="v5-laya-prob-container"' in html
        assert 'setV5LayaPreset' in html
        assert 'runV5LayaTriage' in html

    def test_v5_deck2_rosetta_dom(self, html: str):
        assert 'id="v5-rosetta-select"' in html
        assert 'id="v5-rosetta-run-btn"' in html
        assert 'id="v5-rosetta-lean-badge"' in html
        assert 'id="v5-rosetta-py-badge"' in html
        assert 'id="v5-rosetta-rust-badge"' in html
        assert 'id="v5-lean4-code"' in html
        assert 'id="v5-python-code"' in html
        assert 'id="v5-rust-code"' in html
        assert 'id="v5-kpi-parent"' in html
        assert 'id="v5-kpi-child"' in html
        assert 'id="v5-kpi-delta"' in html
        assert 'id="v5-kpi-speedup"' in html
        assert 'id="v5-proof-token"' in html
        assert 'id="v5-copy-token-btn"' in html
        assert 'runV5RosettaVerify' in html
        assert 'copyV5Token' in html

    def test_v5_deck3_grpo_dom(self, html: str):
        assert 'id="v5-grpo-run-btn"' in html
        assert 'id="v5-grpo-grid"' in html
        assert 'runV5GRPOExplore' in html

    def test_scenario_studio_v5_button(self, html: str):
        assert 'id="studio-phase-v5-btn"' in html
        assert "setStudioCustomPhase('v5')" in html

    def test_v5_js_controllers_and_exports(self, html: str):
        # Window exports
        assert 'window.setV5LayaPreset = setV5LayaPreset;' in html
        assert 'window.onV5LayaTypeChange = onV5LayaTypeChange;' in html
        assert 'window.runV5LayaTriage = runV5LayaTriage;' in html
        assert 'window.loadV5Curricula = loadV5Curricula;' in html
        assert 'window.onV5CurriculumSelect = onV5CurriculumSelect;' in html
        assert 'window.runV5RosettaVerify = runV5RosettaVerify;' in html
        assert 'window.copyV5Token = copyV5Token;' in html
        assert 'window.runV5GRPOExplore = runV5GRPOExplore;' in html

    def test_v5_tab_hook_and_hash(self, html: str):
        assert "tabId === 'anse-v5'" in html
        assert "hash === '#anse-v5'" in html or "'#anse-v5'" in html
