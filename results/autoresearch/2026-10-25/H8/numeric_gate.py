"""H8 numeric falsification gate: S_B(x) = x/sqrt(1+x^2) vs sqrt(x/2), x = k/k*."""
import json
import math
import sys


def gate(n: int = 200000, xmax: float = 100.0) -> dict:
    viol = 0
    best = (0.0, 0.0)
    for i in range(1, n + 1):
        x = xmax * i / n
        s = x / math.sqrt(1.0 + x * x)
        b = math.sqrt(x / 2.0)
        r = s / b
        if r > best[0]:
            best = (r, x)
        if s > b * (1 + 1e-12):
            viol += 1
    # small-x region separately (log grid)
    for j in range(-12, 1):
        x = 10.0 ** j
        if x / math.sqrt(1 + x * x) > math.sqrt(x / 2) * (1 + 1e-12):
            viol += 1
    # negative control: free particle / ideal gas S = 1, x on (0, 2)
    neg_free = sum(1 for i in range(1, 1000) if 1.0 > math.sqrt((2.0 * i / 1000) / 2.0))
    return {"grid_points": n + 13, "xmax": xmax, "violations_bogoliubov": viol,
            "max_ratio_S_over_bound": best[0], "argmax_x": best[1],
            "negative_control_S_eq_1_violations_on_0_2": neg_free, "negative_control_points": 999}


if __name__ == "__main__":
    json.dump(gate(), sys.stdout, indent=1)
