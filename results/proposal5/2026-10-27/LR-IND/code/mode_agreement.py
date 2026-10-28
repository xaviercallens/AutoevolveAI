#!/usr/bin/env python3
"""Cross-check the three phase-1 enumeration modes of lr_sieve (plain hitting-set DFS, + capacity bound,
+ canonical-support pruning): every level's set of classes mod p (count and hash) must agree."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIN = str(HERE / "lr_sieve")

CASES: list[tuple[int, list[int], str]] = [
    (5, [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43], "2,2,/"),
    (6, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53], "7"),
    (7, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61], "2,2,2"),
    (8, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73], "3,3"),
    (10, [127, 131], "2,2,2,/"),
]


def run(k: int, p: int, plan: str, bound: int, canon: int) -> dict[str, object]:
    out = subprocess.run(["taskset", "-c", "2", BIN, str(k), str(p), plan, "0", str(bound), str(canon)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> int:
    log = open(HERE.parent / "logs" / "mode_agreement.jsonl", "w")
    bad = 0
    for k, ps, plan in CASES:
        for p in ps:
            modes = [(1, 1), (1, 0), (0, 0)]
            sig = {}
            for b, c in modes:
                d = run(k, p, plan, b, c)
                sig[(b, c)] = (d["S1"]["classes"], d["S1"]["class_hash"],
                               tuple((s["classes_mod_p"], s["class_hash"]) for s in d["steps"]), d["final_classes"])
                log.write(json.dumps({"k": k, "p": p, "bound": b, "canon": c, "S1": d["S1"],
                                      "phase1": d["phase1"], "steps": d["steps"],
                                      "final_classes": d["final_classes"]}) + "\n")
            ok = len(set(sig.values())) == 1
            bad += not ok
            print(k, p, "AGREE" if ok else "DISAGREE", {m: (v[0], v[3]) for m, v in sig.items()}, flush=True)
    print("disagreements", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
