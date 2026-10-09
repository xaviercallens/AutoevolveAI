"""Tests for anse.infrastructure.agent_environment.

Only external I/O (env vars, the nvidia-smi subprocess) is mocked; the
resolver logic itself always runs for real.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anse.infrastructure.agent_environment import (
    ANTIGRAVITY,
    CLAUDE_CODE,
    UNKNOWN_AGENT,
    CapabilityProfile,
    GPUInfo,
    LLMBackend,
    TPUInfo,
    _parse_nvidia_smi_csv,
    _select_llm_backend,
    detect_coding_agent,
    detect_gpu,
    detect_tpu,
    resolve_capability_profile,
)


class TestDetectCodingAgent:
    def test_claudecode_env_var_wins(self) -> None:
        with patch.dict("os.environ", {"CLAUDECODE": "1"}, clear=True):
            assert detect_coding_agent() == CLAUDE_CODE

    def test_override_takes_precedence_over_signals(self) -> None:
        with patch.dict(
            "os.environ", {"CLAUDECODE": "1", "AUTOEVOLVE_AGENT": "antigravity"}, clear=True
        ):
            assert detect_coding_agent() == ANTIGRAVITY

    def test_invalid_override_is_ignored_falls_back_to_signal(self) -> None:
        with patch.dict(
            "os.environ", {"CLAUDECODE": "1", "AUTOEVOLVE_AGENT": "not-a-real-agent"}, clear=True
        ):
            assert detect_coding_agent() == CLAUDE_CODE

    def test_no_signals_and_no_antigravity_dir_presence_gives_unknown(self) -> None:
        # .antigravity/ exists on disk in every checkout of this repo, so a
        # bare env with no agent signals must still resolve to "unknown" --
        # proves the resolver isn't secretly inferring from the filesystem.
        with patch.dict("os.environ", {}, clear=True):
            assert detect_coding_agent() == UNKNOWN_AGENT

    def test_claude_code_entrypoint_alone_is_sufficient_signal(self) -> None:
        with patch.dict("os.environ", {"CLAUDE_CODE_ENTRYPOINT": "cli"}, clear=True):
            assert detect_coding_agent() == CLAUDE_CODE

    def test_antigravity_agent_env_var_wins(self) -> None:
        with patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=True):
            assert detect_coding_agent() == ANTIGRAVITY

    def test_antigravity_conversation_id_signal(self) -> None:
        with patch.dict("os.environ", {"ANTIGRAVITY_CONVERSATION_ID": "conv-1234"}, clear=True):
            assert detect_coding_agent() == ANTIGRAVITY


class TestParseNvidiaSmiCsv:
    def test_parses_name_and_memory(self) -> None:
        info = _parse_nvidia_smi_csv("Tesla T4, 15360 MiB\n")
        assert info.available is True
        assert info.name == "Tesla T4"
        assert info.total_memory_mb == 15360

    def test_malformed_output_reports_unavailable_with_reason(self) -> None:
        info = _parse_nvidia_smi_csv("garbage-no-comma")
        assert info.available is False
        assert info.probe_error is not None


class TestDetectGpu:
    def test_nvidia_smi_missing_from_path_gives_unavailable(self) -> None:
        with patch("shutil.which", return_value=None):
            info = detect_gpu()
        assert info.available is False
        assert info.name is None
        assert "PATH" in (info.probe_error or "")

    def test_nvidia_smi_present_but_driver_unreachable(self) -> None:
        # Reproduces this project's own GCP host: exit 9, driver error text.
        completed = subprocess.CompletedProcess(
            args=["nvidia-smi"],
            returncode=9,
            stdout="",
            stderr="NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.",
        )
        with (
            patch("shutil.which", return_value="/usr/bin/nvidia-smi"),
            patch("subprocess.run", return_value=completed),
        ):
            info = detect_gpu()
        assert info.available is False
        assert "driver" in (info.probe_error or "").lower()

    def test_timeout_reports_unavailable_not_a_crash(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/nvidia-smi"),
            patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="nvidia-smi", timeout=5.0)),
        ):
            info = detect_gpu()
        assert info.available is False
        assert "timed out" in (info.probe_error or "")


class TestSelectLlmBackend:
    def test_t4_gpu_name_selects_t4_profile(self) -> None:
        gpu = GPUInfo(available=True, name="Tesla T4", total_memory_mb=15360, probe_error=None)
        with patch.dict("os.environ", {}, clear=True):
            backend = _select_llm_backend(gpu)
        assert backend.generation_model == "qwen3:8b"
        assert backend.embedding_model == "qwen3-embedding:0.6b"

    def test_no_gpu_falls_back_to_cpu_backend(self) -> None:
        gpu = GPUInfo(available=False, name=None, total_memory_mb=None, probe_error="nvidia-smi not on PATH")
        with patch.dict("os.environ", {}, clear=True):
            backend = _select_llm_backend(gpu)
        assert backend.generation_model == "qwen2.5-coder:1.5b"

    def test_gpu_hint_overrides_a_failed_live_probe(self) -> None:
        # The exact scenario this repo hits: nvidia-smi unreachable, but the
        # operator knows the box has a T4 (Ollama is live and serving the
        # models the T4 profile expects).
        gpu = GPUInfo(available=False, name=None, total_memory_mb=None, probe_error="driver unreachable")
        with patch.dict("os.environ", {"AUTOEVOLVE_GPU_HINT": "t4"}, clear=True):
            backend = _select_llm_backend(gpu)
        assert backend.generation_model == "qwen3:8b"


class TestResolveCapabilityProfile:
    def test_claude_code_profile_points_at_dot_claude_and_mcp_json(self, tmp_path: Path) -> None:
        with (
            patch.dict("os.environ", {"CLAUDECODE": "1"}, clear=True),
            patch("shutil.which", return_value=None),
        ):
            profile = resolve_capability_profile(project_root=tmp_path)
        assert profile.coding_agent == CLAUDE_CODE
        assert profile.config_dir == tmp_path / ".claude"
        assert profile.mcp_config_path == tmp_path / ".mcp.json"

    def test_antigravity_profile_points_at_dot_antigravity(self, tmp_path: Path) -> None:
        with (
            patch.dict("os.environ", {"AUTOEVOLVE_AGENT": "antigravity"}, clear=True),
            patch("shutil.which", return_value=None),
        ):
            profile = resolve_capability_profile(project_root=tmp_path)
        assert profile.coding_agent == ANTIGRAVITY
        assert profile.config_dir == tmp_path / ".antigravity"
        assert profile.mcp_config_path == tmp_path / ".antigravity" / "mcp_config.json"

    def test_as_dict_is_json_serializable(self, tmp_path: Path) -> None:
        import json

        with (
            patch.dict("os.environ", {"CLAUDECODE": "1"}, clear=True),
            patch("shutil.which", return_value=None),
        ):
            profile = resolve_capability_profile(project_root=tmp_path)
        encoded = json.dumps(profile.as_dict())
        decoded = json.loads(encoded)
        assert decoded["coding_agent"] == CLAUDE_CODE
        assert decoded["config_dir"] == str(tmp_path / ".claude")

    def test_env_overrides_match_selected_llm_backend(self, tmp_path: Path) -> None:
        with (
            patch.dict("os.environ", {"CLAUDECODE": "1", "AUTOEVOLVE_GPU_HINT": "t4"}, clear=True),
            patch("shutil.which", return_value=None),
        ):
            profile = resolve_capability_profile(project_root=tmp_path)
        overrides = profile.env_overrides()
        assert overrides["ANSE_API_MODEL"] == "qwen3:8b"
        assert overrides["ANSE_EMBEDDING_MODEL"] == "qwen3-embedding:0.6b"

    def test_antigravity_cpu_profile_resolution(self, tmp_path: Path) -> None:
        with (
            patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=True),
            patch("shutil.which", return_value=None),
        ):
            profile = resolve_capability_profile(project_root=tmp_path)
        assert profile.coding_agent == ANTIGRAVITY
        assert profile.device == "cpu"
        assert profile.supports_local_lora is True
        assert profile.supports_local_rl is True
        assert profile.supports_local_jepa is True
        assert profile.config_dir == tmp_path / ".antigravity"
        assert profile.mcp_config_path == tmp_path / ".antigravity" / "mcp_config.json"
        assert "antigravity_linux_cpu_" in profile.profile_id


class TestDetectSystemMemory:
    def test_detect_system_memory_returns_positive_ram(self) -> None:
        from anse.infrastructure.agent_environment import detect_system_memory

        mem = detect_system_memory()
        assert mem.total_mb > 0
        assert mem.available_mb > 0
        assert mem.ram_gb > 0.0


@given(
    name=st.text(min_size=1, max_size=40).filter(
        lambda s: "," not in s and s.strip() == s and s != ""
    )
)
def test_parse_nvidia_smi_csv_never_crashes_on_arbitrary_names(name: str) -> None:
    """Property: any single-field or two-field CSV-ish line either parses to
    a well-formed GPUInfo or reports unavailable -- it never raises."""
    line = f"{name}, 8192 MiB"
    info = _parse_nvidia_smi_csv(line)
    assert isinstance(info, GPUInfo)
    if info.available:
        assert info.name == name
        assert info.total_memory_mb == 8192
    else:
        assert info.probe_error is not None


def test_capability_profile_is_frozen(tmp_path: Path) -> None:
    profile = CapabilityProfile(
        coding_agent=CLAUDE_CODE,
        gpu=GPUInfo(available=False, name=None, total_memory_mb=None, probe_error="x"),
        llm=LLMBackend(generation_model="m", embedding_model="e", reason="r"),
        config_dir=tmp_path,
        mcp_config_path=tmp_path / "x.json",
    )
    with pytest.raises(AttributeError):
        profile.coding_agent = ANTIGRAVITY  # type: ignore[misc]


class TestDetectTpu:
    def test_local_tpu_via_accel_nodes(self) -> None:
        with (
            patch.dict("os.environ", {"TPU_ACCELERATOR_TYPE": "v4-8"}, clear=True),
            patch("anse.infrastructure.agent_environment.glob.glob", return_value=["/dev/accel0"]),
        ):
            info = detect_tpu()
        assert info.available and info.kind == "local"
        assert info.accelerator_type == "v4-8"

    def test_vfio_without_metadata_is_not_a_tpu(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("anse.infrastructure.agent_environment._tpu_metadata_accelerator", return_value=None),
            patch("anse.infrastructure.agent_environment.glob.glob",
                  side_effect=lambda pat: ["/dev/vfio/0"] if "vfio" in pat else []),
        ):
            info = detect_tpu()
        assert not info.available
        assert info.kind is None

    def test_vfio_with_metadata_is_local_v5e(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("anse.infrastructure.agent_environment._tpu_metadata_accelerator",
                  return_value="v5litepod-1"),
            patch("anse.infrastructure.agent_environment.glob.glob",
                  side_effect=lambda pat: ["/dev/vfio/0"] if "vfio" in pat else []),
        ):
            info = detect_tpu()
        assert info.available and info.kind == "local"
        assert info.accelerator_type == "v5litepod-1"

    def test_remote_tpu_ready(self) -> None:
        done = subprocess.CompletedProcess([], 0, stdout="READY\tv5litepod-1\n", stderr="")
        env = {"AUTOEVOLVE_TPU_NAME": "gwenlaya-tpu-1", "AUTOEVOLVE_TPU_ZONE": "us-west4-a"}
        with (
            patch.dict("os.environ", env, clear=True),
            patch("anse.infrastructure.agent_environment.glob.glob", return_value=[]),
            patch("anse.infrastructure.agent_environment._tpu_metadata_accelerator", return_value=None),
            patch("anse.infrastructure.agent_environment.shutil.which", return_value="/usr/bin/gcloud"),
            patch("anse.infrastructure.agent_environment.subprocess.run", return_value=done),
        ):
            info = detect_tpu()
        assert info.available and info.kind == "remote"
        assert info.name == "gwenlaya-tpu-1" and info.accelerator_type == "v5litepod-1"

    def test_remote_tpu_not_ready_reports_error(self) -> None:
        done = subprocess.CompletedProcess([], 0, stdout="CREATING\tv5litepod-1\n", stderr="")
        env = {"AUTOEVOLVE_TPU_NAME": "t", "AUTOEVOLVE_TPU_ZONE": "z"}
        with (
            patch.dict("os.environ", env, clear=True),
            patch("anse.infrastructure.agent_environment.glob.glob", return_value=[]),
            patch("anse.infrastructure.agent_environment._tpu_metadata_accelerator", return_value=None),
            patch("anse.infrastructure.agent_environment.shutil.which", return_value="/usr/bin/gcloud"),
            patch("anse.infrastructure.agent_environment.subprocess.run", return_value=done),
        ):
            info = detect_tpu()
        assert not info.available
        assert info.probe_error is not None and "CREATING" in info.probe_error

    def test_no_signal_means_no_tpu(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("anse.infrastructure.agent_environment.glob.glob", return_value=[]),
            patch("anse.infrastructure.agent_environment._tpu_metadata_accelerator", return_value=None),
        ):
            info = detect_tpu()
        assert not info.available
        assert info.kind is None

    def test_profile_exposes_jax_platform_and_keeps_torch_device_safe(self) -> None:
        tpu = TPUInfo(True, "local", "v5litepod-1", None, None)
        with (
            patch("anse.infrastructure.agent_environment.detect_tpu", return_value=tpu),
            patch("anse.infrastructure.agent_environment.detect_gpu",
                  return_value=GPUInfo(False, None, None, "nvidia-smi not on PATH")),
        ):
            profile = resolve_capability_profile()
        assert profile.jax_platform == "tpu"
        assert profile.device == "cpu"
        assert profile.env_overrides()["ANSE_JAX_PLATFORM"] == "tpu"
        assert profile.profile_id.endswith("_tpu_v5litepod-1")
