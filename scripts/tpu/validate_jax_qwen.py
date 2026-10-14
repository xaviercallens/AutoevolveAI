#!/usr/bin/env python3
"""Validate anse.training.jax_lora against Hugging Face torch + PEFT (run on CPU, float32).

  1. positive: JAX base logits == HF Qwen2ForCausalLM logits
  2. positive: JAX logits with a random non-zero LoRA == PEFT-loaded saved adapter logits
  3. negative: JAX run with a wrong rope_theta must disagree with HF (the check can fail)
    .venv/bin/python scripts/tpu/validate_jax_qwen.py MODEL_DIR
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from anse.training import jax_lora as jl  # noqa: E402


def main(model_dir: Path) -> int:
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_dir)
    ids_np = tok("def sum_even(xs: list[int]) -> int:\n    return sum(x for x in xs if x % 2 == 0)\n",
                 return_tensors="np")["input_ids"].astype(np.int32)
    cfg = jl.load_config(model_dir)
    base = jl.load_base(model_dir, jnp.float32)
    hf = AutoModelForCausalLM.from_pretrained(model_dir, torch_dtype=torch.float32).eval()
    with torch.no_grad():
        ref = hf(torch.from_numpy(ids_np).long()).logits.numpy()
    with jax.default_matmul_precision("highest"):
        got = np.asarray(jl.forward(base, None, jnp.asarray(ids_np), cfg))
    err = float(np.max(np.abs(got - ref)))
    agree = float(np.mean(got.argmax(-1) == ref.argmax(-1)))
    print(f"[1] base logits: max abs err={err:.2e} (logit scale {np.abs(ref).max():.1f}), argmax agreement={agree:.3f}")

    lora = jl.init_lora(cfg, 16, jax.random.PRNGKey(0))
    lora = {k: (v if k.endswith(".A") else 0.02 * jax.random.normal(jax.random.PRNGKey(hash(k) % 2**31), v.shape))
            for k, v in lora.items()}
    with jax.default_matmul_precision("highest"):
        got_l = np.asarray(jl.forward(base, lora, jnp.asarray(ids_np), cfg))
    with tempfile.TemporaryDirectory() as d:
        jl.save_peft_adapter(lora, cfg, Path(d), 16, 32.0, str(model_dir))
        peft_model = PeftModel.from_pretrained(hf, d).eval()
        with torch.no_grad():
            ref_l = peft_model(torch.from_numpy(ids_np).long()).logits.numpy()
    err_l = float(np.max(np.abs(got_l - ref_l)))
    moved = float(np.max(np.abs(ref_l - ref)))
    print(f"[2] LoRA vs PEFT: max abs err={err_l:.2e}; adapter moved logits by {moved:.2f} (must be >> err)")

    bad_cfg = dict(cfg, rope_theta=10000.0)
    with jax.default_matmul_precision("highest"):
        bad = np.asarray(jl.forward(base, None, jnp.asarray(ids_np), bad_cfg))
    err_bad = float(np.max(np.abs(bad - ref)))
    print(f"[3] negative control (wrong rope_theta): max abs err={err_bad:.2e} (must be >> {err:.0e})")
    ok = err < 5e-3 and agree == 1.0 and err_l < 5e-3 and moved > 50 * err_l and err_bad > 100 * err
    print("controls", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
