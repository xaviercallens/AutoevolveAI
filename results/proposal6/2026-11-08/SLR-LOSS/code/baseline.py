"""E1: exact gamma of Poliakova's rules (Sec.3 9->8 and Table 1 19->17) at b=1 on base 2..2N, N=n+g.
usage: baseline.py n_lo n_hi  -> JSON lines; also writes configs (v, a, D) to certificates/baseline_*.json"""
import itertools
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "../../../2026-11-07/SLR-EXT/code"))
from gamma_fast import gamma_exact  # noqa: E402
from slr_exact import covers_open  # noqa: E402


def rule9(N, var):
    d = Fr(1, N + 1)
    vel = {2 * j: Fr(0) for j in range(1, N + 1)}
    half = (1 + d) / 2
    reph = {12: half, 24: half, 48: half if var == 0 else (1 - d) / 2, 96: half if var == 0 else (1 - d) / 2,
            16: -d, 64: -d if var == 0 else d}
    for r in (8, 32, 192):
        vel.pop(r)
    vel.update(reph)
    vel[3] = Fr(1, 4)
    vel[9] = Fr(1, 4)
    return vel


def rule19(N, sg):
    """Table 1 first rule; sg = tuple of 4 signs for the (1+-d)/2, -+d, 2d, (3+-d)/4 groups (literature sign ambiguity)."""
    d = Fr(1, N + 1)
    vel = {2 * j: Fr(0) for j in range(1, N + 1)}
    for r in (8, 32, 36, 40, 72, 180, 192, 240):
        vel.pop(r)
    for x in (12, 24, 48, 60, 96, 108, 120):
        vel[x] = (1 + sg[0] * d) / 2
    for x in (16, 64, 80):
        vel[x] = -sg[1] * d
    vel[216] = -2 * sg[2] * d
    for x in (3, 9, 27):
        vel[x] = (1 + sg[3] * d) / 4
    for x in (15, 45, 135):
        vel[x] = (3 + sg[3] * d) / 4
    return vel


def evaluate(vel, N):
    v = sorted(vel)
    D = 4 * (N + 1)
    assert all((vel[x] * D).denominator == 1 for x in v)
    a = [int((vel[x] * D) % D) for x in v]
    ok = covers_open(v, a, D, 1, N + 1)[0]  # strict open cover at 1/(N+1): expected False (tight)
    hi = Fr(1, N + 1) * Fr(1001, 1000)
    if not covers_open(v, a, D, hi.numerator, hi.denominator)[0]:
        return None
    r = gamma_exact(v, a, D, hi)
    return v, a, D, r, ok


if __name__ == "__main__":
    lo, hi_ = int(sys.argv[1]), int(sys.argv[2])
    outdir = os.path.join(HERE, "..", "certificates")
    for n in range(lo, hi_ + 1):
        res = {"n": n}
        for var in (0, 1):
            e = evaluate(rule9(n + 1, var), n + 1)
            if e and len(e[0]) == n:
                res[f"rule9_v{var}"] = {"gamma": str(e[3]["gamma"]), "float": float(e[3]["gamma"]), "ok": e[3]["ok"],
                                        "inv_gamma": float(1 / e[3]["gamma"])}
                json.dump({"n": n, "v": e[0], "a": e[1], "D": e[2], "gamma": str(e[3]["gamma"])},
                          open(os.path.join(outdir, f"baseline_rule9_v{var}_n{n:03d}.json"), "x"))
        if n + 2 >= 120:
            for sg in itertools.product((1, -1), repeat=4):
                try:
                    e = evaluate(rule19(n + 2, sg), n + 2)
                except Exception as ex:  # noqa: BLE001
                    continue
                if e and len(e[0]) == n:
                    res[f"rule19_{''.join('+' if s > 0 else '-' for s in sg)}"] = {
                        "gamma": str(e[3]["gamma"]), "float": float(e[3]["gamma"]), "ok": e[3]["ok"],
                        "inv_gamma": float(1 / e[3]["gamma"])}
                    json.dump({"n": n, "v": e[0], "a": e[1], "D": e[2], "gamma": str(e[3]["gamma"])},
                              open(os.path.join(outdir, f"baseline_rule19_{''.join('p' if s > 0 else 'm' for s in sg)}_n{n:03d}.json"), "x"))
        print(json.dumps(res), flush=True)
