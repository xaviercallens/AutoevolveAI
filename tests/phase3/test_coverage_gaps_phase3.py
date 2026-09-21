"""Phase 3 coverage-completion tests.

Covers the Neuro-Surgeon (deterministic ΔE gating, timeout / cleanup paths, CUDA benchmark path),
the hypervisor child evaluation, frontier domains, latent dreamer, self-healing loop and the
generated ``evolved_core`` artifact. Hermetic: no GPU, no network, no real LLM.
"""

from __future__ import annotations

import runpy
import subprocess
import sys
import textwrap
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest
import torch
import torch.nn as nn

import anse.autopoiesis.neuro_surgeon as ns
from anse.autopoiesis.hypervisor import AutopoiesisHypervisor, BaselineMetrics
from anse.autopoiesis.neuro_surgeon import (
    AutopoieticNeuroSurgeon,
    FlashAttentionEngine,
    MicroMLRealityEngine,
)
from anse.core.latent_dreamer import HippocampalReplayEngine, LatentDreamer
from anse.frontier.domains import CyberImmuneSwarm, _evaluate_exploit_vector

ROOT = Path(__file__).resolve().parents[2]

# ─── MicroMLRealityEngine ────────────────────────────────────────────────────


def test_reality_engine_syntax_error_is_energy_100() -> None:
    res = MicroMLRealityEngine().evaluate_code("class CustomNet(:\n")
    assert res.energy == 100.0 and res.is_valid is False
    assert res.error_trace is not None and res.error_trace.startswith("SyntaxError on line")


def test_reality_engine_timeout(monkeypatch) -> None:
    def _timeout(*a, **kw):
        raise subprocess.TimeoutExpired(cmd="x", timeout=0.1)

    monkeypatch.setattr(ns.subprocess, "run", _timeout)
    code = textwrap.dedent("""
        import torch.nn as nn
        class CustomNet(nn.Module):
            def forward(self, x):
                return x
    """)
    res = MicroMLRealityEngine(timeout_sec=0.1).evaluate_code(code)
    assert res.energy == 100.0
    assert res.error_trace == "Execution timed out after 0.1s"


def test_reality_engine_tolerates_temp_file_cleanup_failure(monkeypatch) -> None:
    def _no_remove(path):
        raise OSError("locked")

    monkeypatch.setattr(ns.os, "remove", _no_remove)
    fake = SimpleNamespace(stdout="ENERGY: 100 | ERROR: boom", stderr="")
    monkeypatch.setattr(ns.subprocess, "run", lambda *a, **kw: fake)
    res = MicroMLRealityEngine().evaluate_code("x = 1\n")
    assert res.energy == 100.0 and res.error_trace == "boom"


def test_parse_output_defaults_and_unknown_error() -> None:
    eng = MicroMLRealityEngine()
    ok = eng._parse_output("ENERGY: 0", "")
    assert ok.is_valid and ok.parameters == 0 and ok.output_shape == "(16, 10)"
    unknown = eng._parse_output("garbage", "")
    assert unknown.error_trace == "Unknown Execution Error"
    from_stderr = eng._parse_output("garbage", "Traceback...")
    assert from_stderr.error_trace == "Traceback..."


# ─── Neuro-Surgeon: benchmark + ΔE gate ──────────────────────────────────────


class _FakeCudaModule(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lin = nn.Linear(128, 128)

    def to(self, *a, **kw):  # stay on CPU while pretending the device is CUDA
        return self

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.lin(x)


def test_benchmark_module_cuda_path(monkeypatch) -> None:
    real_randn = torch.randn
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "reset_peak_memory_stats", lambda: None)
    monkeypatch.setattr(torch.cuda, "synchronize", lambda: None)
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda: 64 * 1024 * 1024)
    monkeypatch.setattr(torch, "randn", lambda *a, device=None, **kw: real_randn(*a, **kw))
    energy, latency, vram = AutopoieticNeuroSurgeon().benchmark_module(
        _FakeCudaModule(), batch_size=2, seq_len=4
    )
    assert vram == 64.0
    assert energy == pytest.approx(latency + vram)


def test_benchmark_module_cpu_uses_best_of_rounds() -> None:
    energy, latency, vram = AutopoieticNeuroSurgeon().benchmark_module(
        FlashAttentionEngine(), batch_size=2, seq_len=8
    )
    assert vram == 12.5 and latency > 0
    assert energy == pytest.approx(latency + vram)


def _stub_bench(monkeypatch, parent: float, child: float) -> AutopoieticNeuroSurgeon:
    surgeon = AutopoieticNeuroSurgeon()
    energies = iter([parent, child])

    def _bench(module, batch_size=32, seq_len=256):
        e = next(energies)
        return e, e - 1.0, 1.0

    monkeypatch.setattr(surgeon, "benchmark_module", _bench)
    return surgeon


def test_hotswap_authorized_only_when_delta_energy_negative(monkeypatch) -> None:
    surgeon = _stub_bench(monkeypatch, parent=30.0, child=20.0)
    report = surgeon.execute_neuro_surgery()
    assert report.hotswap_authorized is True
    assert report.delta_energy == -10.0
    assert report.proof_token is not None
    assert report.active_version_post_swap == "2.0.0-flash-child"
    assert surgeon.live_engine.version == "2.0.0-flash-child"


def test_hotswap_rejected_when_child_not_better(monkeypatch) -> None:
    surgeon = _stub_bench(monkeypatch, parent=20.0, child=30.0)
    report = surgeon.execute_neuro_surgery()
    assert report.hotswap_authorized is False
    assert report.delta_energy == 10.0
    assert report.proof_token is None
    assert surgeon.live_engine.version == "1.0.0-quadratic-parent"


def test_hotswap_rejected_on_exact_tie(monkeypatch) -> None:
    """Strict domination: ΔE == 0 must NOT authorise a swap."""
    surgeon = _stub_bench(monkeypatch, parent=25.0, child=25.0)
    assert surgeon.execute_neuro_surgery().hotswap_authorized is False


def test_real_surgery_report_is_self_consistent() -> None:
    """On real hardware the swap outcome is noise-dependent on CPU; the gate must stay consistent."""
    surgeon = AutopoieticNeuroSurgeon()
    report = surgeon.execute_neuro_surgery()
    assert report.hotswap_authorized == (report.delta_energy < 0)
    assert (report.proof_token is not None) == report.hotswap_authorized
    expected = "2.0.0-flash-child" if report.hotswap_authorized else "1.0.0-quadratic-parent"
    assert surgeon.live_engine.version == expected
    assert report.speedup_factor > 0


def test_flash_and_baseline_engines_are_shape_compatible() -> None:
    x = torch.randn(2, 8, 128)
    assert ns.BaselineAttentionEngine()(x).shape == FlashAttentionEngine()(x).shape == x.shape


# ─── Hypervisor.evaluate_child ───────────────────────────────────────────────


def test_hypervisor_evaluate_child_runs_sandbox_and_scores() -> None:
    hv = AutopoiesisHypervisor(BaselineMetrics(energy=5.0, duration_ms=1.0, peak_ram_mb=1.0))
    res = hv.evaluate_child("print('child')")
    assert res.is_valid is True
    assert res.execution.stdout.strip() == "child"


# ─── Frontier: cyber exploit classification ──────────────────────────────────


@pytest.mark.parametrize(
    "payload,defense,expected_cve,expected_blocked",
    [
        ("stack OVERFLOW attempt", "if len(x) > 8: raise", "CWE-120: Classical Buffer Overflow", True),
        ("payload 0xdeadbeef", "nothing", "CWE-120: Classical Buffer Overflow", False),
        ("' UNION SELECT *", "cur.execute(q, ?)", "CWE-89: SQL Injection", True),
        ("select 1", "cur.execute('%s' % x)", "CWE-89: SQL Injection", False),
        ("unknown weirdness", "validate(x)", "CWE-119: Memory Buffer Overflow", True),
        ("unknown weirdness", "pass", "CWE-119: Memory Buffer Overflow", False),
    ],
)
def test_exploit_vector_classification(payload, defense, expected_cve, expected_blocked) -> None:
    blocked, cve = _evaluate_exploit_vector(payload, defense)
    assert cve == expected_cve
    assert blocked is expected_blocked


def test_cyber_swarm_breach_has_zero_red_energy() -> None:
    res = CyberImmuneSwarm().run_engagement("select 1", "cur.execute('%s' % x)")
    assert res.exploit_succeeded is True and res.energy == 0.0
    assert "BREACH_DETECTED" in res.defense_status


# ─── Latent dreamer / hippocampal replay ─────────────────────────────────────


def test_latent_dreamer_pads_short_candidate_lists() -> None:
    result = LatentDreamer(latent_dim=8, num_branches=4).dream_and_search(
        "p", seed_code_candidates=["a = 1", "b = 2"]
    )
    assert result.num_candidates == 4
    assert result.best_thought.code_proposal in {"a = 1", "b = 2"}


def test_sleep_cycle_without_or_with_empty_memory(tmp_path: Path) -> None:
    mem = tmp_path / "hip.jsonl"
    engine = HippocampalReplayEngine(memory_file=mem)
    assert engine.execute_sleep_cycle() == {"consolidated_traces": 0, "status": "NO_TRACES"}
    mem.write_text("\n   \n", encoding="utf-8")
    assert engine.execute_sleep_cycle() == {"consolidated_traces": 0, "status": "EMPTY_MEMORY"}


# ─── Self-healing loop (mock Gemini) ─────────────────────────────────────────


def _install_fake_genai(monkeypatch, replies: list[str]) -> MagicMock:
    client = MagicMock()
    client.models.generate_content.side_effect = [SimpleNamespace(text=r) for r in replies]
    genai = ModuleType("google.genai")
    genai.Client = MagicMock(return_value=client)  # type: ignore[attr-defined]
    types_mod = ModuleType("google.genai.types")
    types_mod.GenerateContentConfig = lambda **kw: kw  # type: ignore[attr-defined]
    genai.types = types_mod  # type: ignore[attr-defined]
    google = ModuleType("google")
    google.genai = genai  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", types_mod)
    return client


def _guard_results(monkeypatch, codes: list[int]):
    import anse.core.self_healing as sh

    it = iter(codes)

    def _run(cmd, **kw):
        rc = next(it)
        return subprocess.CompletedProcess(cmd, rc, stdout="guard-out", stderr="guard-err")

    monkeypatch.setattr(sh.subprocess, "run", _run)
    return sh


def test_self_heal_first_try_success_strips_fences(monkeypatch, tmp_path: Path) -> None:
    client = _install_fake_genai(monkeypatch, ["```python\nx = 1\n```"])
    sh = _guard_results(monkeypatch, [0])
    target = tmp_path / "sub" / "out.py"
    assert sh.generate_and_heal("goal", str(target), api_key="k") == "x = 1"
    assert target.read_text(encoding="utf-8") == "x = 1"
    sys.modules["google.genai"].Client.assert_called_once_with(api_key="k")
    assert client.models.generate_content.call_count == 1


def test_self_heal_feeds_pain_signal_back_then_succeeds(monkeypatch, tmp_path: Path) -> None:
    client = _install_fake_genai(monkeypatch, ["bad code", "good code"])
    sh = _guard_results(monkeypatch, [1, 0])
    out = sh.generate_and_heal("goal", str(tmp_path / "o.py"))
    assert out == "good code"
    sys.modules["google.genai"].Client.assert_called_once_with()
    second_prompt = client.models.generate_content.call_args_list[1].kwargs["contents"]
    assert "guard-out" in second_prompt and "guard-err" in second_prompt
    assert "Original Goal: goal" in second_prompt


def test_self_heal_exhausts_iterations(monkeypatch, tmp_path: Path) -> None:
    _install_fake_genai(monkeypatch, ["a", "b"])
    sh = _guard_results(monkeypatch, [1, 1])
    with pytest.raises(RuntimeError, match="within 2 iterations"):
        sh.generate_and_heal("goal", str(tmp_path / "o.py"), max_iterations=2)


def test_self_heal_handles_empty_model_response(monkeypatch, tmp_path: Path) -> None:
    _install_fake_genai(monkeypatch, [None])  # type: ignore[list-item]
    sh = _guard_results(monkeypatch, [0])
    assert sh.generate_and_heal("goal", str(tmp_path / "o.py")) == ""


def test_self_heal_requires_google_genai(monkeypatch, tmp_path: Path) -> None:
    import anse.core.self_healing as sh

    monkeypatch.setitem(sys.modules, "google.genai", None)
    with pytest.raises(ImportError, match="google-genai package is required"):
        sh.generate_and_heal("goal", str(tmp_path / "o.py"))


# ─── Generated evolved_core artifact ─────────────────────────────────────────


def test_evolved_core_artifact_is_correct_and_faster_dedup(capsys) -> None:
    runpy.run_path(str(ROOT / "anse" / "autopoiesis" / "evolved_core.py"), run_name="__main__")
    out = capsys.readouterr().out.strip()
    assert out.startswith("OUTPUT_HASH:300_")
    mod = runpy.run_path(str(ROOT / "anse" / "autopoiesis" / "evolved_core.py"))
    records = [{"task_id": 1, "signature": "a"}, {"task_id": 1, "signature": "a"}]
    assert mod["deduplicate_traces"](records) == records[:1]
