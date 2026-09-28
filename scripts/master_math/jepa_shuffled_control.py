#!/usr/bin/env python3
"""JEPA learning check (LL.md §12d rule): train on the real verified traces and
on the same rows with `energy` shuffled across rows, then compare. Also
extracts the numbers from both training logs into a committed JSON, since
the logs themselves are gitignored.

  --build      write the shuffled-energy data file only
  --summarize  parse the two logs into results/night_retrain_20260927/jepa.json
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCES = [REPO / "results/phase1_evolution" / f"{n}.jsonl"
           for n in ("traces_uc2_verified", "traces_uc2_adaptive", "traces_uc4_memory")]
SHUFFLED = REPO / ".scratchpad" / "jepa_shuffled.jsonl"
LOGS = {"real": REPO / "results/night_retrain_20260927/jepa_train.log",
        "shuffled_control": REPO / "results/night_retrain_20260927/jepa_shuffled_control.log"}


def build(seed: int = 7) -> int:
    rows = [json.loads(line) for p in SOURCES for line in p.read_text().splitlines() if line.strip()]
    energies = [r.get("energy") for r in rows]
    random.Random(seed).shuffle(energies)
    for r, e in zip(rows, energies, strict=True):
        r["energy"] = e
    SHUFFLED.parent.mkdir(parents=True, exist_ok=True)
    SHUFFLED.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return len(rows)


def summarize() -> dict:
    out: dict = {"data": [str(p.relative_to(REPO)) for p in SOURCES], "shuffle_seed": 7}
    for arm, log in LOGS.items():
        text = log.read_text()
        best = re.search(r"best val loss: ([0-9.]+)", text)
        epochs = re.findall(r"Epoch (\d+)/\d+ \| Train Loss: ([0-9.]+) \| Val Loss: ([0-9.]+) \| Energy Acc: ([0-9.]+)%", text)
        first, last = epochs[0], epochs[-1]
        out[arm] = {"best_val_loss": float(best.group(1)) if best else None,
                    "epoch1": {"train": float(first[1]), "val": float(first[2]), "energy_acc_pct": float(first[3])},
                    "final": {"epoch": int(last[0]), "train": float(last[1]), "val": float(last[2]),
                              "energy_acc_pct": float(last[3])}}
    out["verdict"] = ("no evidence of learning: real-label best val loss is not below the shuffled control's"
                      if out["real"]["best_val_loss"] >= out["shuffled_control"]["best_val_loss"]
                      else "real labels beat the shuffled control on best val loss")
    path = REPO / "results/night_retrain_20260927/jepa.json"
    path.write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    if "--build" in sys.argv:
        print(build())
    else:
        print(json.dumps(summarize(), indent=1))
