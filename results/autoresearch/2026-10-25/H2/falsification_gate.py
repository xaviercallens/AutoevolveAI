"""H2 numeric falsification gate: signs of (-1)^n d^n g/dt^n, n<=8, on a grid (mpmath, high precision)."""
import json
from typing import Callable

import mpmath as mp

mp.mp.dps = 40


def check(f: Callable, label: str, kappas: list, ts: list, nmax: int = 8) -> dict:
    bad = []
    for k in kappas:
        for t in ts:
            for n in range(nmax + 1):
                v = (-1) ** n * mp.diff(lambda x: f(x, k), t, n)
                if v < 0:
                    bad.append({"kappa": float(k), "t": float(t), "n": n, "val": mp.nstr(v, 8)})
    return {"label": label, "checked": len(kappas) * len(ts) * (nmax + 1), "violations": len(bad), "first": bad[:3]}


kap = [mp.mpf("0.1"), mp.mpf(1), mp.mpf(5)]
ts = [mp.mpf(x) for x in ["0.01", "0.1", "0.5", "1", "2", "5", "10", "30"]]
out = [
    check(lambda t, k: mp.exp(-k * mp.sqrt(t)) / mp.sqrt(t), "yukawa g", kap, ts),
    check(lambda t, k: mp.exp(-k * mp.sqrt(t)), "phi=exp(-k sqrt t)", kap, ts),
    check(lambda t, k: mp.exp(-k * mp.sqrt(t)) * mp.cos(t), "NEG ctl exp(-k sqrt t) cos t", kap, ts),
    check(lambda t, k: mp.exp(-k * t ** 2), "NEG ctl exp(-k t^2)", kap, ts),
]
print(json.dumps(out, indent=1))
