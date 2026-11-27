"""Compile one Lean file in the QuantumFluids rc2 environment (qf-lake) and record the result.

Usage: python -I run_lean.py FILE.lean OUT.json
Runs the v4.34.0-rc2 `lean` binary directly with LEAN_PATH = qf-lake build + package libs + rc2 core lib,
pinned to cores 4-7 by the caller (taskset). Writes rc, stdout, stderr, wall time and the sha256 of FILE.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

QF = "/mnt/disks/disk-socrateai-local-1/leanmaster/qf-lake"
TC = "/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2"
PKGS = ["mathlib", "batteries", "Qq", "aesop", "proofwidgets", "importGraph",
        "LeanSearchClient", "plausible", "Cli"]


def main(src: str, out: str) -> int:
    roots = [QF + "/build/lib/lean"] + [QF + "/packages/" + p + "/.lake/build/lib/lean" for p in PKGS]
    roots.append(TC + "/lib/lean")
    env = dict(os.environ)
    env["LEAN_PATH"] = ":".join(roots)
    env.pop("LEAN_SRC_PATH", None)
    sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    t0 = time.time()
    p = subprocess.run([TC + "/bin/lean", src], env=env, capture_output=True, text=True)
    dt = time.time() - t0
    rec = {"file": src, "sha256": sha, "rc": p.returncode, "seconds": round(dt, 1),
           "stdout": p.stdout, "stderr": p.stderr, "lean": TC + "/bin/lean", "LEAN_PATH": roots}
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print("rc", p.returncode, "seconds", round(dt, 1))
    print(p.stdout[-6000:])
    print(p.stderr[-2000:])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
