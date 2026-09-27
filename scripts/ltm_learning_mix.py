#!/usr/bin/env python3
"""Build ANSE's next training mix from long-term memory, with dilution control.

Sources
  verified   data/episodes/harvest.jsonl        (episodes with real verdicts)
  new        call_logs/*.jsonl                  (every logged LLM call; prover
             bake-off rows carry a kernel verdict, plain calls carry none)

Dilution: at most ``--dilution`` of the final mix may come from the *new*
pool. The ratio guards against catastrophic forgetting: verified prior
episodes anchor the distribution, fresh (partly unverified) signal is folded
in gradually. If the verified pool is too small to honour the ratio, this
script exits BLOCKED — it never silently inverts the mix.

Output rows carry provenance: {source, verified, verdict, sha}. The night
trainer (scripts/night_training_workflow.py DATA step) can consume the file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CALL_LOGS = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/call_logs")
EPISODES = REPO / "data" / "episodes" / "harvest.jsonl"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def load_verified() -> list[dict]:
    rows = []
    if EPISODES.exists():
        for line in EPISODES.open():
            if not line.strip():
                continue
            ep = json.loads(line)
            rows.append({
                "source": "episodes/harvest.jsonl",
                "verified": True,
                "verdict": bool(ep.get("converged")),
                "prompt": ep.get("prompt", ""),
                "completion": ep.get("code", ""),
                "sha": sha(line),
            })
    return rows


def load_new() -> list[dict]:
    rows = []
    for f in sorted(CALL_LOGS.glob("*.jsonl")):
        for line in f.open():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msgs = rec.get("input", {}).get("messages") or []
            prompt = " ".join(m.get("content", "") for m in msgs) or rec.get("input", {}).get("prompt", "")
            rows.append({
                "source": f"call_logs/{f.name}",
                "verified": False,
                "verdict": None,  # a later join with bakeoff results may set this
                "prompt": prompt,
                "completion": rec.get("output", {}).get("text", ""),
                "sha": sha(line),
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dilution", type=float, default=0.3,
                    help="max fraction of the mix drawn from the NEW pool (default 0.3)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=REPO / "data" / "training" / "ltm_mix.jsonl")
    args = ap.parse_args()

    if not 0.0 <= args.dilution <= 0.5:
        print(f"BLOCKED: dilution {args.dilution} outside [0, 0.5]; the verified pool must dominate")
        return 1

    verified = load_verified()
    new = load_new()
    rng = random.Random(args.seed)

    if not verified:
        print("BLOCKED: no verified episodes on disk; refusing to train on unverified calls alone")
        return 1

    # Mix size is anchored by the verified pool: it always enters whole.
    max_new = int(len(verified) * args.dilution / max(1e-9, 1.0 - args.dilution))
    take_new = min(max_new, len(new))
    mix = verified + rng.sample(new, take_new)
    rng.shuffle(mix)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for row in mix:
            f.write(json.dumps(row) + "\n")

    frac = take_new / len(mix) if mix else 0.0
    print(json.dumps({
        "written": str(args.out),
        "rows": len(mix),
        "verified_rows": len(verified),
        "new_rows_taken": take_new,
        "new_pool_available": len(new),
        "effective_dilution": round(frac, 3),
        "dilution_cap": args.dilution,
        "at": datetime.now(UTC).isoformat(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
