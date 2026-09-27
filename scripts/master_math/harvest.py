#!/usr/bin/env python3
"""Turn the master-math run's kernel verdicts into training signal.

  SFT rows   kernel-clean proofs *written by the local provers* on TRUE items,
             appended to the lake corpus the trainer reads
             (`verdict: PASSED` + provenance), idempotently.
  DPO pairs  (clean, failed) attempts on the same TRUE item -- the failures
             are kernel-verified, which is what makes them discriminative.

Never used: false items, and the hand-written reference proofs (the controls;
using frontier-model output as SFT targets is an open terms-of-use decision
for the user, not something this script settles).

Every row is checked against the frozen hardness split with the same
whitespace-normalized proposition match the trainer applies; a leak aborts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))  # repo root: `scripts.*` packages
sys.path.insert(0, str(REPO / "scripts" / "hardness"))  # run_ladder's own flat import

from scripts.hardness import run_ladder as rl  # noqa: E402

RUN_DIR = REPO / "results" / "master_math_run2"
LAKE = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/data")
SFT_PATH = LAKE / "redis" / "redis_ltm_lora_dataset.jsonl"
DPO_PATH = LAKE / "dpo" / "master_math_run2_dpo.jsonl"


def frozen_props() -> list[str]:
    split = json.loads((REPO / "results" / "hardness" / "frozen_split.json").read_text())
    return [f["prop"] for f in split]


def leaks(row: dict, props: list[str]) -> bool:
    text = " ".join(" ".join(str(row.get(k, "")) for k in ("prompt", "completion", "chosen", "rejected")).split())
    return any(p in text for p in props)


def build(runs: list[dict], ladder: list[dict], run_id: str) -> tuple[list[dict], list[dict]]:
    items = {it["id"]: it for it in ladder if it["truth"] is True}
    sft: list[dict] = []
    dpo: list[dict] = []
    for iid, item in items.items():
        attempts = [r for r in runs if r["id"] == iid and "error" not in r]
        good = [r for r in attempts if r.get("clean") and r.get("proof")]
        bad = [r for r in attempts if not r.get("clean") and r.get("proof")]
        prompt = rl.prompt_for(item)
        seen: set[str] = set()
        for g in good:
            if g["proof"] in seen:
                continue
            seen.add(g["proof"])
            sft.append({
                "prompt": prompt, "completion": g["proof"], "verdict": "PASSED", "task": iid,
                "provenance": (f"master_math_run2 {run_id}: {g['model']} round {g['round']}, "
                               f"kernel gate rc=0, axioms {g.get('axioms')}, statement locked in "
                               f"scripts/master_math/problems.py"),
            })
        for g in good[:1]:
            for b in bad:
                dpo.append({
                    "prompt": prompt, "chosen": g["proof"], "rejected": b["proof"], "task": iid,
                    "provenance": (f"master_math_run2 {run_id}: chosen {g['model']} r{g['round']} "
                                   f"clean; rejected {b['model']} r{b['round']} kernel-rejected "
                                   f"(rc={b.get('rc')})"),
                    "rejected_errors": (b.get("errors") or "")[:600],
                })
    return sft, dpo


def append_new(path: Path, rows: list[dict], key: tuple[str, ...]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    have: set[str] = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            have.add(hashlib.sha256("|".join(str(r.get(k, "")) for k in key).encode()).hexdigest())
    new = [r for r in rows
           if hashlib.sha256("|".join(str(r.get(k, "")) for k in key).encode()).hexdigest() not in have]
    with path.open("a") as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(new)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run = json.loads((RUN_DIR / "runs.json").read_text())
    ladder = json.loads((RUN_DIR / "ladder.json").read_text())
    sft, dpo = build(run["runs"], ladder, run.get("started", "?"))
    props = frozen_props()
    leaked = [r["task"] for r in sft + dpo if leaks(r, props)]
    report = {"sft_rows": len(sft), "dpo_pairs": len(dpo), "frozen_split_leaks": leaked,
              "sft_tasks": sorted({r["task"] for r in sft}), "dpo_tasks": sorted({r["task"] for r in dpo})}
    if leaked:
        print(json.dumps(report, indent=1))
        print("ABORT: frozen-split leak")
        return 1
    (RUN_DIR / "dpo_pairs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dpo))
    (RUN_DIR / "sft_rows.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sft))
    if not args.dry_run:
        report["sft_appended"] = append_new(SFT_PATH, sft, ("task", "completion"))
        report["dpo_appended"] = append_new(DPO_PATH, dpo, ("task", "chosen", "rejected"))
    (RUN_DIR / "harvest_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
