"""Pure-JAX Qwen2 forward pass with LoRA, for TPU/GPU/CPU. No flax/optax/transformers needed.

* Base weights are frozen and loaded straight from the HF `model.safetensors` (bf16 or f32).
* LoRA (r, alpha) is applied to q/k/v/o and gate/up/down projections, like scripts/train_qwen_lora.py.
* `save_peft_adapter` writes `adapter_model.safetensors` + `adapter_config.json` in the layout
  PEFT expects, so the trained adapter loads with `PeftModel.from_pretrained` (verified in tests).
* The forward pass is checked against the Hugging Face torch model in
  scripts/tpu/validate_jax_qwen.py before any training number is trusted.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np
from safetensors.flax import load_file, save_file

Params = dict[str, Any]
TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")


def load_config(model_dir: Path) -> dict[str, Any]:
    return json.loads((model_dir / "config.json").read_text())


def load_base(model_dir: Path, dtype: Any = jnp.bfloat16) -> Params:
    raw = load_file(str(model_dir / "model.safetensors"))
    return {k: v.astype(dtype) for k, v in raw.items()}


def init_lora(cfg: Mapping[str, Any], r: int, key: jax.Array) -> Params:
    """A ~ N(0, 1/r-ish) kaiming-uniform like PEFT, B = 0 so the adapter starts as a no-op."""
    h, ff = cfg["hidden_size"], cfg["intermediate_size"]
    nh, nkv = cfg["num_attention_heads"], cfg["num_key_value_heads"]
    hd = h // nh
    shapes = {
        "q_proj": (h, nh * hd), "k_proj": (h, nkv * hd), "v_proj": (h, nkv * hd), "o_proj": (nh * hd, h),
        "gate_proj": (h, ff), "up_proj": (h, ff), "down_proj": (ff, h),
    }
    lora: Params = {}
    for layer in range(cfg["num_hidden_layers"]):
        for name in TARGETS:
            d_in, d_out = shapes[name]
            key, sub = jax.random.split(key)
            bound = 1.0 / np.sqrt(d_in)
            lora[f"{layer}.{name}.A"] = jax.random.uniform(sub, (r, d_in), jnp.float32, -bound, bound)
            lora[f"{layer}.{name}.B"] = jnp.zeros((d_out, r), jnp.float32)
    return lora


def _rms(x: jax.Array, w: jax.Array, eps: float) -> jax.Array:
    xf = x.astype(jnp.float32)
    xf = xf * jax.lax.rsqrt(jnp.mean(xf * xf, axis=-1, keepdims=True) + eps)
    return (w.astype(jnp.float32) * xf).astype(x.dtype)


def _rope(seq: int, hd: int, theta: float) -> tuple[jax.Array, jax.Array]:
    inv = 1.0 / (theta ** (jnp.arange(0, hd, 2, dtype=jnp.float32) / hd))
    ang = jnp.arange(seq, dtype=jnp.float32)[:, None] * inv[None, :]
    emb = jnp.concatenate([ang, ang], axis=-1)
    return jnp.cos(emb), jnp.sin(emb)


def _rot(x: jax.Array) -> jax.Array:
    h = x.shape[-1] // 2
    return jnp.concatenate([-x[..., h:], x[..., :h]], axis=-1)


def _linear(x: jax.Array, base: Params, lora: Params | None, scale: float, layer: int, name: str,
            prefix: str, bias: bool) -> jax.Array:
    w = base[f"{prefix}.{name}.weight"]
    y = x @ w.T
    if bias:
        y = y + base[f"{prefix}.{name}.bias"]
    if lora is not None:
        a, b = lora[f"{layer}.{name}.A"], lora[f"{layer}.{name}.B"]
        y = y + (scale * ((x.astype(jnp.float32) @ a.T) @ b.T)).astype(y.dtype)
    return y


def forward(base: Params, lora: Params | None, ids: jax.Array, cfg: Mapping[str, Any],
            alpha: float = 32.0, r: int = 16) -> jax.Array:
    """Logits (batch, seq, vocab) in float32. `ids` int32 (batch, seq); causal attention, no padding mask
    (right-padded batches are fine because the loss mask ignores pad positions)."""
    nh, nkv = cfg["num_attention_heads"], cfg["num_key_value_heads"]
    hd = cfg["hidden_size"] // nh
    eps = cfg["rms_norm_eps"]
    scale = alpha / r
    x = base["model.embed_tokens.weight"][ids]
    seq = ids.shape[1]
    cos, sin = _rope(seq, hd, cfg["rope_theta"])
    causal = jnp.tril(jnp.ones((seq, seq), bool))
    for layer in range(cfg["num_hidden_layers"]):
        p = f"model.layers.{layer}"
        h = _rms(x, base[f"{p}.input_layernorm.weight"], eps)
        q = _linear(h, base, lora, scale, layer, "q_proj", f"{p}.self_attn", True)
        k = _linear(h, base, lora, scale, layer, "k_proj", f"{p}.self_attn", True)
        v = _linear(h, base, lora, scale, layer, "v_proj", f"{p}.self_attn", True)
        b = ids.shape[0]
        q = q.reshape(b, seq, nh, hd).transpose(0, 2, 1, 3)
        k = k.reshape(b, seq, nkv, hd).transpose(0, 2, 1, 3)
        v = v.reshape(b, seq, nkv, hd).transpose(0, 2, 1, 3)
        q = q * cos.astype(q.dtype) + _rot(q) * sin.astype(q.dtype)
        k = k * cos.astype(k.dtype) + _rot(k) * sin.astype(k.dtype)
        rep = nh // nkv
        k, v = jnp.repeat(k, rep, axis=1), jnp.repeat(v, rep, axis=1)
        att = (q.astype(jnp.float32) @ k.astype(jnp.float32).transpose(0, 1, 3, 2)) / np.sqrt(hd)
        att = jnp.where(causal, att, -1e30)
        att = jax.nn.softmax(att, axis=-1).astype(v.dtype)
        o = (att @ v).transpose(0, 2, 1, 3).reshape(b, seq, nh * hd)
        x = x + _linear(o, base, lora, scale, layer, "o_proj", f"{p}.self_attn", False)
        h = _rms(x, base[f"{p}.post_attention_layernorm.weight"], eps)
        g = _linear(h, base, lora, scale, layer, "gate_proj", f"{p}.mlp", False)
        u = _linear(h, base, lora, scale, layer, "up_proj", f"{p}.mlp", False)
        x = x + _linear(jax.nn.silu(g) * u, base, lora, scale, layer, "down_proj", f"{p}.mlp", False)
    x = _rms(x, base["model.norm.weight"], eps)
    head = base.get("lm_head.weight", base["model.embed_tokens.weight"])
    return (x @ head.T).astype(jnp.float32)


def masked_nll(logits: jax.Array, ids: jax.Array, mask: jax.Array) -> jax.Array:
    """Mean next-token NLL over positions where mask[t+1] == 1 (mask marks completion tokens)."""
    logp = jax.nn.log_softmax(logits[:, :-1], axis=-1)
    tok = jnp.take_along_axis(logp, ids[:, 1:, None], axis=-1)[..., 0]
    m = mask[:, 1:].astype(jnp.float32)
    return -(tok * m).sum() / jnp.maximum(m.sum(), 1.0)


def adam_init(params: Params) -> Params:
    return {"m": jax.tree_util.tree_map(jnp.zeros_like, params),
            "v": jax.tree_util.tree_map(jnp.zeros_like, params), "t": jnp.zeros((), jnp.int32)}


def adamw_step(params: Params, grads: Params, st: Params, lr: float, wd: float = 0.0,
               b1: float = 0.9, b2: float = 0.999, eps: float = 1e-8) -> tuple[Params, Params]:
    t = st["t"] + 1
    m = jax.tree_util.tree_map(lambda m_, g: b1 * m_ + (1 - b1) * g, st["m"], grads)
    v = jax.tree_util.tree_map(lambda v_, g: b2 * v_ + (1 - b2) * g * g, st["v"], grads)
    mh = jax.tree_util.tree_map(lambda x: x / (1 - b1 ** t), m)
    vh = jax.tree_util.tree_map(lambda x: x / (1 - b2 ** t), v)
    new = jax.tree_util.tree_map(lambda p, a, b_: p - lr * (a / (jnp.sqrt(b_) + eps) + wd * p), params, mh, vh)
    return new, {"m": m, "v": v, "t": t}


def save_peft_adapter(lora: Params, cfg: Mapping[str, Any], out: Path, r: int, alpha: float,
                      base_model: str) -> None:
    """PEFT layout: base_model.model.model.layers.N.<block>.<proj>.lora_{A,B}.weight"""
    out.mkdir(parents=True, exist_ok=True)
    tensors = {}
    for key, val in lora.items():
        layer, name, ab = key.split(".")
        block = "mlp" if name in ("gate_proj", "up_proj", "down_proj") else "self_attn"
        tensors[f"base_model.model.model.layers.{layer}.{block}.{name}.lora_{ab}.weight"] = val.astype(jnp.float32)
    save_file(tensors, str(out / "adapter_model.safetensors"), metadata={"format": "pt"})
    (out / "adapter_config.json").write_text(json.dumps({
        "peft_type": "LORA", "task_type": "CAUSAL_LM", "base_model_name_or_path": base_model,
        "r": r, "lora_alpha": alpha, "lora_dropout": 0.0, "bias": "none",
        "target_modules": list(TARGETS), "fan_in_fan_out": False, "inference_mode": True,
    }, indent=1))
