#!/usr/bin/env python3
"""LoRA fine-tune Qwen2.5-Coder-1.5B on the verified-episode npz, in pure JAX (TPU/CPU).

    python lora_train_jax.py MODEL_DIR DATA.npz OUT_DIR [--steps 40] [--lr 2e-4] [--r 16] [--alpha 32]

Runs two trainings from the same init and reports held-out NLL before/after for each:
  real     -- prompts paired with their own verified completions
  shuffled -- NEGATIVE CONTROL: prompts paired with other tasks' completions
The real adapter is saved in PEFT layout to OUT_DIR/real; the shuffled one to OUT_DIR/shuf.
Needs anse/training/jax_lora.py next to this script (the runner uploads both).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    import jax_lora as jl
except ModuleNotFoundError:
    from anse.training import jax_lora as jl


def run(tag: str, base, cfg, lora0, data, args, out: Path) -> dict[str, object]:
    key = "train" if tag == "real" else tag
    tr_ids, tr_mask = jnp.asarray(data[f"{key}_ids"]), jnp.asarray(data[f"{key}_mask"])
    ev_ids, ev_mask = jnp.asarray(data["eval_ids"]), jnp.asarray(data["eval_mask"])

    def loss_fn(lora, base_w, ids, mask):  # base_w is an argument, not a closure: no 3 GB compile constants
        return jl.masked_nll(jl.forward(base_w, lora, ids, cfg, args.alpha, args.r), ids, mask)

    vg_j = jax.jit(jax.value_and_grad(loss_fn))
    ev_j = jax.jit(loss_fn)

    def vg(lora, ids, mask):
        return vg_j(lora, base, ids, mask)

    def ev(lora, ids, mask):
        return ev_j(lora, base, ids, mask)

    step = jax.jit(lambda p, g, s: jl.adamw_step(p, g, s, args.lr))
    lora, st = lora0, jl.adam_init(lora0)
    ev0 = float(ev(lora, ev_ids, ev_mask))
    losses, curve = [], [ev0]
    t0 = time.time()
    for i in range(args.steps):
        loss, g = vg(lora, tr_ids, tr_mask)
        lora, st = step(lora, g, st)
        losses.append(float(loss))
        curve.append(float(ev(lora, ev_ids, ev_mask)))
        if i % 10 == 0 or i == args.steps - 1:
            print(f"  [{tag}] step {i:3d} train NLL {losses[-1]:.4f}", flush=True)
    jax.block_until_ready(lora)
    secs = time.time() - t0
    ev1 = float(ev(lora, ev_ids, ev_mask))
    jl.save_peft_adapter(lora, cfg, out / tag, args.r, args.alpha, "Qwen/Qwen2.5-Coder-1.5B")
    return {"tag": tag, "eval_nll_before": ev0, "eval_nll_after": ev1, "train_nll_first": losses[0],
            "train_nll_last": losses[-1], "seconds": secs, "steps": args.steps, "lr": args.lr,
            "eval_curve": curve, "best_eval_step": int(np.argmin(curve)), "best_eval_nll": float(min(curve))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_dir", type=Path)
    ap.add_argument("data", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--r", type=int, default=16)
    ap.add_argument("--alpha", type=float, default=32.0)
    args = ap.parse_args()
    print("backend", jax.default_backend(), jax.devices())
    cfg = jl.load_config(args.model_dir)
    base = jl.load_base(args.model_dir, jnp.bfloat16)
    data = np.load(args.data)
    lora0 = jl.init_lora(cfg, args.r, jax.random.PRNGKey(0))
    res = [run(tag, base, cfg, lora0, data, args, args.out) for tag in ("real", "shuf")]
    (args.out / f"report_lr{args.lr:g}.json").write_text(json.dumps(res, indent=1))
    for r in res:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
