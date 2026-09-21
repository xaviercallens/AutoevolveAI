#!/usr/bin/env python3
"""Does a model actually fit the T4, and how fast is it? Measured, not estimated.

For each requested context length: load the model with that num_ctx, generate a fixed
prompt of ~300 new tokens, and record VRAM (nvidia-smi), Ollama's own GPU/CPU split
(/api/ps), prompt-processing and generation speed. Run against an isolated Ollama:

    OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_HOST=127.0.0.1:11435 ollama serve &
    python v2_runners/t4_fit_probe.py --model qwen3:8b --ctx 4096 8192 16384
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time

import httpx

PROMPT = ("Write a Python module implementing an LRU cache with O(1) get/put, thread safety, "
          "TTL expiry and full docstrings, followed by pytest tests. " * 1)


def vram_mib() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True).stdout
    return int(out.split()[0])


def probe(base: str, model: str, ctx: int, new_tokens: int) -> dict:
    client = httpx.Client(timeout=900)
    client.post(f"{base}/api/generate", json={"model": model, "keep_alive": 0})  # unload
    time.sleep(2)
    idle = vram_mib()
    body = {"model": model, "prompt": PROMPT, "stream": False, "think": False, "keep_alive": "10m",
            "options": {"num_ctx": ctx, "num_predict": new_tokens, "temperature": 0.2}}
    r = client.post(f"{base}/api/generate", json=body)
    j = r.json()
    if "error" in j:
        return {"model": model, "ctx": ctx, "ok": False, "error": j["error"][:200]}
    ps = next((m for m in client.get(f"{base}/api/ps").json().get("models", []) if m["name"].startswith(model.split(":")[0]) or True), {})
    size, in_vram = ps.get("size", 0), ps.get("size_vram", 0)
    return {
        "model": model, "ctx": ctx, "ok": True,
        "vram_mib_after": vram_mib(), "vram_mib_idle_before": idle,
        "gpu_fraction": round(in_vram / size, 3) if size else None,
        "prompt_tok_s": round(j["prompt_eval_count"] / max(j["prompt_eval_duration"], 1) * 1e9, 1),
        "gen_tok_s": round(j["eval_count"] / max(j["eval_duration"], 1) * 1e9, 1),
        "gen_tokens": j["eval_count"],
        "load_s": round(j.get("load_duration", 0) / 1e9, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--ctx", type=int, nargs="+", default=[4096, 8192])
    ap.add_argument("--base", default="http://127.0.0.1:11435")
    ap.add_argument("--new-tokens", type=int, default=300)
    ap.add_argument("--out")
    a = ap.parse_args()
    rows = []
    for ctx in a.ctx:
        row = probe(a.base, a.model, ctx, a.new_tokens)
        rows.append(row)
        print(json.dumps(row), flush=True)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rows, f, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
