"""Phase 1 coverage-completion tests: sandbox tiers, evaluator, encoder, harvester, CLI.

All tests are hermetic: no Docker daemon, no network, no model weights.
"""

from __future__ import annotations

import builtins
import importlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import torch

import anse.core.agent_loop as agent_loop_mod
import anse.symbolic.ml_sandbox as ml_sandbox_mod
import anse.symbolic.sandbox as sandbox_mod
from anse.config import MemoryConfig, ModelConfig
from anse.core.agent_loop import AgentLoop
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.memory.harvester import Harvester, LoopTrace
from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.sandbox import SandboxExecutor

# ─── Sandbox: runner-script regression + Docker fallback ─────────────────────


def test_tier1_runtime_error_reports_true_traceback_not_nameerror() -> None:
    """Regression: the runner once referenced an unimported ``subprocess`` name."""
    res = SandboxExecutor().execute("raise ValueError('boom')")
    assert res.returncode != 0
    assert "ValueError: boom" in res.stderr
    assert "NameError" not in res.stderr


def test_tier2_falls_back_when_docker_daemon_unreachable(monkeypatch) -> None:
    """docker.from_env() raises DockerException (not OSError) without a daemon."""

    class DockerException(Exception):
        pass

    def _boom() -> None:
        raise DockerException("Error while fetching server API version")

    monkeypatch.setitem(sys.modules, "docker", SimpleNamespace(from_env=_boom))
    res = SandboxExecutor().execute("import os\nprint('still runs')")
    assert res.tier_used == 2
    assert "Docker unavailable, fell back to Tier-1" in res.stderr
    assert "still runs" in res.stdout
    assert "os" in res.dangerous_imports


def _force_windows_env(monkeypatch, module) -> None:
    monkeypatch.setattr(module.sys, "platform", "win32")
    for k in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "SYSTEMDRIVE", "COMSPEC", "PATHEXT"):
        monkeypatch.setenv(k, "x")


def test_tier1_windows_env_passthrough(monkeypatch) -> None:
    _force_windows_env(monkeypatch, sandbox_mod)
    captured: dict = {}
    real_run = sandbox_mod.subprocess.run

    def _spy(*a, **kw):
        captured["env"] = kw["env"]
        return real_run(*a, **kw)

    monkeypatch.setattr(sandbox_mod.subprocess, "run", _spy)
    res = sandbox_mod._tier1_execute("print('hi')", 5.0)
    assert res.returncode == 0
    assert captured["env"]["SYSTEMROOT"] == "x"
    assert captured["env"]["COMSPEC"] == "x"


def test_tier1_windows_env_partial_passthrough(monkeypatch) -> None:
    monkeypatch.setattr(sandbox_mod.sys, "platform", "win32")
    monkeypatch.delenv("SYSTEMROOT", raising=False)
    res = sandbox_mod._tier1_execute("print('hi')", 5.0)
    assert res.returncode == 0


def test_tier1_corrupt_metric_files_are_ignored(monkeypatch) -> None:
    """A runner that writes non-numeric metrics must not crash the executor."""
    garbage_runner = (
        "import sys\n"
        "open(sys.argv[2], 'w').write('not-a-number')\n"
        "open(sys.argv[3], 'w').write('also-bad')\n"
    )
    monkeypatch.setattr(sandbox_mod, "_RUNNER_SCRIPT", garbage_runner)
    res = sandbox_mod._tier1_execute("print(1)", 5.0)
    assert res.peak_ram_mb == 0.0
    assert res.duration_ms > 0  # falls back to wall-clock measurement


# ─── ML sandbox ──────────────────────────────────────────────────────────────


def test_parse_ml_stats_ignores_corrupt_json(tmp_path: Path) -> None:
    stats = tmp_path / "stats.json"
    stats.write_text("{not json", encoding="utf-8")
    params, acc, val_loss, _, elapsed, mismatch, oom = ml_sandbox_mod._parse_ml_stats(
        stats, 0, "", 12.0
    )
    assert params == 0 and acc == 0.0 and val_loss == float("inf")
    assert elapsed == 12.0 and mismatch is False and oom is False


def test_parse_ml_stats_detects_oom_and_shape() -> None:
    p = Path("/nonexistent/stats.json")
    *_, mismatch, oom = ml_sandbox_mod._parse_ml_stats(p, 1, "CUDA out of memory", 1.0)
    assert oom is True and mismatch is False
    *_, mismatch, oom = ml_sandbox_mod._parse_ml_stats(p, 1, "size mismatch for fc", 1.0)
    assert mismatch is True and oom is False


def test_ml_tier1_windows_env_passthrough(monkeypatch) -> None:
    _force_windows_env(monkeypatch, ml_sandbox_mod)
    captured: dict = {}
    real_run = ml_sandbox_mod.subprocess.run

    def _spy(*a, **kw):
        captured["env"] = kw["env"]
        return real_run(*a, **kw)

    monkeypatch.setattr(ml_sandbox_mod.subprocess, "run", _spy)
    code = (
        "import torch.nn as nn\n"
        "class CandidateNet(nn.Module):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.fc = nn.Linear(20, 2)\n"
        "    def forward(self, x):\n"
        "        return self.fc(x)\n"
    )
    ml_sandbox_mod._tier1_ml_execute(code, 60.0)
    assert captured["env"]["SYSTEMROOT"] == "x"


def test_ml_runner_reports_true_traceback_not_nameerror() -> None:
    res = ml_sandbox_mod._tier1_ml_execute("raise RuntimeError('ml boom')", 60.0)
    assert "NameError" not in res.stderr


# ─── Evaluator ───────────────────────────────────────────────────────────────


def test_check_test_presence_paths() -> None:
    ev = EnergyEvaluator()
    assert ev._check_test_presence("3 passed in 0.1s", None) is True
    assert ev._check_test_presence("nothing", "assert x == 1") is True
    assert ev._check_test_presence("nothing", "assert(x)") is True
    assert ev._check_test_presence("nothing", "print(1)") is False
    assert ev._check_test_presence("nothing", None) is False


# ─── Encoder ─────────────────────────────────────────────────────────────────


def test_resolve_device_cpu_fallback(monkeypatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends, "mps", SimpleNamespace(is_available=lambda: False))
    ext = HiddenStateExtractor(config=ModelConfig(device="auto"), mock_mode=False)
    assert ext._device == "cpu"


def test_resolve_device_cuda_and_mps_and_explicit(monkeypatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    assert HiddenStateExtractor(config=ModelConfig(device="auto"))._device == "cuda"
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends, "mps", SimpleNamespace(is_available=lambda: True))
    assert HiddenStateExtractor(config=ModelConfig(device="auto"))._device == "mps"
    assert HiddenStateExtractor(config=ModelConfig(device="cpu"))._device == "cpu"
    assert HiddenStateExtractor(mock_mode=True)._device == "cpu"


def test_format_prompt_variants() -> None:
    ext = HiddenStateExtractor(mock_mode=True)
    ext._tokenizer = SimpleNamespace(chat_template=None)
    assert ext._format_prompt("hi", "be nice") == "System: be nice\n\nUser: hi\n\nAssistant:"
    assert ext._format_prompt("hi", None) == "User: hi\n\nAssistant:"

    tok = MagicMock()
    tok.chat_template = "tmpl"
    tok.apply_chat_template.return_value = "CHAT"
    ext._tokenizer = tok
    assert ext._format_prompt("hi", "sys") == "CHAT"
    assert tok.apply_chat_template.call_args.args[0][0] == {"role": "system", "content": "sys"}
    assert ext._format_prompt("hi", None) == "CHAT"


# ─── Harvester ───────────────────────────────────────────────────────────────


def _trace(**over) -> LoopTrace:
    base = dict(
        task="t", prompt="p", code="c", raw_response="r", energy=0.0,
        energy_category="ok", converged=True, iteration=1, duration_ms=1.0,
        returncode=0, execution_stdout="", execution_stderr="", hidden_state=[0.1, 0.2],
    )
    base.update(over)
    return LoopTrace(**base)


def _cfg(tmp_path: Path) -> MemoryConfig:
    return MemoryConfig(
        persist_directory=tmp_path / "chroma", interactions_log=tmp_path / "log.jsonl"
    )


def test_harvester_chroma_init_expected_failure(tmp_path: Path, monkeypatch) -> None:
    import chromadb

    def _bad(*a, **kw):
        raise ValueError("bad path")

    monkeypatch.setattr(chromadb, "PersistentClient", _bad)
    h = Harvester(config=_cfg(tmp_path), enable_chroma=True)
    assert h._chroma_collection is None


def test_harvester_chroma_init_unexpected_failure(tmp_path: Path, monkeypatch) -> None:
    import chromadb

    def _bad(*a, **kw):
        raise KeyError("weird")

    monkeypatch.setattr(chromadb, "PersistentClient", _bad)
    h = Harvester(config=_cfg(tmp_path), enable_chroma=True)
    assert h._chroma_client is None and h._chroma_collection is None


def test_harvester_upsert_failures_do_not_lose_jsonl(tmp_path: Path) -> None:
    h = Harvester(config=_cfg(tmp_path), enable_chroma=False)
    h._chroma_collection = MagicMock()
    h._chroma_collection.upsert.side_effect = ValueError("dim mismatch")
    h.record(_trace())
    h._chroma_collection.upsert.side_effect = KeyError("unexpected")
    h.record(_trace())
    assert h.get_trace_count() == 2


def test_harvester_build_hits_empty_and_sparse(tmp_path: Path) -> None:
    h = Harvester(config=_cfg(tmp_path), enable_chroma=False)
    assert h._build_hits({}) == []
    assert h._build_hits({"ids": []}) == []
    assert h._build_hits({"ids": [[]]}) == []
    sparse = h._build_hits({"ids": [["a"]]})
    assert sparse == [{"id": "a", "document": "", "metadata": {}, "distance": 0.0}]
    full = h._build_hits(
        {"ids": [["a"]], "documents": [["d"]], "metadatas": [[{"k": 1}]], "distances": [[0.5]]}
    )
    assert full[0]["distance"] == 0.5 and full[0]["document"] == "d"


def test_harvester_query_similar_paths(tmp_path: Path) -> None:
    h = Harvester(config=_cfg(tmp_path), enable_chroma=False)
    assert h.query_similar([0.1]) == []
    h._chroma_collection = MagicMock()
    h._chroma_collection.query.side_effect = RuntimeError("down")
    assert h.query_similar([0.1]) == []
    h._chroma_collection.query.side_effect = None
    h._chroma_collection.query.return_value = {"ids": [["x"]]}
    assert h.query_similar([0.1])[0]["id"] == "x"


def test_harvester_load_traces_tolerates_bad_lines(tmp_path: Path) -> None:
    h = Harvester(config=_cfg(tmp_path), enable_chroma=False)
    assert h.get_trace_count() == 0
    assert h.load_traces() == []
    good = json.dumps(_trace().to_dict())
    h.log_path.write_text(
        "\n".join(["", "{broken json", json.dumps({"unexpected": 1}), good]) + "\n",
        encoding="utf-8",
    )
    loaded = h.load_traces()
    assert len(loaded) == 1 and loaded[0].task == "t"


# ─── AgentLoop: JEPA import fallback + metadata ──────────────────────────────


def test_agent_loop_survives_missing_jepa(monkeypatch) -> None:
    real_import = builtins.__import__

    def _no_jepa(name, *a, **kw):
        if name == "anse.jepa.world_model":
            raise ImportError("no jepa")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", _no_jepa)
    try:
        reloaded = importlib.reload(agent_loop_mod)
        assert reloaded.JEPAWorldModel is None
    finally:
        monkeypatch.undo()
        importlib.reload(agent_loop_mod)


def _hs_record() -> HiddenStateRecord:
    return HiddenStateRecord(
        hidden_state=torch.ones(1, 8), layer_indices=[-1], token_count=1,
        model_id="mock", device="mock",
    )


def _loop_with(world_model, tmp_path: Path) -> AgentLoop:
    h = Harvester(config=_cfg(tmp_path), enable_chroma=False)
    return AgentLoop(
        extractor=HiddenStateExtractor(mock_mode=True), harvester=h, world_model=world_model
    )


def test_agent_loop_metadata_with_and_without_world_model(tmp_path: Path) -> None:
    exec_res = SandboxExecutor().execute("print(1)")
    energy_res = EnergyEvaluator().evaluate(exec_res)

    plain = _loop_with(None, tmp_path)._build_trace_metadata(_hs_record(), exec_res, energy_res)
    assert "jepa_predicted_energy" not in plain

    wm = MagicMock()
    wm.predict_energy_scalar.return_value = 7.0
    meta = _loop_with(wm, tmp_path)._build_trace_metadata(_hs_record(), exec_res, energy_res)
    assert meta["jepa_predicted_energy"] == 7.0
    assert meta["jepa_surprise"] == round(abs(7.0 - energy_res.score), 2)

    wm.predict_energy_scalar.side_effect = RuntimeError("jepa down")
    meta = _loop_with(wm, tmp_path)._build_trace_metadata(_hs_record(), exec_res, energy_res)
    assert meta["jepa_error"] == "jepa down"


# ─── main.py CLI ─────────────────────────────────────────────────────────────


def test_load_tasks_accepts_list_and_rejects_unknown_shapes(tmp_path: Path) -> None:
    from main import load_tasks

    as_list = tmp_path / "list.yaml"
    as_list.write_text("- {name: a, task: b}\n", encoding="utf-8")
    assert load_tasks(as_list) == [{"name": "a", "task": "b"}]
    as_scalar = tmp_path / "scalar.yaml"
    as_scalar.write_text("hello\n", encoding="utf-8")
    assert load_tasks(as_scalar) == []


def _run_main(monkeypatch, tmp_path: Path, extra: list[str]) -> int:
    from main import main

    monkeypatch.setattr(
        sys, "argv",
        ["main.py", "--mock-llm", "--no-chroma", "--output-dir", str(tmp_path), *extra],
    )
    return main()


def test_main_benchmark_empty_task_file_fails(monkeypatch, tmp_path: Path) -> None:
    empty = tmp_path / "empty.yaml"
    empty.write_text("[]\n", encoding="utf-8")
    assert _run_main(monkeypatch, tmp_path, ["--tasks", str(empty)]) == 1


def test_main_benchmark_pass_and_fail_thresholds(monkeypatch, tmp_path: Path) -> None:
    tasks = tmp_path / "tasks.yaml"
    tasks.write_text("tasks:\n  - {name: a, task: 'Return True'}\n", encoding="utf-8")
    import main as main_mod

    monkeypatch.setattr(main_mod, "run_benchmark", lambda *a, **k: ([], 100.0))
    assert _run_main(monkeypatch, tmp_path, ["--tasks", str(tasks)]) == 0
    monkeypatch.setattr(main_mod, "run_benchmark", lambda *a, **k: ([], 10.0))
    assert _run_main(monkeypatch, tmp_path, ["--tasks", str(tasks)]) == 1


def test_main_dunder_main_guard(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        sys, "argv",
        ["main.py", "--mock-llm", "--no-chroma", "--output-dir", str(tmp_path),
         "--single-task", "Return True"],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(__file__).resolve().parents[2] / "main.py"), run_name="__main__")
    assert exc.value.code == 0


# ─── Branch-completion tests ─────────────────────────────────────────────────


class _FakeTokenizer:
    chat_template = None
    eos_token_id = 0
    pad_token_id = 0

    def __init__(self, with_mask: bool) -> None:
        self.with_mask = with_mask

    def __call__(self, text, return_tensors="pt"):
        out = {"input_ids": torch.tensor([[1, 2, 3]])}
        if self.with_mask:
            out["attention_mask"] = torch.ones(1, 3, dtype=torch.long)
        return out

    def decode(self, tokens, skip_special_tokens=True):
        return "decoded"


class _FakeModel:
    device = "cpu"

    def generate(self, **kw):
        return SimpleNamespace(
            sequences=torch.tensor([[1, 2, 3, 4, 5]]),
            hidden_states=((torch.zeros(1, 1, 8),), (torch.ones(1, 1, 8),)),
        )


@pytest.mark.parametrize("with_mask", [True, False])
def test_extract_real_path_with_and_without_attention_mask(with_mask: bool) -> None:
    ext = HiddenStateExtractor(config=ModelConfig(device="cpu"), mock_mode=False)
    ext._model = _FakeModel()
    ext._tokenizer = _FakeTokenizer(with_mask)
    text, record = ext.extract("hi")
    assert text == "decoded"
    assert record.token_count == 2 and record.hidden_state.shape == (1, 8)
    assert float(record.hidden_state.sum()) == 8.0


def test_sandbox_visit_import_from_relative_and_metric_files_absent(monkeypatch) -> None:
    # `from . import x` has node.module None -> must not be flagged or crash the scanner
    assert sandbox_mod.scan_dangerous_imports("from . import sibling", ["os"]) == []
    # A runner that emits no metric files: executor keeps wall-clock time and zero RAM.
    monkeypatch.setattr(sandbox_mod, "_RUNNER_SCRIPT", "print('bare')\n")
    res = sandbox_mod._tier1_execute("print(1)", 5.0)
    assert res.peak_ram_mb == 0.0 and res.duration_ms > 0 and "bare" in res.stdout


def test_ml_windows_env_skips_unset_variables(monkeypatch) -> None:
    monkeypatch.setattr(ml_sandbox_mod.sys, "platform", "win32")
    monkeypatch.delenv("SYSTEMROOT", raising=False)
    monkeypatch.setenv("WINDIR", "w")
    captured: dict = {}
    real_run = ml_sandbox_mod.subprocess.run

    def _spy(*a, **kw):
        captured["env"] = kw["env"]
        return real_run(*a, **kw)

    monkeypatch.setattr(ml_sandbox_mod.subprocess, "run", _spy)
    ml_sandbox_mod._tier1_ml_execute("raise SystemExit(0)", 60.0)
    assert "SYSTEMROOT" not in captured["env"] and captured["env"]["WINDIR"] == "w"


def test_evaluator_matching_expected_output_and_default_singleton() -> None:
    from anse.symbolic import evaluator as ev_mod

    res = SandboxExecutor().execute("assert True\nprint('ok')")
    matched = EnergyEvaluator().evaluate(res, expected_output="ok")
    assert matched.category.name != "WRONG_OUTPUT"
    ev_mod._default_evaluator = None
    first = ev_mod.evaluate_energy(res, expected_output="ok")
    second = ev_mod.evaluate_energy(res, expected_output="ok")  # singleton already built
    assert first.score == second.score


def test_main_without_output_dir_keeps_default_paths(monkeypatch) -> None:
    from main import main

    monkeypatch.setattr(sys, "argv", ["main.py", "--mock-llm", "--no-chroma", "--single-task", "x"])
    import main as main_mod

    seen: dict = {}

    class _Loop:
        def __init__(self, **kw) -> None:
            seen["memory"] = kw["config"].memory

        def run(self, task, max_retries):
            return SimpleNamespace(final_energy=0.0, final_category="ok", iterations=1, converged=True)

    monkeypatch.setattr(main_mod, "AgentLoop", _Loop)
    monkeypatch.setattr(main_mod, "Harvester", lambda **kw: object())
    assert main() == 0
