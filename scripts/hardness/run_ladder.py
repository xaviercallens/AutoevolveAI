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
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import build_ladder as bl
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")
from gpu_lease import release as lease_release  # noqa: E402
from gpu_lease import wait_and_acquire  # noqa: E402

LEASE_HOLDER = "autoevolveai"
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


def wait_for_server(max_wait_s: int = 3600) -> bool:
    """Block until Ollama answers. The T4 is shared: other sessions stop Ollama
    to free the GPU (seen 2026-09-27), and a runner that keeps going logs a
    wall of instant ConnectErrors that measure nothing. We never start Ollama
    ourselves -- whoever stopped it may still need the card."""
    t0 = time.time()
    while time.time() - t0 < max_wait_s:
        try:
            httpx.get("http://localhost:11434/api/tags", timeout=5).raise_for_status()
            return True
        except Exception:
            time.sleep(30)
    return False


def acquire_gpu_lease(purpose: str, timeout_s: int = 3600) -> bool:
    """Hold the shared T4 lease (/mnt/disks/disk-socrateai-local-1/gpu_lease)
    for the run's duration. Fixes the actual root cause of 2026-09-27's
    112 wasted rows: a runux-ai-runtime session stopped Ollama mid-baseline
    with no coordination. This does not make Ollama itself exclusive-aware --
    it only stops OUR side from racing a concurrent GPU job, and other jobs
    must adopt the same lease for it to protect anyone."""
    print(f"Waiting for shared T4 lease (holder={LEASE_HOLDER})...", flush=True)
    ok = wait_and_acquire(LEASE_HOLDER, purpose, ttl_s=1800, timeout_s=timeout_s)
    if ok:
        print("Lease acquired.", flush=True)
    else:
        print(f"Could not acquire GPU lease within {timeout_s}s.", flush=True)
    return ok


def generate(model: str, prompt: str, temperature: float = 0.0) -> tuple[str, dict]:
    t0 = time.time()
    r = httpx.post("http://localhost:11434/api/chat", timeout=1200, json={
        "model": model, "stream": False,
        "options": {"temperature": temperature, "num_ctx": 12288, "num_predict": 4096},
        "messages": [{"role": "user", "content": prompt}],
    })
    r.raise_for_status()
    d = r.json()
    msg = d.get("message", {})
    text = (msg.get("content") or "") + "\n" + (msg.get("thinking") or "")
    rec = {"timestamp": datetime.now(UTC).isoformat(), "model": model,
           "input": {"messages": [{"role": "user", "content": prompt}], "temperature": temperature},
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
    ap.add_argument("--split", choices=["all", "frozen"], default="all",
                    help="frozen = only items in results/hardness/frozen_split.json (P4-5 gate)")
    ap.add_argument("--samples", type=int, default=1, help="attempts per item (pass@k needs k)")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--tag", action="append", default=[], metavar="KEY=OLLAMA_TAG",
                    help="register an extra arm, e.g. deepseek-adapter=my-adapter:latest")
    ap.add_argument("--emit-heldout", default=None, metavar="PATH",
                    help="write the gate's candidate eval (heldout_eval.json) for the one model run")
    ap.add_argument("--prover", default=None,
                    help="base prover key the candidate is compared against (with --emit-heldout)")
    args = ap.parse_args()
    for kv in args.tag:
        key, _, tag = kv.partition("=")
        if not key or not tag:
            ap.error(f"--tag expects KEY=OLLAMA_TAG, got {kv!r}")
        MODELS[key] = tag
    unknown = [m for m in args.models if m not in MODELS]
    if unknown:
        ap.error(f"unknown model key(s) {unknown}; known: {sorted(MODELS)}")
    if args.samples < 1:
        ap.error("--samples must be >= 1")
    if args.samples > 1 and args.temperature <= 0.0:
        # Greedy decoding returns the same text every time: pass@k would equal
        # pass@1 by construction, a k that cannot vary.
        ap.error("--samples > 1 needs --temperature > 0")
    if args.emit_heldout and (len(args.models) != 1 or not args.prover):
        ap.error("--emit-heldout needs exactly one model in --models and --prover")

    ladder = json.loads((bl.OUT / "ladder.json").read_text())
    if args.split == "frozen":
        frozen = {str(f["id"]) for f in json.loads((bl.OUT / "frozen_split.json").read_text())}
        ladder = [it for it in ladder if it["id"] in frozen]
        if not ladder:
            print("BLOCKED: frozen split selects no ladder items", flush=True)
            return 2
    results = {"started": datetime.now(UTC).isoformat(), "n_items": len(ladder), "runs": []}
    # Resume: keep rows that actually ran (no infrastructure error).
    prev = Path(args.out)
    if prev.exists():
        old = json.loads(prev.read_text())
        results["runs"] = [r for r in old.get("runs", []) if "error" not in r]
    done = {(r["model"], r["id"], r.get("sample", 0)) for r in results["runs"]}

    if not acquire_gpu_lease(f"hardness ladder ({','.join(args.models)})"):
        return 2
    try:
        return _run(args, ladder, results, done)
    finally:
        lease_release(LEASE_HOLDER)


def _run(args, ladder: list[dict], results: dict, done: set) -> int:
    for key in args.models:
        model = MODELS[key]
        for it, sample in ((it, j) for it in ladder for j in range(args.samples)):
            if (key, it["id"], sample) in done:
                continue
            row = {"model": key, "id": it["id"], "tier": it["tier"], "truth": it["truth"],
                   "sample": sample, "temperature": args.temperature}
            if not wait_for_server():
                print("ABORT: Ollama unavailable for 60 min; rerun to resume", flush=True)
                Path(args.out).write_text(json.dumps(results, indent=1))
                return 2
            # Renew: a long ladder run can outlive the lease's 30-min TTL.
            wait_and_acquire(LEASE_HOLDER, "hardness ladder (renew)", ttl_s=1800, timeout_s=60)
            try:
                text, rec = generate(model, prompt_for(it), args.temperature)
                proof = extract_proof(text, it)
                row["gen_s"] = rec["elapsed_s"]
                if proof is None:
                    row.update(extracted=False, clean=False)
                else:
                    v = bl.compile_one(bl.lean_file(it, proof), f"run_{key}_{it['id']}")
                    row.update(extracted=True, clean=v["clean"], axioms=v["axioms"], compile_s=v["secs"])
            except Exception as e:
                # Recorded, not hidden; error rows are dropped on resume and
                # the item retried (a dead server is not a prover failure).
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
    results["finished"] = datetime.now(UTC).isoformat()
    Path(args.out).write_text(json.dumps(results, indent=1))
    print(json.dumps(results["summary"], indent=1))
    if args.emit_heldout:
        from anse.v2 import heldout_eval
        doc = heldout_eval.build_candidate_eval(
            Path(args.out), bl.OUT / "frozen_split.json", args.samples,
            prover=args.prover, arm=args.models[0], tag=MODELS[args.models[0]],
        )
        Path(args.emit_heldout).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.emit_heldout}", flush=True)
    return 1 if any(s["false_accepted"] for s in summ.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
