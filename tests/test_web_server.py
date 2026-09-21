"""Use-case validation for the interactive web API (Phases 1-3), driven through FastAPI's TestClient."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import web.server as srv

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(srv.app)


def _boom(*a, **kw):
    raise RuntimeError("kaboom")


# ─── Static index ────────────────────────────────────────────────────────────


def test_index_served_and_missing(monkeypatch, tmp_path) -> None:
    resp = client.get("/")
    assert resp.status_code == 200 and "html" in resp.headers["content-type"]
    monkeypatch.setattr(srv, "STATIC_DIR", tmp_path)
    assert client.get("/").status_code == 404


# ─── Phase 1: sandbox physics + audit ────────────────────────────────────────


def test_execute_success_reports_energy_and_tier() -> None:
    body = client.post("/api/execute", json={"code": "print(sum(range(10)))"}).json()
    assert body["status"] == "success" and body["returncode"] == 0
    assert body["stdout"].strip() == "45" and body["tier_used"] == 1
    assert body["timed_out"] is False and body["energy"] >= 0


def test_execute_wrong_output_and_crash_raise_energy() -> None:
    good = client.post("/api/execute", json={"code": "print(1)", "expected_output": "1"}).json()
    bad = client.post("/api/execute", json={"code": "print(1)", "expected_output": "2"}).json()
    crash = client.post("/api/execute", json={"code": "1/0"}).json()
    assert bad["energy"] > good["energy"] and crash["energy"] > good["energy"]
    assert crash["is_valid"] is False


def test_execute_internal_error_is_max_pain(monkeypatch) -> None:
    monkeypatch.setattr(srv.executor, "execute", _boom)
    body = client.post("/api/execute", json={"code": "print(1)"}).json()
    assert body == {
        "status": "error", "energy": 1_000_000.0, "category": "crash",
        "is_valid": False, "error": "kaboom",
    }


def test_audit_attests_clean_code_and_rejects_stubs_and_syntax() -> None:
    clean = client.post("/api/audit", json={"code": "def f(x):\n    return x + 1\n"}).json()
    assert clean["passed"] and clean["zero_trust_status"] == "ATTESTED" and clean["proof_token"]
    stub = client.post("/api/audit", json={"code": "def f(x):\n    pass\n"}).json()
    assert not stub["passed"] and stub["proof_token"] is None and stub["violations"]
    assert stub["zero_trust_status"] == "REJECTED"
    bad = client.post("/api/audit", json={"code": "def f(:"}).json()
    assert bad["zero_trust_status"] == "SYNTAX_ERROR" and "Syntax Error line" in bad["violations"][0]


# ─── Phase 2: JEPA latent view ───────────────────────────────────────────────


def test_jepa_predict_is_deterministic_and_reports_vicreg() -> None:
    a = client.post("/api/jepa/predict", json={"code": "x = 1"}).json()
    b = client.post("/api/jepa/predict", json={"code": "x = 1"}).json()
    assert a == b and len(a["latent_vector"]) == 8
    assert set(a["vicreg"]) >= {"latent_std", "variance_penalty", "collapse_prevented"}
    with_pass = client.post("/api/jepa/predict", json={"code": "pass"}).json()
    assert with_pass["predicted_energy"] >= 0


@pytest.mark.parametrize("dim", [0, 3, 33, 1000])
def test_jepa_predict_rejects_out_of_range_latent_dim(dim: int) -> None:
    """Regression: previously latent_dim<4 raised IndexError and >32 raised ValueError (HTTP 500)."""
    assert client.post("/api/jepa/predict", json={"code": "x", "latent_dim": dim}).status_code == 422


@pytest.mark.parametrize("dim", [4, 32])
def test_jepa_predict_accepts_boundary_latent_dims(dim: int) -> None:
    assert client.post("/api/jepa/predict", json={"code": "x", "latent_dim": dim}).status_code == 200


# ─── Use case 3: autopoietic hot-swap gate ───────────────────────────────────


def test_hotswap_admissible_only_when_child_has_lower_energy_and_is_valid() -> None:
    fast = client.post(
        "/api/autopoiesis/hotswap", json={"parent_energy": 10_000.0, "child_code": "print(1)"}
    ).json()
    assert fast["thermodynamically_admissible"] and fast["action"] == "HOT_SWAP_EXECUTED"
    assert fast["delta_energy"] < 0 and fast["improvement_pct"] > 0
    slow_parent = client.post(
        "/api/autopoiesis/hotswap", json={"parent_energy": 0.0, "child_code": "print(1)"}
    ).json()
    assert slow_parent["action"] == "REJECTED_HIGH_ENERGY" and slow_parent["improvement_pct"] == 0.0
    broken = client.post(
        "/api/autopoiesis/hotswap", json={"parent_energy": 10_000.0, "child_code": "1/0"}
    ).json()
    assert broken["child_valid"] is False and broken["action"] == "REJECTED_HIGH_ENERGY"


def test_evolve_endpoint_success_and_error(monkeypatch) -> None:
    monkeypatch.setattr(srv, "run_self_evolution_demo", lambda: {"hot_swapped": True})
    assert client.post("/api/autopoiesis/evolve").json() == {
        "status": "success", "data": {"hot_swapped": True},
    }
    monkeypatch.setattr(srv, "run_self_evolution_demo", _boom)
    assert client.post("/api/autopoiesis/evolve").json() == {"status": "error", "error": "kaboom"}


# ─── Phase 3: Micro-ML active inference + Neuro-Surgeon ──────────────────────


def test_active_inference_endpoint_converges_from_100_to_0() -> None:
    body = client.post("/api/phase3/active-inference").json()
    assert body["status"] == "success"
    first, second = body["steps"]
    assert first["energy"] == 100.0 and first["is_valid"] is False and first["feedback_prompt"]
    assert second["energy"] == 0.0 and second["is_valid"] and second["proof_token"]


def test_active_inference_endpoint_error(monkeypatch) -> None:
    monkeypatch.setattr(srv, "ActiveInferenceLoop", _boom)
    assert client.post("/api/phase3/active-inference").json()["status"] == "error"


def test_neuro_surgeon_endpoint_report_is_consistent() -> None:
    body = client.post("/api/phase3/neuro-surgeon").json()
    assert body["status"] == "success"
    rep = body["report"]
    assert rep["hotswap_authorized"] == (rep["delta_energy"] < 0)
    assert rep["lean4_theorem"] == "ANSE.Autopoiesis.autopoiesis_exists"


def test_neuro_surgeon_endpoint_error(monkeypatch) -> None:
    monkeypatch.setattr(srv, "AutopoieticNeuroSurgeon", _boom)
    assert client.post("/api/phase3/neuro-surgeon").json()["status"] == "error"


# ─── Symbiotic co-pilot ──────────────────────────────────────────────────────


def _copilot_summary(converged: bool = True) -> SimpleNamespace:
    step = SimpleNamespace(attempt=1, energy=0.0, is_valid=True, feedback="f" * 300, duration_ms=1.234)
    return SimpleNamespace(
        converged=converged, attempts_used=1, final_code="x = 1", proof_token="tok",
        dpo_pair_recorded=False, steps=[step],
    )


def test_copilot_endpoint_success_truncates_feedback_and_cleans_temp(monkeypatch) -> None:
    seen: dict = {}

    def _fake(prompt, target_file, test_command, max_attempts):
        seen["target"] = target_file
        return _copilot_summary()

    monkeypatch.setattr(srv, "active_inference_copilot", _fake)
    body = client.post("/api/symbiotic/copilot", json={}).json()
    assert body["status"] == "success" and body["converged"] is True
    assert len(body["steps"][0]["feedback"]) == 200
    assert not Path(seen["target"]).exists()


def test_copilot_endpoint_tolerates_cleanup_failure_and_reports_errors(monkeypatch) -> None:
    monkeypatch.setattr(srv, "active_inference_copilot", lambda **kw: _copilot_summary())

    def _no_remove(path):
        raise OSError("busy")

    monkeypatch.setattr(srv.os, "remove", _no_remove)
    assert client.post("/api/symbiotic/copilot", json={}).json()["status"] == "success"
    monkeypatch.setattr(srv, "active_inference_copilot", _boom)
    assert client.post("/api/symbiotic/copilot", json={}).json()["status"] == "error"


def test_copilot_endpoint_real_loop_with_passing_harness() -> None:
    cmd = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
    body = client.post("/api/symbiotic/copilot", json={"test_command": cmd}).json()
    assert body["status"] == "success" and body["converged"] is True and body["proof_token"]


# ─── 10,000x accelerator + frontier domains ──────────────────────────────────


def test_latent_dream_endpoint_scores_all_branches() -> None:
    body = client.post("/api/accelerator/latent-dream", json={"branches": 8}).json()
    assert body["status"] == "success" and body["num_candidates"] == 8
    assert 0 <= body["best_candidate_idx"] < 8
    assert body["best_thought"]["code_proposal"]


def test_latent_dream_endpoint_error(monkeypatch) -> None:
    monkeypatch.setattr(srv, "LatentDreamer", _boom)
    assert client.post("/api/accelerator/latent-dream", json={}).json()["status"] == "error"


def test_mathematician_endpoint_accepts_proof_and_rejects_sorry(monkeypatch) -> None:
    ok = client.post("/api/frontier/mathematician", json={}).json()
    assert ok["status"] == "success" and ok["is_valid"] and ok["energy"] == 0.0
    assert "omega" in ok["tactics"]
    gap = client.post(
        "/api/frontier/mathematician", json={"proof_code": "theorem t : True := by sorry"}
    ).json()
    assert gap["is_valid"] is False and gap["energy"] == 1000.0
    monkeypatch.setattr(srv, "AutonomousMathematician", _boom)
    assert client.post("/api/frontier/mathematician", json={}).json()["status"] == "error"


def test_cyber_endpoint_defense_and_breach_and_error(monkeypatch) -> None:
    secure = client.post("/api/frontier/cyber", json={}).json()
    assert secure["status"] == "success" and secure["exploit_succeeded"] is False
    breach = client.post(
        "/api/frontier/cyber", json={"red_payload": "select 1", "blue_patch": "pass"}
    ).json()
    assert breach["exploit_succeeded"] is True and breach["cve"] == "CWE-89: SQL Injection"
    monkeypatch.setattr(srv, "CyberImmuneSwarm", _boom)
    assert client.post("/api/frontier/cyber", json={}).json()["status"] == "error"


# ─── Entrypoint ──────────────────────────────────────────────────────────────


def test_main_launches_uvicorn_with_env_overrides(monkeypatch, capsys) -> None:
    calls: list = []
    monkeypatch.setattr(srv.uvicorn, "run", lambda *a, **kw: calls.append((a, kw)))
    monkeypatch.setenv("PORT", "5055")
    monkeypatch.setenv("HOST", "0.0.0.0")
    srv.main()
    assert calls == [(("web.server:app",), {"host": "0.0.0.0", "port": 5055, "reload": False})]
    assert "5055" in capsys.readouterr().out


def test_dunder_main_guard(monkeypatch) -> None:
    import uvicorn

    calls: list = []
    monkeypatch.setattr(uvicorn, "run", lambda *a, **kw: calls.append(a))
    # Executing as a script from elsewhere: project root is not importable yet -> bootstrap adds it.
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p not in (str(ROOT), "")])
    runpy.run_path(str(ROOT / "web" / "server.py"), run_name="__main__")
    assert calls == [("web.server:app",)]
    assert str(ROOT) in sys.path
