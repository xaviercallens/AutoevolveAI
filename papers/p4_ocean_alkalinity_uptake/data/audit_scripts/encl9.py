"""Auditor's independent rigorous check of eta enclosures over the K2 seawater box.

Method (differs from producer): constants via mean-value (centred) form with analytic T,S derivatives enclosed in
intervals; h bracketed using monotonicity of the root in each constant (TA(h) increasing in C,K1,K2,BT,KB,KW,
decreasing in h) and verified by interval sign tests; eta by plain interval evaluation of 1/(1+g) on h sub-pieces;
adaptive bisection of cells until each cell's enclosure lies inside the target [L,U].
usage: encl.py nsigma L U
"""
import sys, json, time
sys.path.insert(0, '/tmp/k2audit')
from mpmath import mp, iv, mpf
import mpmath
from model import logs, SIG
iv.dps = 30
mp.dps = 30
I = iv.mpf
BOX = {"T": (0.0, 30.0), "S": (30.0, 38.0), "f": (280.0, 560.0), "TA35": (2200.0, 2400.0)}
KEYS = ("T", "S", "f", "TA35", "dK0", "dK1", "dK2", "dKB", "dKW")


def dlogs(T_c, S):
    """interval enclosures of d/dT and d/dS of (lnK0, log10K1, log10K2, lnKB, lnKW); T_c,S intervals."""
    T = T_c + I("273.15")
    lnT = iv.log(T)
    q = iv.sqrt(S)
    dT = [
        -I("93.4517")*100/T**2 + I("23.3585")/T + S*(-I("0.023656")/100 + 2*I("0.0047036")*T/10000),
        I("3633.86")/T**2 - I("9.67770")/T,
        I("471.78")/T**2 + I("3.16967")/T,
        -(I("-8966.90") - I("2890.53")*q - I("77.942")*S + I("1.728")*S*q - I("0.0996")*S**2)/T**2
        + (I("-24.4344") - I("25.085")*q - I("0.2474")*S)/T + I("0.053105")*q,
        I("13847.26")/T**2 - I("23.6521")/T + (-I("118.67")/T**2 + I("1.0495")/T)*q,
    ]
    dS = [
        I("0.023517") - I("0.023656")*(T/100) + I("0.0047036")*(T/100)**2,
        I("0.011555") - 2*I("0.0001152")*S,
        I("0.01781") - 2*I("0.0001122")*S,
        (-I("2890.53")/(2*q) - I("77.942") + I("1.5")*I("1.728")*q - 2*I("0.0996")*S)/T
        + (I("137.1942")/(2*q) + I("1.62142")) + (-I("25.085")/(2*q) - I("0.2474"))*lnT + I("0.053105")*T/(2*q),
        (I("118.67")/T - I("5.977") + I("1.0495")*lnT)/(2*q) - I("0.01615"),
    ]
    return dT, dS


CC = {}


def consts_iv(t, s, ns, dp=None):
    key = (t, s, ns, dp)
    if key in CC:
        return CC[key]
    tm, sm = (t[0]+t[1])/2, (s[0]+s[1])/2
    ti, si = I(list(t)), I(list(s))
    f0 = logs(I(tm), I(sm), iv)
    dT, dS = dlogs(ti, si)
    ht, hs = I([-(t[1]-t[0])/2, (t[1]-t[0])/2]), I([-(s[1]-s[0])/2, (s[1]-s[0])/2])
    L = [f0[k] + dT[k]*ht + dS[k]*hs for k in range(5)]
    pm = (lambda name: I([-ns*SIG[name], ns*SIG[name]])) if dp is None else (lambda name: I(list(dict(dp)[name])))
    ln10 = iv.log(10)
    c = dict(K0=iv.exp(L[0] + pm("K0")*ln10), K1=iv.exp((L[1]+pm("K1"))*ln10), K2=iv.exp((L[2]+pm("K2"))*ln10),
             KB=iv.exp(L[3] + pm("KB")*ln10), KW=iv.exp(L[4] + pm("KW")*ln10), BT=I("0.000416")*si/35)
    CC[key] = c
    return c


def F(h, c, f, ta):
    C = c["K0"]*f*I("1e-6")
    return C*(c["K1"]/h + 2*c["K1"]*c["K2"]/h**2) + c["BT"]/(1 + h/c["KB"]) + c["KW"]/h - h - ta


def endpt(c, which):
    return {k: I(mp.make_mpf(v._mpi_[which])) for k, v in c.items()}


def root_point(cp, f, ta):
    lo, hi = mpf("1e-10"), mpf("1e-6")
    for _ in range(80):
        mid = mp.sqrt(lo*hi)
        if F(I(mid), cp, I(f), I(ta)).mid > 0:
            lo = mid
        else:
            hi = mid
    return lo


def eta_iv(h, c, f):
    C = c["K0"]*f*I("1e-6")
    R = c["BT"]*c["KB"]/(c["KB"]+h)**2 + c["KW"]/h**2 + 1
    g = (2*c["K2"] + h**3*R/(C*c["K1"]))/(h + 2*c["K2"])
    return 1/(1+g)


def cell_enc(cell, ns, npieces=4):
    dp = tuple((n, cell["d"+n]) for n in ("K0", "K1", "K2", "KB", "KW"))
    c = consts_iv(cell["T"], cell["S"], ns, dp)
    f = I(list(cell["f"]))
    tas = [s/35*t*1e-6 for s in cell["S"] for t in cell["TA35"]]
    ta = I([min(tas), max(tas)])
    # monotone root: smallest h at low consts, low f, high TA; largest at high consts, high f, low TA
    hl0 = root_point(endpt(c, 0), mpf(cell["f"][0]), ta.b)
    hh0 = root_point(endpt(c, 1), mpf(cell["f"][1]), ta.a)
    # rigorous verification over the full parameter cell (widen until the interval sign test passes)
    eps = mpf("1e-12")
    while True:
        hl, hh = hl0*(1-eps), hh0*(1+eps)
        if F(I(hl), c, f, ta).a > 0 and F(I(hh), c, f, ta).b < 0:
            break
        eps *= 4
        if eps > 0.5:
            raise RuntimeError("bracket not verified")
    lo, hi = mpf(1), mpf(0)
    r = (hh/hl)**(mpf(1)/npieces)
    edges = [hl*r**k for k in range(npieces)] + [hh]
    for k in range(npieces):
        e = eta_iv(I([edges[k], edges[k+1]]), c, f)
        lo, hi = min(lo, mp.make_mpf(e._mpi_[0])), max(hi, mp.make_mpf(e._mpi_[1]))
    return lo, hi


def run(ns, L, U, init=(6, 2, 2, 2), maxdepth=60):
    L, U = mpf(L), mpf(U)
    for n in ("K0", "K1", "K2", "KB", "KW"):
        BOX["d"+n] = (-ns*SIG[n], ns*SIG[n])
    stack = []
    for i in range(init[0]):
        for j in range(init[1]):
            for k in range(init[2]):
                for l in range(init[3]):
                    cell = {"d"+n: BOX["d"+n] for n in ("K0", "K1", "K2", "KB", "KW")}
                    for key, n, ix in zip(KEYS[:4], init, (i, j, k, l)):
                        a, b = BOX[key]
                        w = (b-a)/n
                        cell[key] = (a+ix*w, a+(ix+1)*w if ix < n-1 else b)
                    stack.append((cell, 0))
    ncells = 0
    glo, ghi = mpf(1), mpf(0)
    fails = []
    while stack:
        cell, d = stack.pop()
        lo, hi = cell_enc(cell, ns)
        if lo >= L and hi <= U:
            ncells += 1
            glo, ghi = min(glo, lo), max(ghi, hi)
            continue
        if d >= maxdepth:
            fails.append((cell, float(lo), float(hi)))
            continue
        wd = {k: (0.2 if k.startswith("d") else 1.0)*(cell[k][1]-cell[k][0])/(BOX[k][1]-BOX[k][0]) for k in KEYS}
        k = max(wd, key=wd.get)
        m = (cell[k][0]+cell[k][1])/2
        for part in ((cell[k][0], m), (m, cell[k][1])):
            sub = dict(cell); sub[k] = part
            stack.append((sub, d+1))
    return {"nsigma": ns, "target": [str(L), str(U)], "accepted_cells": ncells, "fails": len(fails),
            "fail_examples": fails[:3], "union_of_cell_enclosures": [float(glo), float(ghi)]}


if __name__ == "__main__":
    t0 = time.time()
    res = run(float(sys.argv[1]), sys.argv[2], sys.argv[3])
    res["seconds"] = time.time()-t0
    print(json.dumps(res))
