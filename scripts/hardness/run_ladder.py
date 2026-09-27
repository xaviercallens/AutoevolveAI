#!/usr/bin/env python3
"""Run prover models over the validated hardness ladder; kernel decides.

One model at a time over every item (model swaps cost ~200 s on the T4).
Each attempt: /api/chat -> take the LAST Lean block from content+thinking
(Goedel-V2 puts its whole answer in `thinking` and writes a sorry-sketch
before the real proof) -> strip model imports -> pinned header -> compile ->
`#print axioms` whitelist. Every call is appended to the durable call log.

Per-tier outcome: pass rate on TRUE items (difficulty) and acceptance count
on FALSE items (must be 0; anything else is a gate failure).
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx

import build_ladder as bl

CALL_LOG = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/call_logs/hardness_ladder.jsonl")
MODELS = {
    "deepseek": "hf.co/unsloth/DeepSeek-Prover-V2-7B-GGUF:Q8_0",
    "goedel": "hf.co/mradermacher/Goedel-Prover-V2-8B-GGUF:Q6_K",
}


def prompt_for(item: dict) -> str:
    body = (bl.HEADER + item.get("extra_imports", "") + "\n" + item["defs"] + "\n\n"
            + item["statement"] + " := by\n  sorry")
    return ("Complete the following Lean 4 code. Replace `sorry` with a full proof. "
            "Do not use sorry or axioms.\n\n```lean4\n" + body + "\n```")


def generate(model: str, prompt: str) -> tuple[str, dict]:
    t0 = time.time()
    r = httpx.post("http://localhost:11434/api/chat", timeout=1200, json={
        "model": model, "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 12288, "num_predict": 4096},
        "messages": [{"role": "user", "content": prompt}],
    })
    r.raise_for_status()
    d = r.json()
    msg = d.get("message", {})
    text = (msg.get("content") or "") + "\n" + (msg.get("thinking") or "")
    rec = {"timestamp": datetime.now(timezone.utc).isoformat(), "model": model,
           "input": {"messages": [{"role": "user", "content": prompt}], "temperature": 0.0},
           "output": {"text": msg.get("content") or "", "thinking": msg.get("thinking") or "",
                      "completion_tokens": d.get("eval_count", 0)},
           "elapsed_s": round(time.time() - t0, 1)}
    CALL_LOG.parent.mkdir(parents=True, exist_ok=True)
    with CALL_LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return text, rec


def extract_proof(text: str, item: dict) -> str | None:
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text, re.DOTALL)
    for block in reversed(blocks):  # last complete answer wins
        if item["id"] in block and "sorry" not in block:
            m = re.search(re.escape(item["id"]) + r"[^\n]*?:=\s*(by\b.*|.*)", block, re.DOTALL)
            if m:
                return m.group(1).strip()
    # Fallback: model renamed the theorem. Take the proof body of the last
    # sorry-free theorem. Safe because it is compiled against OUR statement.
    for block in reversed(blocks):
        if "sorry" in block:
            continue
        m = re.search(r"(?:theorem|lemma)\s+\S+.*?:=\s*(by\b.*)", block, re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(MODELS))
    ap.add_argument("--out", default=str(bl.OUT / "baseline.json"))
    args = ap.parse_args()

    ladder = json.loads((bl.OUT / "ladder.json").read_text())
    results = {"started": datetime.now(timezone.utc).isoformat(), "n_items": len(ladder), "runs": []}
    for key in args.models:
        model = MODELS[key]
        for it in ladder:
            row = {"model": key, "id": it["id"], "tier": it["tier"], "truth": it["truth"]}
            try:
                text, rec = generate(model, prompt_for(it))
                proof = extract_proof(text, it)
                row["gen_s"] = rec["elapsed_s"]
                if proof is None:
                    row.update(extracted=False, clean=False)
                else:
                    v = bl.compile_one(bl.lean_file(it, proof), f"run_{key}_{it['id']}")
                    row.update(extracted=True, clean=v["clean"], axioms=v["axioms"], compile_s=v["secs"])
            except Exception as e:  # recorded, not hidden
                row.update(error=f"{type(e).__name__}: {e}", clean=False)
            results["runs"].append(row)
            print(json.dumps(row), flush=True)
            Path(args.out).write_text(json.dumps(results, indent=1))

    # Summary per model x tier
    summ: dict = defaultdict(lambda: {"true_n": 0, "true_pass": 0, "false_n": 0, "false_accepted": 0})
    for r in results["runs"]:
        s = summ[f"{r['model']}|{r['tier']}"]
        if r["truth"] is False:
            s["false_n"] += 1
            s["false_accepted"] += int(bool(r.get("clean")))
        else:
            s["true_n"] += 1
            s["true_pass"] += int(bool(r.get("clean")))
    results["summary"] = dict(summ)
    results["finished"] = datetime.now(timezone.utc).isoformat()
    Path(args.out).write_text(json.dumps(results, indent=1))
    print(json.dumps(results["summary"], indent=1))
    return 1 if any(s["false_accepted"] for s in summ.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
