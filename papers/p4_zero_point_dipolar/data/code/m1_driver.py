"""M1 driver: runs the certifier jobs one after another (one process at a time, on the core this driver is pinned to).

usage: python -I m1_driver.py M1_DIR JOBSET
  JOBSET controls  : positive / negative controls (N2 settings) + the riesz3direct tail-lemma control
  JOBSET main      : Riesz 3, dipolar d = 1/10, 1/2
  JOBSET extra     : dipolar at d/a = 0.06, 0.09 (d = 129/2000, 967/10000; a = sqrt(2/sqrt3))
Skips a job whose output JSON already exists.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"

JOBS = {
    "controls": [
        ("ctl_gauss1", ["gauss", "1", "64", "1/100000", "21"], {"N2_MAX_DEPTH": "1", "N2_REFINE_TOL": "0.5"}),
        ("negctl_gauss2", ["gauss", "2", "64", "1/100000", "21"], {"N2_MAX_DEPTH": "1", "N2_REFINE_TOL": "0.5"}),
        ("ctl_yukawa2", ["yukawa", "2", "64", "1/100000", "150"], {"N2_MAX_DEPTH": "1", "N2_REFINE_TOL": "0.5"}),
        ("negctl_riesz3direct", ["riesz3direct", "x", "64", "1/100000", "300"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
        ("ctl_yukawa1", ["yukawa", "1", "64", "1/100000", "650"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "1.0"}),
    ],
    "main": [
        ("riesz3", ["riesz3", "x", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
        ("dipolar_d0.1", ["dipolar", "1/10", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
        ("dipolar_d0.5", ["dipolar", "1/2", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
    ],
    "extra": [
        ("dipolar_da0.06", ["dipolar", "129/2000", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
        ("dipolar_da0.09", ["dipolar", "967/10000", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
    ],
}


JOBS["prereg"] = [  # preregistered d/a = 0.1 and 0.5 exactly (a = sqrt(2/sqrt3)): d = 1075/10000, 5373/10000
    ("dipolar_da0.1", ["dipolar", "1075/10000", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
    ("dipolar_da0.5", ["dipolar", "5373/10000", "64", "1/100000", "300", "1/10"], {"N2_MAX_DEPTH": "2", "N2_REFINE_TOL": "0.5"}),
]
JOBS["all"] =JOBS["controls"] + JOBS["main"] + JOBS["extra"]


def main() -> None:
    m1, jobset = sys.argv[1], sys.argv[2]
    cert = os.path.join(m1, "code", "m1_certify.py")
    status = []
    for name, args, env in JOBS[jobset]:
        out = os.path.join(m1, "data", f"{name}.json")
        if os.path.exists(out):
            status.append({"job": name, "skipped": "exists"})
            continue
        log = os.path.join(m1, "logs", f"{name}.log")
        t0 = time.time()
        with open(log, "w") as fh:
            p = subprocess.run([PY, "-I", cert] + args[:5] + [out] + args[5:], env=dict(os.environ, **env),
                               stdout=fh, stderr=subprocess.STDOUT)
        status.append({"job": name, "rc": p.returncode, "seconds": round(time.time() - t0, 1), "env": env, "args": args})
        with open(os.path.join(m1, "logs", f"driver_{jobset}.json"), "w") as fh:
            json.dump(status, fh, indent=1)
    with open(os.path.join(m1, "logs", f"driver_{jobset}.json"), "w") as fh:
        json.dump(status + [{"done": True}], fh, indent=1)


if __name__ == "__main__":
    main()
