"""Exact set-cover model (CP-SAT) for a replacement rule on the even base 2,4,..,2N (shift 0).

n = N-1 runners, open radius r = 1/N = 1/(n+1).  Fixed runners F = evens <= 2N not in the pool and not
dropped; candidate runners (v, shift) from a velocity pool and a shift menu.  Points to cover: every critical
point (arc endpoints, gap boundaries) and one point per cell inside the part of the circle the fixed runners leave
uncovered, all in exact integers.  Any SAT answer is re-checked by the two exact checkers (never trusted).

usage: cpsat_rule.py N J tlimit tag [--noodd] [--menu0] [--evens "a,b,.."] [--odds "..."]
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slr_exact import covers_open  # noqa: E402

from ortools.sat.python import cp_model  # noqa: E402


def smooth(limit: int, primes: tuple[int, ...]) -> list[int]:
    out = {1}
    for p in primes:
        new = set()
        for x in out:
            y = x
            while y <= limit:
                new.add(y)
                y *= p
        out |= new
    return sorted(out)


def build_and_solve(N: int, J: int, tlimit: float, pool_even: list[int], pool_odd: list[int], menu_mode: str,
                    workers: int = 1, extra_menu: list[int] | None = None, fix: list | None = None,
                    b: int = 2, dmult: int = 8, qs: tuple = (4,), jstep: int = 1, slots_max: int = 99999) -> dict:
    n = N - 1
    D = dmult * (N + 1)
    evens = [b * j for j in range(1, N + 1)]
    pe = [v for v in pool_even if v in set(evens)]
    po = [v for v in pool_odd if v not in set(evens)]
    F = [v for v in evens if v not in set(pe)]
    slots = min(n - len(F), slots_max)
    pool = pe + po
    L = 1
    for v in set(F) | set(pool):
        L = L * v // math.gcd(L, v)
    M = 2 * L * D * N  # scaled circle length

    def arcs(v: int, a: int):
        f = 2 * (L // v)
        step = D * N * f
        base = -a * N * f
        half = D * f
        kmin = (-(base + half)) // step - 1
        kmax = (M - base + half) // step + 1
        for k in range(kmin, kmax + 1):
            c = base + k * step
            lo, hi = c - half, c + half
            if hi > 0 and lo < M:
                yield lo, hi

    t0 = time.time()
    fa = sorted(x for v in F for x in arcs(v, 0))
    gaps = []
    R = 0
    for lo, hi in fa:
        if lo < R:
            if hi > R:
                R = hi
        else:
            gaps.append((R, lo))
            R = hi
    if R <= M:
        gaps.append((R, M))
    # shift menu (units of 1/D)
    shifts = set()
    for q in qs:
        assert D % q == 0
        for c in range(q):
            for j in range(-J, J + 1):
                shifts.add((c * (D // q) + j * jstep) % D)
    if menu_mode == "zero":
        shifts = {0}
    if extra_menu:
        shifts |= {x % D for x in extra_menu}
    shifts = sorted(shifts)
    cands = [(v, a) for v in pool for a in shifts]
    # candidate arcs restricted to those meeting a gap
    gl = [g[0] for g in gaps]
    gu = [g[1] for g in gaps]

    def meets(lo: int, hi: int) -> bool:
        # some gap [g0,g1] with g1 > lo and g0 < hi (open arc meets closed gap)
        i = bisect.bisect_left(gu, lo + 1)  # first gap with g1 >= lo+1
        return i < len(gaps) and gl[i] < hi

    cand_arcs: dict[tuple[int, int], list[tuple[int, int]]] = {}
    crit = set()
    for g0, g1 in gaps:
        crit.add(g0)
        crit.add(g1)
    for c in cands:
        al = [(lo, hi) for lo, hi in arcs(*c) if meets(lo, hi)]
        if al:
            cand_arcs[c] = al
            for lo, hi in al:
                for x in (lo, hi):
                    i = bisect.bisect_left(gu, x)
                    if i < len(gaps) and gl[i] <= x <= gu[i]:
                        crit.add(x)
    cs = sorted(crit)
    pts = list(cs)
    for x, y in zip(cs, cs[1:]):
        mid = (x + y) // 2
        # keep cell midpoint only if inside a gap
        i = bisect.bisect_left(gu, mid)
        if x < mid < y and i < len(gaps) and gl[i] <= mid <= gu[i]:
            pts.append(mid)
    pts = sorted(set(pts))
    cover: list[list[tuple[int, int]]] = [[] for _ in pts]
    for c, al in cand_arcs.items():
        for lo, hi in al:
            i0 = bisect.bisect_right(pts, lo)
            i1 = bisect.bisect_left(pts, hi)
            for i in range(i0, i1):
                cover[i].append(c)
    info = {"N": N, "n": n, "F": len(F), "slots": slots, "pool": len(pool), "shifts": len(shifts),
            "gaps": len(gaps), "points": len(pts), "prep_s": round(time.time() - t0, 1)}
    if any(not cv for cv in cover):
        info["status"] = "INFEASIBLE_NO_CANDIDATE_COVERS_A_POINT"
        return info
    uniq = {frozenset(cv) for cv in cover}
    # drop sets that are supersets of another (a point with more candidates is implied by the sparser one)
    ul = sorted(uniq, key=len)
    keep: list[frozenset] = []
    for st_ in ul:
        if len(keep) < 4000 and any(k <= st_ for k in keep[:2000]):
            continue
        keep.append(st_)
    info["distinct_cover_sets"] = len(uniq)
    info["kept_constraints"] = len(keep)
    m = cp_model.CpModel()
    x = {c: m.NewBoolVar(f"x{c[0]}_{c[1]}") for c in cand_arcs}
    for v in pool:
        vs = [x[c] for c in cand_arcs if c[0] == v]
        if len(vs) > 1:
            m.AddAtMostOne(vs)
    for cv in keep:
        m.AddBoolOr([x[c] for c in cv])
    if fix:
        for c in fix:
            if c not in x:
                info["status"] = f"FIX_CANDIDATE_MISSING {c}"
                return info
            m.Add(x[c] == 1)
    m.Add(sum(x.values()) <= slots)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tlimit
    s.parameters.num_workers = workers
    st = s.Solve(m)
    info["status"] = s.StatusName(st)
    info["solve_s"] = round(s.WallTime(), 1)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [c for c in x if s.Value(x[c])]
        v = F + [c[0] for c in chosen]
        a = [0] * len(F) + [c[1] for c in chosen]
        used = set(v)
        w = 1
        while len(v) < n:  # pad with harmless extra runners if the solver used fewer slots
            while w in used:
                w += 1
            v.append(w)
            a.append(0)
            used.add(w)
        info.update({"v": v, "a": a, "D": D})
    return info


def certify(info: dict, outdir: str, meta: dict) -> dict:
    v, a, D, n = info["v"], info["a"], info["D"], info["n"]
    assert len(v) == n == len(set(v)) and min(v) >= 1
    ok1 = covers_open(v, a, D, 1, n + 1)[0]
    cert = {"n": n, "v": v, "a": a, "D": D, "s": [f"{x}/{D}" for x in a], "delta_num": 1, "delta_den": n + 1,
            "delta": f"1/{n + 1}", "meta": meta}
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, f"cert_n{n:03d}.json")
    k = 0
    while os.path.exists(p):  # never overwrite an existing certificate
        k += 1
        p = os.path.join(outdir, f"cert_n{n:03d}_alt_{meta.get('tag', 'x')}_{k}.json")
    tmp = p + ".tmp"
    json.dump(cert, open(tmp, "w"), indent=1)
    r = subprocess.run([os.path.join(HERE, "check_cover"), tmp], capture_output=True, text=True)
    ok2 = r.returncode == 0
    if ok1 and ok2:
        cert["checker1"] = "COVERED"
        cert["checker2"] = r.stdout.strip()
        json.dump(cert, open(p, "w"), indent=1)
    os.remove(tmp)
    return {"checker1": ok1, "checker2": ok2, "out": r.stdout.strip()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("J", type=int)
    ap.add_argument("tlimit", type=float)
    ap.add_argument("tag")
    ap.add_argument("--b", type=int, default=2)
    ap.add_argument("--dmult", type=int, default=8)
    ap.add_argument("--qs", default="4")
    ap.add_argument("--jstep", type=int, default=1)
    ap.add_argument("--evp", default="2,3", help="primes for removable base multiples")
    ap.add_argument("--odp", default="3,5", help="primes for added non-base velocities")
    ap.add_argument("--vmax", type=float, default=1.0, help="added-velocity cap as multiple of b*N")
    ap.add_argument("--evmin", type=int, default=0, help="removable base velocities must be multiples of this")
    ap.add_argument("--slots", type=int, default=99999)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--family", default="x")
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(HERE), "certificates"))
    a = ap.parse_args()
    N = a.N
    cap = int(a.vmax * a.b * N)
    evp = tuple(int(x) for x in a.evp.split(",") if x)
    odp = tuple(int(x) for x in a.odp.split(",") if x)
    mult = a.evmin or a.b
    pe = [v for v in smooth(a.b * N, evp) if v % mult == 0 and v % a.b == 0]
    po = [v for v in smooth(cap, odp) if v % a.b != 0]
    qs = tuple(int(x) for x in a.qs.split(","))
    t0 = time.time()
    info = build_and_solve(N, a.J, a.tlimit, pe, po, "full", workers=a.workers, b=a.b, dmult=a.dmult, qs=qs,
                           jstep=a.jstep, slots_max=a.slots)
    out = {k: v for k, v in info.items() if k not in ("v", "a")}
    out.update({"family": a.family, "b": a.b, "J": a.J, "qs": a.qs, "jstep": a.jstep, "dmult": a.dmult,
                "pool_even": len(pe), "pool_odd": len(po), "workers": a.workers,
                "wall_s": round(time.time() - t0, 1), "tag": a.tag, "evp": a.evp, "odp": a.odp})
    if "v" in info:
        out["certify"] = certify(info, a.outdir, {"method": "cpsat_gen", "tag": a.tag, "family": a.family, "J": a.J,
                                                  "qs": a.qs, "b": a.b, "pool_even": pe, "pool_odd": po})
    print(json.dumps(out), flush=True)
    with open(os.path.join(os.path.dirname(HERE), "logs", "runs.jsonl"), "a") as f:
        f.write(json.dumps(out) + "\n")
