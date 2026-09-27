#!/usr/bin/env python3
"""Overnight chain for master-math run two, one GPU job at a time.

  1. run_master.py      resume the prover run (both models)
  2. harvest.py         PASSED lake rows + DPO pairs
  3. train_prover.py --smoke   positive control: the HF-harness base must
                        prove >= 1 of 2 T0 items, else stop (suspect the
                        prompt/template, not the model)
  4. train_prover.py    full QLoRA + frozen-split base-vs-adapter gate
  5. night_training_workflow.py --models qwen_lora

Before each step: wait until MemAvailable >= the step's need (the box is
shared; a run was reaped once at 26/29 GB used). Nothing here stops other
sessions' processes or Ollama. Every step's exit code and log path go to
results/night_retrain_20260927/overnight.json.
"""

from __future__ import annotations

import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
OUT = REPO / "results" / "night_retrain_20260927"
LOG = OUT / "overnight.json"


def mem_available_gib() -> float:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 2**20
    return 0.0


def wait_mem(need_gib: float, max_wait_s: int = 6 * 3600) -> bool:
    t0 = time.time()
    while time.time() - t0 < max_wait_s:
        if mem_available_gib() >= need_gib:
            return True
        time.sleep(60)
    return False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state: dict = {"started": datetime.now(UTC).isoformat(), "steps": []}

    def step(name: str, argv: list[str], need_gib: float, timeout_s: int) -> int:
        rec: dict = {"step": name, "argv": argv[1:], "need_gib": need_gib}
        if not wait_mem(need_gib):
            rec.update(rc=None, outcome=f"BLOCKED: MemAvailable < {need_gib} GiB for 6 h")
        else:
            log = OUT / f"{name}.log"
            rec.update(start=datetime.now(UTC).isoformat(), log=str(log),
                       mem_available_gib=round(mem_available_gib(), 1))
            with log.open("a") as f:
                try:
                    rc = subprocess.run(argv, cwd=str(REPO), stdout=f, stderr=subprocess.STDOUT,
                                        timeout=timeout_s).returncode
                except subprocess.TimeoutExpired:
                    rc = -9
            rec.update(rc=rc, end=datetime.now(UTC).isoformat())
        state["steps"].append(rec)
        LOG.write_text(json.dumps(state, indent=1))
        print(json.dumps(rec), flush=True)
        return -1 if rec.get("rc") is None else rec["rc"]

    mm = REPO / "scripts" / "master_math"
    rc = step("run_master", [PY, str(mm / "run_master.py")], 8, 10 * 3600)
    if rc not in (0,):
        state["stopped"] = f"run_master rc={rc}; not harvesting a partial/failed run"
        LOG.write_text(json.dumps(state, indent=1))
        return 1
    step("harvest", [PY, str(mm / "harvest.py")], 2, 1800)
    rc = step("prover_smoke", [PY, str(mm / "train_prover.py"), "--smoke"], 14, 3 * 3600)
    smoke = REPO / "results" / "master_math_run2" / "prover_training_smoke.json"
    base_ok = False
    if rc == 0 and smoke.exists():
        base_ok = json.loads(smoke.read_text()).get("eval_base", {}).get("true_pass", 0) >= 1
    if not base_ok:
        state["stopped"] = ("prover smoke failed its positive control (base proved 0 of 2 T0 items "
                            "in the HF harness) or crashed; full prover run not started")
        LOG.write_text(json.dumps(state, indent=1))
    else:
        step("prover_full", [PY, str(mm / "train_prover.py")], 14, 8 * 3600)
    # night_training_workflow checks free VRAM once and BLOCKs; wait for Ollama
    # to hold no model first so a BLOCKED there is a real result, not timing.
    for _ in range(240):
        try:
            import httpx

            if not httpx.get("http://localhost:11434/api/ps", timeout=5).json().get("models"):
                break
        except Exception:
            break
        time.sleep(60)
    step("qwen_lora", [PY, str(REPO / "scripts" / "night_training_workflow.py"), "--models", "qwen_lora"],
         14, 3 * 3600)
    state["finished"] = datetime.now(UTC).isoformat()
    LOG.write_text(json.dumps(state, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
