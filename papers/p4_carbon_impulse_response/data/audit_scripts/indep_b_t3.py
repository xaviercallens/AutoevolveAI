"""Independent auditor check of K3 (b) peak times and T2/T3 numerics. Own closed forms, mpmath mp (not iv), Brent/bisection root finding."""
import json, sys
import mpmath as mp
mp.mp.dps = 50
D = mp.mpf
JOOS = (D('0.2173'), [D('0.2240'), D('0.2824'), D('0.2763')], [D('394.4'), D('36.54'), D('4.304')])
SESH43 = (D('0.217'), [D('0.224'), D('0.282'), D('0.276')], [D('394'), D('36.5'), D('4.30')])
SESH44 = (D('0.217'), [D('0.224'), D('0.282'), D('0.276')], [D('394'), D('36.5'), D('4.4')])

def seshadri_uprime(irf, r, taum, tg, t):
    """m(z)=exp(al z) z<=tg, exp(al tg - (z-tg)/taum) z>tg; al=ln(1+r)-1/taum. u'(t)=m(t)-sum a_i/tau_i x_i(t)."""
    a0, A, T = irf
    al = mp.log(1 + r) - 1 / taum
    be = -1 / taum
    def m(z):
        return mp.e**(al * z) if z <= tg else mp.e**(al * tg + be * (z - tg))
    s = m(t)
    for ai, ti in zip(A, T):
        lam = 1 / ti
        # x = int_0^min(t,tg) e^{al z} e^{-lam(t-z)} dz + int_tg^t m(tg) e^{be(z-tg)} e^{-lam(t-z)} dz
        t1 = min(t, tg)
        x = mp.e**(-lam * t) * (mp.e**((al + lam) * t1) - 1) / (al + lam)
        if t > tg:
            c = mp.e**(al * tg)
            x += c * mp.e**(-lam * t) * mp.e**(-be * tg) * (mp.e**((be + lam) * t) - mp.e**((be + lam) * tg)) / (be + lam)
        s -= ai / ti * x
    return s

def peak(irf, r, taum, tg=D(60)):
    f = lambda t: seshadri_uprime(irf, r, taum, tg, t)
    # coarse scan for sign changes with step 0.5 over [0.01, 3000]
    grid = [D(k) / 2 for k in range(1, 6001)]
    vals = [f(t) for t in grid[::1]] if False else None
    sc = []
    prev_t, prev_v = D('0.01'), f(D('0.01'))
    for t in grid:
        v = f(t)
        if prev_v > 0 and v <= 0:
            sc.append(('+-', prev_t, t))
        elif prev_v < 0 and v >= 0:
            sc.append(('-+', prev_t, t))
        prev_t, prev_v = t, v
    roots = [mp.findroot(f, (lo, hi), solver='anderson') for kind, lo, hi in sc if kind == '+-']
    al = mp.log(1 + r) - 1 / taum
    t1 = tg if al > 0 else D(0)
    return sc, roots, t1

def main():
    prod = json.load(open(sys.argv[1]))['scenarios']
    out = {}
    cases = []
    for name, irf in [('joos_table5', JOOS)]:
        for r in ['3/100', '5/100', '15/1000']:
            for tm in [20, 40, 50, 60, 80, 100, 120]:
                cases.append((name, irf, r, tm))
    maxdiff = D(0)
    for name, irf, r, tm in cases:
        rr = (lambda n,d: D(n)/D(d))(*map(int, r.split('/')))
        sc, roots, t1 = peak(irf, rr, D(tm))
        key = f"{name}|r={r}|tau_m={tm}"
        if key not in prod:
            # producer may write 3/200 instead of 15/1000
            alt = [k for k in prod if k.startswith(name) and k.endswith(f"tau_m={tm}") and abs(eval(k.split('|')[1][2:]) - float(rr)) < 1e-12]
            key = alt[0]
        p = prod[key]
        pt2 = (lambda n,d: D(n)/D(d))(*map(int, p['t2_enclosure'][0].split('/')))
        d = abs(roots[0] - pt2) if roots else None
        maxdiff = max(maxdiff, d)
        print(key, 'signchanges', [(k, float(a)) for k, a, b in sc], 't2', mp.nstr(roots[0], 25), 'delay', mp.nstr(roots[0] - t1, 8), 't1', t1, '|diff vs producer|', mp.nstr(d, 3))
    print('max |t2_auditor - t2_producer| over Joos 21 =', mp.nstr(maxdiff, 3))
    # Seshadri variants, a few
    for irf, nm in [(SESH43, 'S4.30'), (SESH44, 'S4.4')]:
        for r, tm in [('3/100', 50), ('15/1000', 50), ('5/100', 120)]:
            rr = (lambda n,d: D(n)/D(d))(*map(int, r.split('/')))
            sc, roots, t1 = peak(irf, rr, D(tm))
            print(nm, r, tm, 't2', mp.nstr(roots[0], 12), 'delay', mp.nstr(roots[0] - t1, 8))
    # boundary ln(1+r)=1/taum: t2 continuous, t1 jumps
    r = D('0.03'); tb = 1 / mp.log(1 + r)
    for eps in [D('-1e-6'), D('1e-6')]:
        sc, roots, t1 = peak(JOOS, r, tb + eps)
        print('boundary taum=', mp.nstr(tb + eps, 12), 't2', mp.nstr(roots[0], 12), 't1', t1, 'delay', mp.nstr(roots[0] - t1, 10))

main()
