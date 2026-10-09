#!/usr/bin/env python3
"""Tokenise the sandbox-verified episodes into a LoRA training npz (train / held-out / shuffled-label control).

Rows come ONLY from scripts/ltm_learning_mix.load_verified (origin 'sandbox', real converged verdicts);
transcript-origin and unverified call-log rows are never read here (origin policy, card N-9).

    .venv/bin/python scripts/tpu/prepare_lora_data.py MODEL_DIR OUT.npz [--holdout 2 6 10]

Layout per row:  prompt + "\\n" + code + EOS ; loss mask = 1 on code+EOS tokens only.
`shuf_*` pairs each training prompt with a different training row's completion (negative control).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from ltm_learning_mix import load_verified  # noqa: E402


def encode(tok, prompt: str, code: str, length: int) -> tuple[np.ndarray, np.ndarray]:
    p = tok(prompt + "\n", add_special_tokens=False)["input_ids"]
    c = tok(code, add_special_tokens=False)["input_ids"] + [tok.eos_token_id]
    ids = (p + c)[:length]
    mask = ([0] * len(p) + [1] * len(c))[:length]
    pad = length - len(ids)
    return (np.array(ids + [tok.eos_token_id] * pad, np.int32), np.array(mask + [0] * pad, np.int32))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_dir", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--holdout", type=int, nargs="+", default=[2, 6, 10])
    ap.add_argument("--length", type=int, default=192)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model_dir)
    rows = [r for r in load_verified() if r["verified"] and r["verdict"] and r["origin"] == "sandbox"]
    print(f"{len(rows)} verified+converged sandbox rows")
    tr = [r for i, r in enumerate(rows) if i not in a.holdout]
    ev = [r for i, r in enumerate(rows) if i in a.holdout]
    enc = lambda rs, shift=0: [encode(tok, r["prompt"], rs[(j + shift) % len(rs)]["completion"], a.length)  # noqa: E731
                               for j, r in enumerate(rs)]
    out = {}
    for name, rs, shift in (("train", tr, 0), ("eval", ev, 0), ("shuf", tr, 3)):
        e = enc(rs, shift)
        out[f"{name}_ids"], out[f"{name}_mask"] = np.stack([x[0] for x in e]), np.stack([x[1] for x in e])
    np.savez(a.out, **out)
    longest = int(max(m.sum() + 0 for m in out["train_mask"]))
    print({k: v.shape for k, v in out.items()}, "max completion tokens", longest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
