"""Compile one Lean file in the QuantumFluids rc2 environment (H7/H8 recipe) and record the output.

Usage: python -I run_lean_rc2.py FILE.lean OUT.json
LEAN_PATH = qf-lake build/lib/lean + packages/*/.lake/build/lib/lean + rc2 lib/lean.
Pinned to cores 4-7, timeout 1800 s.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

QF = "/mnt/disks/disk-socrateai-local-1/leanmaster/qf-lake"
TC = "/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2"


def main(src: str, out: str) -> None:
    paths = [QF + "/build/lib/lean"]
    paths += sorted(glob.glob(QF + "/packages/*/.lake/build/lib/lean"))
    paths.append(TC + "/lib/lean")
    env = dict(os.environ)
    env["LEAN_PATH"] = ":".join(paths)
    cmd = ["taskset", "-c", "4-7", TC + "/bin/lean", src]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1800)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = 124, str(e.stdout or ""), str(e.stderr or "")
    dt = time.time() - t0
    sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    res = {"file": src, "sha256": sha, "rc": rc, "seconds": round(dt, 1), "started_unix": int(t0),
           "lean": TC + "/bin/lean", "LEAN_PATH": paths, "stdout": so, "stderr": se}
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2)
    print("rc", rc, "seconds", round(dt, 1), "sha256", sha)
    print(so[-6000:])
    print(se[-2000:])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
