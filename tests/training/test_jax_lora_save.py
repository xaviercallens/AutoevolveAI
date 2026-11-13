"""Regression: save_peft_adapter must write C-ordered bytes even when the host array is not C-contiguous.

Found on a TPU v5e: np.asarray(<(d,16) device array>) is not C-contiguous, and the safetensors writer
serialised the raw buffer, scrambling every lora_B (training numbers were right, saved adapters were not).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("jax")
from safetensors.numpy import load_file  # noqa: E402

from anse.training import jax_lora as jl  # noqa: E402

CFG = {"num_hidden_layers": 1}


class _FortranLike:
    """Mimics a TPU array: np.asarray(...) yields the right values in Fortran order."""

    def __init__(self, arr: np.ndarray) -> None:
        self._f = np.asfortranarray(arr)

    def __array__(self, dtype=None, copy=None):  # noqa: ANN001
        return self._f if dtype is None else self._f.astype(dtype, copy=False)


def _lora(b_wrapper) -> dict:
    rng = np.random.default_rng(0)
    out = {}
    for name in jl.TARGETS:
        out[f"0.{name}.A"] = rng.normal(size=(16, 24)).astype(np.float32)
        out[f"0.{name}.B"] = b_wrapper(rng.normal(size=(40, 16)).astype(np.float32))
    return out


def test_noncontiguous_b_is_saved_faithfully(tmp_path: Path) -> None:
    lora = _lora(_FortranLike)
    assert not np.asarray(lora["0.q_proj.B"]).flags["C_CONTIGUOUS"]
    jl.save_peft_adapter(lora, CFG, tmp_path, 16, 32.0, "x")
    back = load_file(str(tmp_path / "adapter_model.safetensors"))
    key = "base_model.model.model.layers.0.self_attn.q_proj.lora_B.weight"
    assert np.array_equal(back[key], np.asarray(lora["0.q_proj.B"]))
    assert back[key].shape == (40, 16)


def test_roundtrip_matches_for_all_tensors(tmp_path: Path) -> None:
    lora = _lora(lambda a: a)
    jl.save_peft_adapter(lora, CFG, tmp_path, 16, 32.0, "x")
    back = load_file(str(tmp_path / "adapter_model.safetensors"))
    assert len(back) == 2 * len(jl.TARGETS)
    for name in jl.TARGETS:
        block = "mlp" if name in ("gate_proj", "up_proj", "down_proj") else "self_attn"
        for ab in "AB":
            got = back[f"base_model.model.model.layers.0.{block}.{name}.lora_{ab}.weight"]
            assert np.array_equal(got, np.asarray(lora[f"0.{name}.{ab}"]))
