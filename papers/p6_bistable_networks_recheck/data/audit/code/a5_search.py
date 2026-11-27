"""Independent random search (F model, rho sampled) on the 27 positives and the 193 ROOT/FLUX negatives."""
import sys, json, time
sys.path.insert(0, "/tmp/bistabaudit/code")
import numpy as np
import sympy as sp
from net import catalogue, field, x, y, a, b, rho, K

ids = catalogue()
rules = json.load(open("/tmp/bistabaudit/a3_rules.json"))
POS = "N0438 N0440 N0442 N0443 N0448 N0450 N0452 N0453 N0459 N0467 N0474 N0476 N0477 N0480 N0482 N0483 N0489 N0510 N0514 N0515 N0520 N0524 N0525 N0548 N0549 N0554 N0555".split()
NEG = [n for n in rules["rest"] if n not in POS]
NS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
rng = np.random.default_rng(20261101)


def run(n):
    es = ids[n]; m = len(es)
    P = [a, b, rho, *K[:m]]
    f, g = field(es, "F")
    R = sp.Poly(sp.resultant(f, g, y), x)
    cf = [sp.lambdify(P, c, "numpy") for c in R.all_coeffs()]
    gq = sp.Poly(g, y)
    gc = [sp.lambdify([x] + P, c, "numpy") for c in gq.all_coeffs()]
    fl = sp.lambdify([x, y] + P, f, "numpy")
    fsc = sp.lambdify([x, y] + P, sum(sp.Abs(t) for t in sp.Add.make_args(f)), "numpy")
    J = [sp.lambdify([x, y] + P, sp.diff(p, v), "numpy") for p in (f, g) for v in (x, y)]
    global LAST_TH
    th = 10 ** rng.uniform(-3, 3, size=(len(P), NS)); LAST_TH = th
    co = np.array([np.broadcast_to(np.asarray(c(*th), float), (NS,)) for c in cf]).T  # (NS, d+1)
    d = co.shape[1] - 1
    best = np.zeros(NS, int)
    if d < 1:
        return 0, best
    lead = co[:, 0:1]
    comp = np.zeros((NS, d, d))
    comp[:, 0, :] = -co[:, 1:] / lead
    if d > 1:
        comp[:, np.arange(1, d), np.arange(d - 1)] = 1.0
    roots = np.linalg.eigvals(comp)
    sinkX = np.full((NS, d), np.nan)
    for r in range(d):
        xr = roots[:, r]
        ok = (np.abs(xr.imag) <= 1e-7 * np.abs(xr)) & (xr.real > 0)
        X = xr.real
        cs = [np.broadcast_to(np.asarray(c(X, *th), float), (NS,)) for c in gc]
        cand = []
        if len(cs) == 3:
            A, B, Cc = cs
            disc = B * B - 4 * A * Cc
            sq = np.sqrt(np.maximum(disc, 0))
            q = -0.5 * (B + np.sign(B + (B == 0)) * sq)  # stable quadratic
            with np.errstate(all="ignore"):
                cand = [q / A, Cc / q]
        else:
            with np.errstate(all="ignore"):
                cand = [-cs[1] / cs[0]]
        Ybest = np.full(NS, np.nan); resid = np.full(NS, np.inf)
        for Y in cand:
            with np.errstate(all="ignore"):
                fv = np.abs(fl(X, Y, *th)) / fsc(X, np.abs(Y), *th)
            better = np.isfinite(Y) & (Y > 0) & (fv < resid)
            Ybest = np.where(better, Y, Ybest); resid = np.where(better, fv, resid)
        good = ok & (resid < 1e-8) & np.isfinite(Ybest)
        with np.errstate(all="ignore"):
            fx, fy, gx, gy = [np.broadcast_to(np.asarray(j(X, Ybest, *th), float), (NS,)) for j in J]
        sink = good & (fx + gy < 0) & (fx * gy - fy * gx > 0)
        sinkX[:, r] = np.where(sink, X, np.nan)
    srt = np.sort(sinkX, axis=1)  # nans last
    distinct = np.isfinite(srt[:, :1]).astype(int).ravel()
    for r in range(1, d):
        prev, cur = srt[:, r - 1], srt[:, r]
        distinct += (np.isfinite(cur) & (np.abs(cur - prev) > 1e-6 * np.abs(cur))).astype(int)
    return int((distinct >= 2).sum()), distinct


if __name__ == "__main__":
    t0 = time.time(); out = {}
    for n in POS + NEG:
        hits, dist = run(n)
        conf = 0
        if hits and n not in POS:
            from a2_witness import check
            for i in np.nonzero(dist >= 2)[0][:200]:
                th = LAST_TH[:, i]
                pr = [sp.Rational(float(t)).limit_denominator(10**9) for t in th]
                r = check(ids[n], [pr[0], pr[1]] + pr[3:], r=pr[2])
                conf += int(r["sinks"] >= 2 or r["undecided"] > 0)
        out[n] = [hits, conf]
    print("samples/network", NS, "secs", round(time.time() - t0))
    print("positives found:", sum(1 for n in POS if out[n][0] > 0), "/27; min hit rate",
          min(out[n][0] for n in POS) / NS)
    print("negatives with >=2 numerical sinks:", {n: out[n] for n in NEG if out[n][0] > 0}, "of", len(NEG))
    print("exact-confirmed (>=2 sinks or undecided) among negatives:", sum(out[n][1] for n in NEG))
    json.dump(out, open(f"/tmp/bistabaudit/a5_search_{NS}.json", "w"))
