"""Non-rigorous cross-check: scipy Radau at tight tolerances (two settings) on the full 3-D Robertson system."""
import json, sys
import numpy as np
from scipy.integrate import solve_ivp


def f(t, y):
    return [-0.04 * y[0] + 1e4 * y[1] * y[2], 0.04 * y[0] - 1e4 * y[1] * y[2] - 3e7 * y[1] ** 2, 3e7 * y[1] ** 2]


def jac(t, y):
    return [[-0.04, 1e4 * y[2], 1e4 * y[1]], [0.04, -1e4 * y[2] - 6e7 * y[1], -1e4 * y[1]], [0, 6e7 * y[1], 0]]


T = [1.0, 10.0, 40.0, 1000.0, 4000.0]
out = {}
for rt, at in [(1e-12, 1e-20), (1e-13, 1e-22)]:
    s = solve_ivp(f, (0, 4000), [1.0, 0.0, 0.0], method="Radau", jac=jac, rtol=rt, atol=at, t_eval=T, dense_output=False)
    out[f"{rt:g}"] = {str(t): list(map(float, s.y[:, i])) for i, t in enumerate(s.t)}
    print(rt, s.status, s.nfev, flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
