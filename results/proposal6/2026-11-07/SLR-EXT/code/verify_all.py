"""Re-verify every certificate with both checkers from the stored JSON only, plus the
perturbation negative control (N2) on selected certificates.  Writes a JSON summary."""
from __future__ import annotations

import glob
import hashlib
import json
import os
import subprocess
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slr_exact import covers_open  # noqa: E402

C = os.path.join(HERE, "check_cover")
ROOT = os.path.dirname(HERE)


def sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(path: str) -> tuple[bool, bool, str]:
    c = json.load(open(path))
    v, a, D = c["v"], c["a"], c["D"]
    dp, dq = c["delta_num"], c["delta_den"]
    n = c["n"]
    assert len(v) == n == len(a) and len(set(v)) == n and min(v) >= 1
    assert Fraction(dp, dq) == Fraction(1, n + 1), "delta must be 1/(n+1)"
    ok1 = covers_open(v, a, D, dp, dq)[0]
    r = subprocess.run([C, path], capture_output=True, text=True)
    return ok1, r.returncode == 0, r.stdout.strip()


def perturb(path: str, tmp: str) -> dict:
    c = json.load(open(path))
    v, a, D, n = c["v"], c["a"], c["D"], c["n"]
    S = sum(v)
    D2 = D * 10 * S
    base = [x * 10 * S for x in a]
    rows = []
    for i in range(n):
        for sg in (1, -1):
            aa = list(base)
            aa[i] = (aa[i] + sg * D) % D2
            ok1 = covers_open(v, aa, D2, 1, n + 1)[0]
            with open(tmp, "w") as fh:
                json.dump({"n": n, "v": v, "a": aa, "D": D2, "delta_num": 1, "delta_den": n + 1}, fh)
            ok2 = subprocess.run([C, tmp], capture_output=True).returncode == 0
            rows.append((i, sg, ok1, ok2))
    os.remove(tmp)
    return {"cert": os.path.basename(path), "perturbations": len(rows),
            "broken_both": sum(1 for r in rows if not r[2] and not r[3]),
            "disagree": sum(1 for r in rows if r[2] != r[3])}


def main() -> None:
    sel = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else []
    out = {"certificates": [], "perturbation_control": []}
    t0 = time.process_time()
    for p in sorted(glob.glob(os.path.join(ROOT, "certificates", "cert_n*.json"))):
        ok1, ok2, msg = check(p)
        c = json.load(open(p))
        out["certificates"].append({"file": os.path.basename(p), "n": c["n"], "D": c["D"],
                                    "checker1": ok1, "checker2": ok2, "checker2_msg": msg, "sha256": sha(p)})
    for n in sel:
        p = os.path.join(ROOT, "certificates", f"cert_n{n:03d}.json")
        if os.path.exists(p):
            out["perturbation_control"].append(perturb(p, os.path.join(ROOT, "controls", "pert_tmp.json")))
    out["cpu_s"] = time.process_time() - t0
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
