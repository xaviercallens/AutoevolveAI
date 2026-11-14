"""Auditor tests: own exact evaluator vs producer evaluators; controls; gauge invariance; mutation power."""
from __future__ import annotations

import importlib.util
import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, "/tmp/dhaudit")
import aud_eval as A  # noqa: E402

import numpy as np  # noqa: E402

L = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/DH-Psi2")
spec = importlib.util.spec_from_file_location("psi_exhaust_prod", L / "code" / "psi_exhaust.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

out: dict = {}
rng = random.Random(777)
NRAND = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

# 1. random sign inputs at N=2: own S (wT=1,3,4) vs producer direct_value and h5_exact_value; Haar-free vs direct_value(haar=False)
agree = 0
agree_hf = 0
for _ in range(NRAND):
    F = [A.rand_sign(4, rng) for _ in range(3)]
    q = [np.array(m, dtype=np.int64) for m in F]
    p = A.parts(F, 2)
    ok = True
    for w in (1, 3, 4):
        mine = (w * abs(p["T"]) + p["H"]) * 64
        ok &= mine.denominator == 1 and int(mine) == P.direct_value(q, w, True) == P.h5_exact_value(q, w)
    agree += ok
    agree_hf += all(int(A.S_haar_free(F, 2, w)) == P.direct_value(q, w, False) for w in (1, 3))
out["random_N2_own_vs_direct_vs_h5exact"] = {"n": NRAND, "agree": agree}
out["random_N2_haarfree_own_vs_direct"] = {"n": NRAND, "agree": agree_hf}

# 1b. random REAL (integer-valued, non-sign) inputs: own vs producer direct_value (both are multilinear formulas)
agree_r = 0
for _ in range(300):
    F = [[[rng.randint(-3, 3) for _ in range(4)] for _ in range(4)] for _ in range(3)]
    q = [np.array(m, dtype=np.int64) for m in F]
    p = A.parts(F, 2)
    agree_r += all((w * abs(p["T"]) + p["H"]) * 64 == P.direct_value(q, w, True) for w in (1, 3))
out["random_N2_integer_inputs_own_vs_direct"] = {"n": 300, "agree": agree_r}

# 2. structured inputs
ones = [[[1] * 4 for _ in range(4)] for _ in range(3)]
pc = A.parts(ones, 2)
rigor = json.loads(Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/openai_math/hypotheses/tensor/rigor.json").read_text())
g = rigor["seeds"]["g2_lane_witness"]["matrices"]
pg = A.parts(g, 2)
out["const"] = {k: str(v) for k, v in pc.items()}
out["const_haarfree_R"] = str(A.S_haar_free(ones, 2, 1) / 64)
out["const_haarfree_Psi"] = str(A.S_haar_free(ones, 2, 3) / 64)
out["seed_g"] = {k: str(v) for k, v in pg.items()}
# producer C argmax for R (from summary.json) and HF argmaxes
summ = json.loads((L / "data" / "summary.json").read_text())
am = {}
for mode, (w, hb) in P.MODES.items():
    F = summ["modes"][mode]["c_int_enumeration"]["argmax"]
    val = (A.parts(F, 2)["H"] + w * abs(A.parts(F, 2)["T"])) * 64 if hb else A.S_haar_free(F, 2, w)
    am[mode] = {"own_S": str(val), "claimed_max_S": summ["modes"][mode]["c_int_enumeration"]["max_S"]}
out["producer_argmax_reevaluated"] = am

# 3. N=1 exhaustive (2^12): paper theorem max R = 1, Psi <= 3
maxR = Fraction(0)
maxPsi = Fraction(0)
for bits in range(2**12):
    F = [[[1 - 2 * ((bits >> (4 * v + 2 * i + j)) & 1) for j in range(2)] for i in range(2)] for v in range(3)]
    p = A.parts(F, 1)
    maxR = max(maxR, p["R"])
    maxPsi = max(maxPsi, p["Psi"])
out["N1_exhaustive"] = {"maxR": str(maxR), "maxPsi": str(maxPsi)}

# 4. gauge invariance of every term (own evaluator) and of the k-level parts
gauge_ok = 0
for _ in range(200):
    F = [A.rand_sign(4, rng) for _ in range(3)]
    D = [[rng.choice((-1, 1)) for _ in range(4)] for _ in range(3)]
    G = [[[D[v][i] * F[v][i][j] * D[(v + 1) % 3][j] for j in range(4)] for i in range(4)] for v in range(3)]
    a, b = A.parts(F, 2), A.parts(G, 2)
    gauge_ok += a["T"] == b["T"] and a["H"] == b["H"]
out["gauge_invariance_random"] = {"n": 200, "agree": gauge_ok}

# 5. mutation power: mutated own evaluator must disagree with producer's direct_value on random inputs
mut = {}
for variant in ("level1_weight1", "odd_class", "coarse_haar_at_level1"):
    dis = 0
    for _ in range(200):
        F = [A.rand_sign(4, rng) for _ in range(3)]
        q = [np.array(m, dtype=np.int64) for m in F]
        p = A.parts(F, 2, variant)
        dis += (3 * abs(p["T"]) + p["H"]) * 64 != P.direct_value(q, 3, True)
    mut[variant] = {"n": 200, "disagree": dis}
out["mutation_power"] = mut

# 6. h1 parity convention immaterial: flip level-1 Haar orientation (h1(x)=+1 for odd x) by relabelling
#    cells 2p<->2p+1 in coordinate v and checking Psi unchanged
perm_ok = 0
sw = [1, 0, 3, 2]
for _ in range(200):
    F = [A.rand_sign(4, rng) for _ in range(3)]
    v = rng.randrange(3)
    G = [row[:] for row in F[v]]
    # permute x_v: affects F_v rows and F_{v-1} columns
    Fv = [[F[v][sw[i]][j] for j in range(4)] for i in range(4)]
    Fm = [[F[(v - 1) % 3][i][sw[j]] for j in range(4)] for i in range(4)]
    Fn = [m for m in F]
    Fn[v] = Fv
    Fn[(v - 1) % 3] = Fm
    perm_ok += A.parts(F, 2)["Psi"] == A.parts(Fn, 2)["Psi"]
out["within_interval_swap_invariance"] = {"n": 200, "agree": perm_ok}

print(json.dumps(out, indent=1))
