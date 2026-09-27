#!/usr/bin/env python3
"""Run the provers over the validated master-math ladder; the kernel decides.

Round 0 is the same greedy attempt as the hardness baseline
(`scripts/hardness/run_ladder.py`: same models, prompt shape, extraction and
gate). Round 1 -- the new measurement -- feeds the Lean error messages of a
failed round-0 attempt back to the same model once. False items get the same
treatment: any clean proof of a false item is a gate failure (exit 1).

Every attempt keeps its proof text and compile errors, so kernel-verified
failures can be paired with successes (DPO) and quoted in the paper.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # repo root: `scripts.*` packages
sys.path.insert(0, str(HERE.parent / "hardness"))  # run_ladder's own flat import

from scripts.hardness import run_ladder as rl  # noqa: E402

bl = rl.bl  # one build_ladder module object, shared with run_ladder

OUT_DIR = HERE.parents[1] / "results" / "master_math_run2"
rl.CALL_LOG = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/call_logs/master_math_run2.jsonl")


def repair_prompt(item: dict, proof: str | None, errors: str) -> str:
    """Round-1 prompt: the original task plus the failed attempt and Lean's errors."""
    if proof is None:
        feedback = ("Your previous answer contained no complete, sorry-free Lean 4 code block "
                    "for this theorem.")
    else:
        feedback = ("Your previous attempt was:\n```lean4\n" + bl.lean_file(item, proof)
                    + "```\nLean 4 rejected it with:\n```\n" + (errors or "(no error text)")
                    + "\n```")
    return (rl.prompt_for(item) + "\n\n" + feedback
            + "\nWrite a corrected, complete proof of exactly this statement.")


def attempt(model_key: str, item: dict, prompt: str, rnd: int) -> dict:
    text, rec = rl.generate(rl.MODELS[model_key], prompt)
    proof = rl.extract_proof(text, item)
    row = {"model": model_key, "id": item["id"], "tier": item["tier"], "truth": item["truth"],
           "round": rnd, "gen_s": rec["elapsed_s"], "tokens": rec["output"]["completion_tokens"],
           "proof": proof}
    if proof is None:
        row.update(extracted=False, clean=False, errors="")
    else:
        v = bl.compile_one(bl.lean_file(item, proof), f"mm_{model_key}_{item['id']}_r{rnd}")
        row.update(extracted=True, clean=v["clean"], axioms=v["axioms"], rc=v["rc"],
                   axioms_printed=v["axioms_printed"], compile_s=v["secs"], errors=v["errors"])
    return row


def summarize(runs: list[dict]) -> dict:
    s: dict = defaultdict(lambda: {"true_n": 0, "pass_r0": 0, "pass_r1": 0,
                                   "false_n": 0, "false_accepted": 0})
    final: dict = {}
    for r in runs:
        final.setdefault((r["model"], r["id"]), {})[r["round"]] = r
    for (model, _), by_round in final.items():
        r0 = by_round.get(0)
        if r0 is None:
            continue
        agg = s[model]
        solved = any(x.get("clean") for x in by_round.values())
        if r0["truth"] is False:
            agg["false_n"] += 1
            agg["false_accepted"] += int(solved)
        else:
            agg["true_n"] += 1
            agg["pass_r0"] += int(bool(r0.get("clean")))
            agg["pass_r1"] += int(solved)
    return dict(s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(rl.MODELS))
    ap.add_argument("--ladder", default=str(OUT_DIR / "ladder.json"))
    ap.add_argument("--out", default=str(OUT_DIR / "runs.json"))
    ap.add_argument("--repair-rounds", type=int, default=1, choices=[0, 1])
    args = ap.parse_args()

    ladder = json.loads(Path(args.ladder).read_text())
    out = Path(args.out)
    results = {"started": datetime.now(UTC).isoformat(), "n_items": len(ladder),
               "repair_rounds": args.repair_rounds, "runs": []}
    if out.exists():  # resume: keep rows that really ran
        results["runs"] = [r for r in json.loads(out.read_text()).get("runs", []) if "error" not in r]
    done = {(r["model"], r["id"], r["round"]) for r in results["runs"]}

    if not rl.acquire_gpu_lease(f"master-math run two ({','.join(args.models)})"):
        return 2
    try:
        for key in args.models:
            for it in ladder:
                prev0 = next((r for r in results["runs"]
                              if (r["model"], r["id"], r["round"]) == (key, it["id"], 0)), None)
                for rnd in range(args.repair_rounds + 1):
                    if (key, it["id"], rnd) in done:
                        continue
                    if rnd == 1 and (prev0 is None or prev0.get("clean")):
                        continue  # repair only after a real round-0 failure
                    if not rl.wait_for_server():
                        print("ABORT: Ollama unavailable; rerun to resume", flush=True)
                        return 2
                    rl.wait_and_acquire(rl.LEASE_HOLDER, "master-math (renew)", ttl_s=1800, timeout_s=60)
                    prompt = (rl.prompt_for(it) if rnd == 0
                              else repair_prompt(it, prev0.get("proof"), prev0.get("errors", "")))
                    try:
                        row = attempt(key, it, prompt, rnd)
                    except Exception as e:  # infrastructure, not a prover verdict
                        row = {"model": key, "id": it["id"], "tier": it["tier"], "truth": it["truth"],
                               "round": rnd, "error": f"{type(e).__name__}: {e}", "clean": False}
                    results["runs"].append(row)
                    if rnd == 0:
                        prev0 = row
                    print(json.dumps({k: row.get(k) for k in
                                      ("model", "id", "round", "clean", "extracted", "gen_s", "error")}),
                          flush=True)
                    out.write_text(json.dumps(results, indent=1))
    finally:
        rl.lease_release(rl.LEASE_HOLDER)

    results["summary"] = summarize(results["runs"])
    results["finished"] = datetime.now(UTC).isoformat()
    out.write_text(json.dumps(results, indent=1))
    print(json.dumps(results["summary"], indent=1))
    return 1 if any(v["false_accepted"] for v in results["summary"].values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
