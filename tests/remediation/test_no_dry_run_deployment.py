"""A DRY_RUN training result must never be recorded as a deployed checkpoint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import fakeredis
import pytest

from anse.infrastructure.fabrication import UnverifiedDataError
from daily_trainer_daemon import _record_successful_deployment, run_cycle


def _write_adapter_config(adapter_dir: Path, mode: str, with_weights: bool) -> None:
    adapter_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "base_model": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "dataset": "dummy.jsonl",
        "lora_rank": 16,
        "lora_alpha": 32,
        "mode": mode,
    }
    (adapter_dir / "adapter_config.json").write_text(json.dumps(config), encoding="utf-8")
    if with_weights:
        (adapter_dir / "adapter_model.safetensors").write_bytes(b"\x00" * 128)


class TestRecordSuccessfulDeployment:
    """_record_successful_deployment must refuse to deploy unverified adapters."""

    def test_dry_run_adapter_raises_and_writes_nothing(self, tmp_path: Path) -> None:
        """A DRY_RUN adapter with no weights must raise and leave Redis state untouched."""
        adapter_dir = tmp_path / "checkpoint_v1" / "final_adapter"
        _write_adapter_config(adapter_dir, mode="DRY_RUN", with_weights=False)

        r = fakeredis.FakeRedis(decode_responses=True)

        with pytest.raises(UnverifiedDataError):
            _record_successful_deployment(r, cycle_id=1, cycle_watermark=123.0, adapter_path=adapter_dir)

        assert r.get("antigravity:active_lora_version") is None
        assert r.lrange("antigravity:lora:history", 0, -1) == []

    def test_real_adapter_with_weights_is_recorded(self, tmp_path: Path) -> None:
        """A REAL adapter with weights on disk must be recorded and both keys set."""
        adapter_dir = tmp_path / "checkpoint_v2" / "final_adapter"
        _write_adapter_config(adapter_dir, mode="REAL", with_weights=True)

        r = fakeredis.FakeRedis(decode_responses=True)

        _record_successful_deployment(r, cycle_id=2, cycle_watermark=456.0, adapter_path=adapter_dir)

        assert r.get("antigravity:active_lora_version") == "checkpoint_v2"
        assert r.lrange("antigravity:lora:history", 0, -1) == ["v2"]
        assert r.get("antigravity:training:watermark_ts") == "456.0"


class TestRunCycleWatermark:
    """run_cycle must not advance the watermark when training only produced a dry-run."""

    def test_dry_run_result_does_not_advance_watermark(self, tmp_path: Path) -> None:
        """A dry-run adapter must fail the cycle and leave the watermark unchanged."""
        adapter_dir = tmp_path / "checkpoint_vX" / "final_adapter"
        _write_adapter_config(adapter_dir, mode="DRY_RUN", with_weights=False)

        r = fakeredis.FakeRedis(decode_responses=True)
        r.set("antigravity:training:watermark_ts", "100.0")

        dataset_file = tmp_path / "delta.jsonl"
        dataset_file.write_text("{}\n", encoding="utf-8")

        with (
            patch(
                "daily_trainer_daemon.extract_delta_dataset",
                return_value=(True, dataset_file, 200.0),
            ),
            patch("daily_trainer_daemon.run_training_job", return_value=adapter_dir),
            patch("daily_trainer_daemon.hot_reload_vllm_adapter", return_value=True),
        ):
            watermark_before = r.get("antigravity:training:watermark_ts")
            result = run_cycle(redis_client=r)
            watermark_after = r.get("antigravity:training:watermark_ts")

        assert result is False
        assert watermark_after == watermark_before == "100.0"
        assert r.get("antigravity:active_lora_version") is None
