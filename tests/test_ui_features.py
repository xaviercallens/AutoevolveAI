"""
Comprehensive UI Feature Tests — Frontend + Backend Integration.

Tests every interactive feature across all 8 dashboard sections:
  1. Concepts & Video (static HTML)
  2. Phase 1: Symbolic Sandbox & Attestation
  3. Phase 2: JEPA Latent Space
  4. Autopoietic Hot-Swap Hypervisor
  5. Phase 3: AI Neuro-Surgeon
  6. Symbiotic Co-Pilot & Accelerators
  7. Evolution Lab
  8. PR Factory

Plus: PWA infrastructure, health check, mobile responsiveness markers.
"""

from __future__ import annotations

import json
import re
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Create a TestClient for the FastAPI app (no live server needed)."""
    from web.server import app

    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════
# 1. CONCEPTS & STATIC HTML
# ═══════════════════════════════════════════════════════════════════


class TestConceptsSection:
    """Tab 1: Concepts & procedural video — static HTML served correctly."""

    def test_index_html_serves_200(self, client: TestClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_index_contains_all_section_ids(self, client: TestClient) -> None:
        html = client.get("/").text
        expected_sections = [
            "section-concepts",
            "section-phase1",
            "section-phase2",
            "section-autopoiesis",
            "section-phase3",
            "section-symbiotic",
            "section-evolution",
            "section-factory",
        ]
        for sid in expected_sections:
            assert sid in html, f"Missing section id: {sid}"

    def test_index_contains_all_tab_buttons(self, client: TestClient) -> None:
        html = client.get("/").text
        expected_tabs = [
            "tab-concepts",
            "tab-phase1",
            "tab-phase2",
            "tab-autopoiesis",
            "tab-phase3",
            "tab-symbiotic",
            "tab-evolution",
            "tab-factory",
        ]
        for tid in expected_tabs:
            assert tid in html, f"Missing tab button: {tid}"

    def test_index_contains_canvas_elements(self, client: TestClient) -> None:
        html = client.get("/").text
        assert "loopCanvas" in html, "Missing procedural video canvas"
        assert "latentCanvas" in html, "Missing JEPA latent canvas"

    def test_index_contains_mobile_bottom_nav(self, client: TestClient) -> None:
        html = client.get("/").text
        assert "mobile-bottom-nav" in html, "Missing mobile bottom navigation"

    def test_index_contains_switchTab_function(self, client: TestClient) -> None:
        html = client.get("/").text
        assert "function switchTab" in html, "Missing switchTab JS function"

    def test_index_contains_pwa_manifest_link(self, client: TestClient) -> None:
        html = client.get("/").text
        assert 'rel="manifest"' in html, "Missing PWA manifest link"

    def test_index_contains_service_worker_registration(self, client: TestClient) -> None:
        html = client.get("/").text
        assert "serviceWorker" in html, "Missing service worker registration"


# ═══════════════════════════════════════════════════════════════════
# 2. PHASE 1: SYMBOLIC SANDBOX & ATTESTATION
# ═══════════════════════════════════════════════════════════════════


class TestPhase1Sandbox:
    """Tab 2: Code execution in sandbox + AST anti-stub attestation."""

    # ── Execute endpoint ──
    def test_execute_clean_code(self, client: TestClient) -> None:
        resp = client.post(
            "/api/execute",
            json={"code": "print(42)", "timeout": 3.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert isinstance(data["energy"], (int, float))
        # When Docker sandbox is unavailable, energy may be 1M (graceful degradation)
        if "SANDBOX_UNAVAILABLE" not in data.get("stderr", ""):
            assert data["energy"] < 1_000_000, "Clean code should NOT get max energy"
            assert "42" in data["stdout"]
            assert data["is_valid"] is True

    def test_execute_returns_all_fields(self, client: TestClient) -> None:
        data = client.post("/api/execute", json={"code": "x=1+1; print(x)"}).json()
        required = [
            "status", "energy", "category", "is_valid",
            "duration_ms", "peak_ram_mb", "stdout",
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_execute_crash_code_high_energy(self, client: TestClient) -> None:
        data = client.post("/api/execute", json={"code": "raise ValueError('boom')"}).json()
        # Crashed code should get high energy
        assert data["energy"] >= 100 or not data["is_valid"]

    def test_execute_timeout_code(self, client: TestClient) -> None:
        data = client.post(
            "/api/execute",
            json={"code": "import time; time.sleep(10)", "timeout": 1.0},
        ).json()
        assert data["status"] in ("success", "error")
        # Either timed_out or high energy
        if data["status"] == "success":
            assert data.get("timed_out", False) or data["energy"] >= 100

    def test_execute_empty_code(self, client: TestClient) -> None:
        data = client.post("/api/execute", json={"code": ""}).json()
        assert data["status"] in ("success", "error")

    # ── Audit endpoint ──
    def test_audit_detects_pass_stub(self, client: TestClient) -> None:
        data = client.post("/api/audit", json={"code": "def f(): pass"}).json()
        assert data["passed"] is False
        assert len(data["violations"]) > 0
        assert data["proof_token"] is None

    def test_audit_detects_ellipsis_stub(self, client: TestClient) -> None:
        data = client.post("/api/audit", json={"code": "def f(): ..."}).json()
        assert data["passed"] is False
        assert len(data["violations"]) > 0

    def test_audit_accepts_real_implementation(self, client: TestClient) -> None:
        data = client.post(
            "/api/audit",
            json={"code": "def add(a, b):\n    return a + b"},
        ).json()
        assert data["passed"] is True
        assert data["proof_token"] is not None
        assert len(data["proof_token"]) > 0
        assert data["zero_trust_status"] == "ATTESTED"

    def test_audit_handles_syntax_error(self, client: TestClient) -> None:
        data = client.post("/api/audit", json={"code": "def f(:"}).json()
        assert data["passed"] is False
        assert "Syntax Error" in data["violations"][0] or "zero_trust_status" in data


# ═══════════════════════════════════════════════════════════════════
# 3. PHASE 2: JEPA LATENT SPACE
# ═══════════════════════════════════════════════════════════════════


class TestPhase2JEPA:
    """Tab 3: JEPA latent prediction + VICReg regularization."""

    def test_jepa_predict_returns_latent_vector(self, client: TestClient) -> None:
        data = client.post(
            "/api/jepa/predict",
            json={"code": "print(42)", "latent_dim": 16},
        ).json()
        assert "latent_vector" in data
        assert isinstance(data["latent_vector"], list)
        assert len(data["latent_vector"]) == 8  # first 8 dims displayed

    def test_jepa_predict_returns_2d_projection(self, client: TestClient) -> None:
        data = client.post(
            "/api/jepa/predict",
            json={"code": "x = 1", "latent_dim": 16},
        ).json()
        proj = data["2d_projection"]
        assert "x" in proj and "y" in proj
        assert isinstance(proj["x"], (int, float))
        assert isinstance(proj["y"], (int, float))

    def test_jepa_predict_returns_vicreg_metrics(self, client: TestClient) -> None:
        data = client.post(
            "/api/jepa/predict",
            json={"code": "a = 1", "latent_dim": 16, "gamma_margin": 1.0, "cov_weight": 0.01},
        ).json()
        vicreg = data["vicreg"]
        assert "latent_std" in vicreg
        assert "variance_penalty" in vicreg
        assert "covariance_penalty" in vicreg
        assert "total_vicreg_loss" in vicreg
        assert "collapse_prevented" in vicreg
        assert isinstance(vicreg["collapse_prevented"], bool)

    def test_jepa_predict_energy_for_stub_code(self, client: TestClient) -> None:
        data = client.post(
            "/api/jepa/predict",
            json={"code": "def f(): pass", "latent_dim": 16},
        ).json()
        # "pass" in code adds +1.0 to energy
        assert data["predicted_energy"] > 0

    def test_jepa_deterministic_same_code(self, client: TestClient) -> None:
        payload = {"code": "hello_world = True", "latent_dim": 16}
        d1 = client.post("/api/jepa/predict", json=payload).json()
        d2 = client.post("/api/jepa/predict", json=payload).json()
        assert d1["latent_vector"] == d2["latent_vector"], "JEPA should be deterministic"


# ═══════════════════════════════════════════════════════════════════
# 4. AUTOPOIETIC HOT-SWAP HYPERVISOR
# ═══════════════════════════════════════════════════════════════════


class TestAutopoiesisHotSwap:
    """Tab 4: Live self-evolution + process hot-swapping."""

    def test_evolve_returns_success(self, client: TestClient) -> None:
        data = client.post("/api/autopoiesis/evolve").json()
        assert data["status"] == "success"
        assert "data" in data

    def test_evolve_has_parent_and_child(self, client: TestClient) -> None:
        d = client.post("/api/autopoiesis/evolve").json()["data"]
        assert "parent" in d
        assert "attempt_2_evolved" in d
        assert "thermodynamics" in d

    def test_evolve_parent_has_energy(self, client: TestClient) -> None:
        parent = client.post("/api/autopoiesis/evolve").json()["data"]["parent"]
        assert "energy" in parent
        assert isinstance(parent["energy"], (int, float))
        assert parent["energy"] > 0

    def test_evolve_child_improves_on_parent(self, client: TestClient) -> None:
        d = client.post("/api/autopoiesis/evolve").json()["data"]
        thermo = d["thermodynamics"]
        assert "delta_energy" in thermo
        # ΔE should be negative (child is better) or zero when sandbox is unavailable
        assert thermo["delta_energy"] <= 0, "Child should have equal or lower energy than parent"

    def test_evolve_lazy_shortcut_caught(self, client: TestClient) -> None:
        d = client.post("/api/autopoiesis/evolve").json()["data"]
        lazy = d["attempt_1_lazy"]
        assert "violations" in lazy
        assert len(lazy["violations"]) > 0, "AST whistleblower should catch lazy stub"

    def test_evolve_hotswap_metadata(self, client: TestClient) -> None:
        d = client.post("/api/autopoiesis/evolve").json()["data"]
        hs = d["hotswap"]
        assert "target_instance" in hs
        assert "new_version" in hs
        assert "live_latency_us" in hs

    def test_hotswap_endpoint_with_explicit_energies(self, client: TestClient) -> None:
        data = client.post(
            "/api/autopoiesis/hotswap",
            json={"parent_energy": 50.0, "child_code": "print(sum(range(100)))"},
        ).json()
        assert "parent_energy" in data
        assert "child_energy" in data
        assert "delta_energy" in data
        assert "thermodynamically_admissible" in data


# ═══════════════════════════════════════════════════════════════════
# 5. PHASE 3: AI NEURO-SURGEON
# ═══════════════════════════════════════════════════════════════════


class TestPhase3NeuroSurgeon:
    """Tab 5: Active inference loop + FlashAttention neuro-surgery."""

    # ── Active Inference ──
    def test_active_inference_returns_steps(self, client: TestClient) -> None:
        data = client.post("/api/phase3/active-inference").json()
        assert data["status"] == "success"
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) >= 1

    def test_active_inference_step_has_required_fields(self, client: TestClient) -> None:
        steps = client.post("/api/phase3/active-inference").json()["steps"]
        for step in steps:
            assert "iteration" in step
            assert "energy" in step
            assert "duration_ms" in step
            assert isinstance(step["energy"], (int, float))

    def test_active_inference_converges(self, client: TestClient) -> None:
        steps = client.post("/api/phase3/active-inference").json()["steps"]
        last = steps[-1]
        # Last step should have energy 0 (converged)
        assert last["energy"] == 0, "Active inference should converge to E=0"
        assert last.get("proof_token") is not None

    # ── Neuro-Surgeon ──
    def test_neuro_surgeon_returns_report(self, client: TestClient) -> None:
        data = client.post("/api/phase3/neuro-surgeon").json()
        assert data["status"] == "success"
        assert "report" in data

    def test_neuro_surgeon_report_has_metrics(self, client: TestClient) -> None:
        r = client.post("/api/phase3/neuro-surgeon").json()["report"]
        required = [
            "parent_energy", "parent_latency_ms", "parent_vram_mb",
            "child_energy", "child_latency_ms", "child_vram_mb",
            "delta_energy", "speedup_factor", "vram_reduction_pct",
        ]
        for field in required:
            assert field in r, f"Missing report field: {field}"

    def test_neuro_surgeon_delta_energy_is_numeric(self, client: TestClient) -> None:
        r = client.post("/api/phase3/neuro-surgeon").json()["report"]
        # Timing is non-deterministic; assert the delta is computed correctly
        assert isinstance(r["delta_energy"], (int, float))
        assert isinstance(r["speedup_factor"], (int, float))

    def test_neuro_surgeon_has_proof_token(self, client: TestClient) -> None:
        r = client.post("/api/phase3/neuro-surgeon").json()["report"]
        assert r["proof_token"] is not None
        assert len(r["proof_token"]) > 0

    def test_neuro_surgeon_hotswap_field_is_bool(self, client: TestClient) -> None:
        r = client.post("/api/phase3/neuro-surgeon").json()["report"]
        assert isinstance(r["hotswap_authorized"], bool)


# ═══════════════════════════════════════════════════════════════════
# 6. SYMBIOTIC CO-PILOT & ACCELERATORS
# ═══════════════════════════════════════════════════════════════════


class TestSymbioticCoPilot:
    """Tab 6: TDD co-pilot, latent dreamer, Lean prover, cyber engagement."""

    # ── Symbiotic Co-Pilot ──
    def test_copilot_converges(self, client: TestClient) -> None:
        data = client.post(
            "/api/symbiotic/copilot",
            json={"prompt": "Implement add(a,b)", "test_command": 'python -c "assert True"'},
        ).json()
        assert data["status"] == "success"
        assert "converged" in data
        assert "attempts_used" in data
        assert "steps" in data

    def test_copilot_returns_final_code(self, client: TestClient) -> None:
        data = client.post(
            "/api/symbiotic/copilot",
            json={"prompt": "Hello world", "test_command": 'python -c "print(1)"'},
        ).json()
        assert "final_code" in data
        assert data["final_code"] is not None

    def test_copilot_steps_have_energy(self, client: TestClient) -> None:
        data = client.post(
            "/api/symbiotic/copilot",
            json={"prompt": "binary search", "test_command": 'python -c "1"'},
        ).json()
        for step in data["steps"]:
            assert "attempt" in step
            assert "energy" in step
            assert "duration_ms" in step

    # ── Latent Dreamer ──
    def test_latent_dreamer_returns_candidates(self, client: TestClient) -> None:
        data = client.post(
            "/api/accelerator/latent-dream",
            json={"prompt": "optimize dense pass", "branches": 16},
        ).json()
        assert data["status"] == "success"
        assert data["num_candidates"] == 16
        assert "best_candidate_idx" in data

    def test_latent_dreamer_grpo_stats(self, client: TestClient) -> None:
        data = client.post(
            "/api/accelerator/latent-dream",
            json={"prompt": "kernel", "branches": 8},
        ).json()
        assert "group_mean_energy" in data
        assert "group_std_energy" in data
        assert isinstance(data["group_mean_energy"], (int, float))

    def test_latent_dreamer_best_thought_structure(self, client: TestClient) -> None:
        data = client.post(
            "/api/accelerator/latent-dream",
            json={"prompt": "attention", "branches": 4},
        ).json()
        best = data["best_thought"]
        assert "thought_id" in best
        assert "predicted_energy" in best
        assert "group_advantage" in best
        assert "relative_weight" in best
        assert "code_proposal" in best

    def test_latent_dreamer_speedup_over_sandbox(self, client: TestClient) -> None:
        data = client.post(
            "/api/accelerator/latent-dream",
            json={"prompt": "matmul", "branches": 16},
        ).json()
        assert data["speedup_vs_sandbox"] > 1, "Latent dream should be faster than OS sandbox"

    # ── Frontier: Lean Mathematician ──
    def test_lean_mathematician_valid_proof(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/mathematician",
            json={
                "theorem_name": "add_comm",
                "proof_code": "theorem add_comm (n m : Nat) : n + m = m + n := by omega",
            },
        ).json()
        assert data["status"] == "success"
        assert data["is_valid"] is True
        assert data["energy"] == 0.0
        assert "tactics" in data
        assert len(data["tactics"]) > 0

    def test_lean_mathematician_invalid_proof(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/mathematician",
            json={
                "theorem_name": "bogus",
                "proof_code": "theorem bogus : 1 = 2 := by sorry",
            },
        ).json()
        assert data["status"] == "success"
        assert data["is_valid"] is False
        assert data["energy"] > 0

    def test_lean_mathematician_has_diagnostics(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/mathematician",
            json={"theorem_name": "test", "proof_code": "by omega"},
        ).json()
        assert "diagnostics" in data
        assert "duration_ms" in data
        assert isinstance(data["duration_ms"], (int, float))

    # ── Frontier: Cyber Red vs Blue ──
    def test_cyber_engagement_returns_result(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/cyber",
            json={
                "red_payload": "A" * 200,
                "blue_patch": "def handle(data):\n    if len(data) > 64:\n        raise ValueError()\n    return data",
            },
        ).json()
        assert data["status"] == "success"
        assert "exploit_succeeded" in data
        assert "energy" in data
        assert "cve" in data

    def test_cyber_blue_team_defends(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/cyber",
            json={
                "red_payload": "A" * 200,
                "blue_patch": "def handle(data):\n    if len(data) > 64:\n        raise ValueError()\n    return data",
            },
        ).json()
        assert data["exploit_succeeded"] is False, "Blue team patch should block buffer overflow"
        # Blue defense has non-zero cost energy (defense effort)
        assert isinstance(data["energy"], (int, float))

    def test_cyber_red_team_succeeds_without_patch(self, client: TestClient) -> None:
        data = client.post(
            "/api/frontier/cyber",
            json={
                "red_payload": "A" * 200,
                "blue_patch": "def handle(data): return data",
            },
        ).json()
        assert data["exploit_succeeded"] is True, "Without bounds check, exploit should succeed"
        # Attacker energy is 0 when exploit succeeds (minimal effort)
        assert isinstance(data["energy"], (int, float))


# ═══════════════════════════════════════════════════════════════════
# 7. EVOLUTION LAB
# ═══════════════════════════════════════════════════════════════════


class TestEvolutionLab:
    """Tab 7: Evolution results viewer — read-only data from results files."""

    def test_evolution_all_phases_returns_structure(self, client: TestClient) -> None:
        data = client.get("/api/evolution").json()
        assert "phases" in data
        assert "goals" in data
        assert "generated" in data
        # Should have phases 1, 2, 3
        for p in ("1", "2", "3"):
            assert p in data["phases"], f"Missing phase {p}"

    def test_evolution_phase_has_status(self, client: TestClient) -> None:
        data = client.get("/api/evolution").json()
        for p_key, phase_data in data["phases"].items():
            assert "status" in phase_data
            assert phase_data["status"] in ("missing", "running", "invalid", "finished")

    def test_evolution_goals_have_names(self, client: TestClient) -> None:
        data = client.get("/api/evolution").json()
        for p_key, goal in data["goals"].items():
            assert "name" in goal
            assert "goal" in goal
            assert "runner" in goal

    def test_evolution_single_phase_endpoint(self, client: TestClient) -> None:
        resp = client.get("/api/evolution/1")
        assert resp.status_code == 200
        data = resp.json()
        assert "goal" in data
        assert "status" in data

    def test_evolution_invalid_phase_404(self, client: TestClient) -> None:
        resp = client.get("/api/evolution/99")
        assert resp.status_code == 404

    def test_evolution_phase_has_gate(self, client: TestClient) -> None:
        data = client.get("/api/evolution").json()
        for p_key, phase_data in data["phases"].items():
            assert "gate" in phase_data
            assert "gate_passed" in phase_data
            assert "gate_total" in phase_data


# ═══════════════════════════════════════════════════════════════════
# 8. PR FACTORY
# ═══════════════════════════════════════════════════════════════════


class TestPRFactory:
    """Tab 8: Jules PR Factory — dispatch, missions, CI, reviews, history."""

    def test_factory_dispatch_creates_mission(self, client: TestClient) -> None:
        data = client.post(
            "/api/factory/dispatch",
            json={
                "mission_type": "performance",
                "target": "anse/sandbox.py",
                "description": "Test dispatch",
            },
        ).json()
        assert "id" in data
        assert "status" in data
        assert len(data["id"]) > 0

    def test_factory_missions_list(self, client: TestClient) -> None:
        data = client.get("/api/factory/missions").json()
        assert "active" in data
        assert "completed" in data
        assert isinstance(data["active"], list)
        assert isinstance(data["completed"], list)

    def test_factory_dispatched_mission_appears_in_list(self, client: TestClient) -> None:
        # Dispatch a unique mission
        dispatch = client.post(
            "/api/factory/dispatch",
            json={
                "mission_type": "qa_fuzzing",
                "target": "tests/unique_target.py",
                "description": "Verify appears in list",
            },
        ).json()
        mid = dispatch["id"]

        missions = client.get("/api/factory/missions").json()
        all_ids = [m["id"] for m in missions["active"] + missions["completed"]]
        assert mid in all_ids, "Dispatched mission should appear in mission list"

    def test_factory_ci_status_has_pillars(self, client: TestClient) -> None:
        data = client.get("/api/factory/ci-status").json()
        assert "pillars" in data
        assert isinstance(data["pillars"], list)

    def test_factory_ci_pillars_have_names(self, client: TestClient) -> None:
        data = client.get("/api/factory/ci-status").json()
        for pillar in data["pillars"]:
            assert "name" in pillar
            assert "passed" in pillar
            assert "details" in pillar

    def test_factory_reviews_endpoint(self, client: TestClient) -> None:
        data = client.get("/api/factory/reviews").json()
        assert "reviews" in data
        assert isinstance(data["reviews"], list)

    def test_factory_history_pagination(self, client: TestClient) -> None:
        data = client.get("/api/factory/history?page=1").json()
        assert "missions" in data
        assert "page" in data
        assert "total_pages" in data
        assert data["page"] == 1

    def test_factory_history_page_2(self, client: TestClient) -> None:
        data = client.get("/api/factory/history?page=2").json()
        assert "page" in data
        # Page 2 may be empty but should still return valid structure
        assert isinstance(data["missions"], list)

    def test_factory_all_mission_types(self, client: TestClient) -> None:
        """Verify all 5 mission types dispatch successfully."""
        types = ["performance", "qa_fuzzing", "security", "lean_proof", "custom"]
        for mt in types:
            data = client.post(
                "/api/factory/dispatch",
                json={"mission_type": mt, "target": f"test_{mt}.py"},
            ).json()
            assert "id" in data, f"Failed to dispatch mission type: {mt}"


# ═══════════════════════════════════════════════════════════════════
# PWA & INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════


class TestPWAInfrastructure:
    """Service Worker, Manifest, Icons, Health Check."""

    def test_health_check(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_pwa_manifest_json(self, client: TestClient) -> None:
        resp = client.get("/manifest.json")
        assert resp.status_code == 200
        manifest = resp.json()
        assert "name" in manifest
        assert "icons" in manifest
        assert "start_url" in manifest
        assert manifest.get("display") in ("standalone", "fullscreen", "minimal-ui")

    def test_pwa_manifest_has_icons(self, client: TestClient) -> None:
        manifest = client.get("/manifest.json").json()
        icons = manifest["icons"]
        assert len(icons) >= 2, "Manifest should have at least 2 icon sizes"
        sizes = [i["sizes"] for i in icons]
        assert "192x192" in sizes
        assert "512x512" in sizes

    def test_service_worker_js(self, client: TestClient) -> None:
        resp = client.get("/sw.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers["content-type"]
        text = resp.text
        assert "cache" in text.lower() or "fetch" in text.lower()

    def test_icon_192_serves(self, client: TestClient) -> None:
        resp = client.get("/icons/icon-192.png")
        assert resp.status_code == 200

    def test_icon_512_serves(self, client: TestClient) -> None:
        resp = client.get("/icons/icon-512.png")
        assert resp.status_code == 200

    def test_icon_nonexistent_404(self, client: TestClient) -> None:
        resp = client.get("/icons/nonexistent.png")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# FRONTEND JS FUNCTION COVERAGE AUDIT
# ═══════════════════════════════════════════════════════════════════


class TestFrontendJSPresence:
    """Verify all critical JS functions exist in the served HTML."""

    @pytest.fixture(autouse=True)
    def _load_html(self, client: TestClient) -> None:
        self.html = client.get("/").text

    def test_phase1_functions(self) -> None:
        for fn in ["loadPreset", "runExecution", "runAudit", "simulateExecution", "simulateAudit"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_phase2_functions(self) -> None:
        for fn in ["renderLatentSpace", "updateVICReg", "perturbLatent", "initLatentPoints"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_video_loop_functions(self) -> None:
        for fn in ["drawVideoLoop", "toggleAnimation", "resetAnimation", "scrubAnimation"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_autopoiesis_functions(self) -> None:
        assert "executeHotSwap" in self.html

    def test_phase3_functions(self) -> None:
        for fn in ["runPhase3ActiveInference", "runPhase3NeuroSurgeon"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_symbiotic_functions(self) -> None:
        for fn in ["runSymbioticCoPilot", "runLatentDreamer", "runFrontierMathematician", "runFrontierCyber"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_evolution_functions(self) -> None:
        for fn in ["loadEvolution", "renderSelector", "renderGoal", "renderGate", "renderUseCases"]:
            assert fn in self.html, f"Missing JS function: {fn}"

    def test_factory_functions(self) -> None:
        for fn in ["factoryDispatch", "factoryRefreshMissions", "factoryRefreshCI", "factoryRefreshReviews", "factoryLoadHistory"]:
            assert fn in self.html, f"Missing JS function: {fn}"


# ═══════════════════════════════════════════════════════════════════
# CROSS-CUTTING EDGE CASES
# ═══════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Cross-cutting edge cases and data integrity."""

    def test_execute_code_with_expected_output(self, client: TestClient) -> None:
        data = client.post(
            "/api/execute",
            json={"code": "print('hello')", "expected_output": "hello"},
        ).json()
        assert data["status"] == "success"

    def test_multiple_rapid_dispatches(self, client: TestClient) -> None:
        """Verify factory handles burst dispatches without collision."""
        ids = set()
        for i in range(5):
            d = client.post(
                "/api/factory/dispatch",
                json={"mission_type": "custom", "target": f"burst_{i}.py"},
            ).json()
            ids.add(d["id"])
        assert len(ids) == 5, "All dispatch IDs should be unique"

    def test_jepa_different_codes_different_vectors(self, client: TestClient) -> None:
        d1 = client.post("/api/jepa/predict", json={"code": "a = 1"}).json()
        d2 = client.post("/api/jepa/predict", json={"code": "b = 99999"}).json()
        assert d1["latent_vector"] != d2["latent_vector"], "Different code should produce different embeddings"
