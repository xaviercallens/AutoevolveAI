"""Exploratory tensor search (deviations.md item 8): exact values of f (x) g for +-1 bases.

Product rule (proved in NOTE.md, tested in verify_tensor.py): for +-1 f, g,
R(f (x) g) = H(g) + |T(g)| R(f). Every pair is predicted by the rule, and the best pair at each
resolution is re-evaluated exactly with h5_exact.exact_ratio and with verify_tensor's independent code.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[4]
HYP = REPO / "scripts" / "openai_math" / "hypotheses"
WDIR = REPO / "results" / "openai_math" / "hypotheses" / "H5"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


vt = _load("h5_verify_tensor_ts", LANE / "verify_tensor.py")
hx = _load("h5_exact_ts", HYP / "h5_exact.py")


def bases() -> dict[str, list[np.ndarray]]:
    out: dict[str, list[np.ndarray]] = {"ones_N1": [np.ones((2, 2), dtype=np.int64)] * 3}
    e2 = json.loads((LANE / "chunks" / "E2_00_exhaust_N2.json").read_text())["result"]["argmax"]
    out["E2_00_argmax_N2"] = [np.array(x, dtype=np.int64) for x in e2]
    for n in (2, 3, 4):
        z = np.load(WDIR / f"best_inputs_N{n}.npz")
        out[f"witness_sign_N{n}"] = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
    return out


def main() -> int:
    b = bases()
    stats: dict[str, dict[str, Any]] = {}
    for name, f in b.items():
        r, h, t = vt.pm1_ratio(f)
        if r != hx.exact_ratio(f)[0]:
            raise ArithmeticError(name)
        fixed = str(h / (1 - t)) if t < 1 else "inf"
        stats[name] = {"N": f[0].shape[0].bit_length() - 1, "R": r, "H": h, "T": t, "fixed_point": fixed}
    pairs = []
    for fn, f in b.items():
        for gn, g in b.items():
            n = stats[fn]["N"] + stats[gn]["N"]
            if n > 8:
                continue
            pred = stats[gn]["H"] + stats[gn]["T"] * stats[fn]["R"]
            pairs.append({"coarse": fn, "fine": gn, "N": n, "predicted": pred})
    best: dict[int, dict[str, Any]] = {}
    for p in pairs:
        if p["N"] not in best or p["predicted"] > best[p["N"]]["predicted"]:
            best[p["N"]] = p
    checked = []
    for n in sorted(best):
        p = best[n]
        q = [np.kron(x, y) for x, y in zip(b[p["coarse"]], b[p["fine"]])]
        ex = hx.exact_ratio(q)[0]
        direct = vt.pm1_ratio(q)[0]
        checked.append({**{k: (str(v) if isinstance(v, Fraction) else v) for k, v in p.items()}, "h5_exact": str(ex), "direct": str(direct), "agree": ex == direct == p["predicted"], "exceeds_5_2": ex > Fraction(5, 2) + Fraction(1, 10**9)})
        if ex > Fraction(5, 2):
            np.savez_compressed(LANE / f"tensor_best_N{n}.npz", *q)
    out = {
        "exploratory": True,
        "bases": {k: {kk: (str(vv) if isinstance(vv, Fraction) else vv) for kk, vv in v.items()} for k, v in stats.items()},
        "all_pairs": [{**p, "predicted": str(p["predicted"])} for p in pairs],
        "best_per_N_checked": checked,
    }
    (LANE / "tensor_search.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"bases": out["bases"], "best_per_N_checked": checked}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
