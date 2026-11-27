"""Paper-stage rerun of the qf-yukawa-crystal crate tests and the keldysh_jellium scan (cores 4-7, 2 jobs).

Writes stdout/stderr and return codes to rerun_cargo.json next to this file. Not the producer's run.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

WT = "/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h3"
TGT = "/home/callensxavier_gmail_com/rusty-target-ar"
OUT = Path(__file__).resolve().parent / "rerun_cargo.json"


def run(cmd: list[str]) -> dict[str, object]:
    env = dict(os.environ, CARGO_TARGET_DIR=TGT)
    t0 = time.time()
    r = subprocess.run(["taskset", "-c", "4-7", *cmd], env=env, capture_output=True, text=True, timeout=1700)
    return {"cmd": cmd, "rc": r.returncode, "seconds": round(time.time() - t0, 1),
            "stdout_tail": r.stdout[-6000:], "stderr_tail": r.stderr[-3000:]}


def main() -> None:
    res: dict[str, object] = {}
    res["test"] = run(["cargo", "test", "--release", "-j", "2", "--offline", "--manifest-path", WT + "/Cargo.toml",
                       "-p", "qf-yukawa-crystal", "--", "--test-threads=2"])
    scan_out = str(Path(__file__).resolve().parent / "rerun_scan.json")
    res["scan"] = run([TGT + "/release/keldysh_jellium", "scan", scan_out])
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v["rc"] for k, v in res.items()}))


if __name__ == "__main__":
    main()
