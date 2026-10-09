#!/usr/bin/env python3
"""CLI: ship files to the TPU, run a command in its JAX venv, fetch results.

    AUTOEVOLVE_TPU_NAME=gwenlaya-tpu-1 AUTOEVOLVE_TPU_ZONE=us-west4-a \\
      python scripts/tpu/run_on_tpu.py --file a.py --file b.npz --result out.json --dest /tmp/out -- python a.py b.npz
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from anse.infrastructure.tpu_runner import TPUTarget, run_job  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", action="append", default=[], type=Path)
    p.add_argument("--result", action="append", default=[])
    p.add_argument("--dest", type=Path, default=Path("."))
    p.add_argument("--timeout", type=float, default=600.0)
    p.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args()
    cmd = shlex.join([c for c in args.command if c != "--"])
    if not cmd:
        p.error("no command given after --")
    out, fetched = run_job(TPUTarget.from_env(), args.file, cmd, args.result, args.dest, args.timeout)
    sys.stdout.write(out)
    for f in fetched:
        print("fetched", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
