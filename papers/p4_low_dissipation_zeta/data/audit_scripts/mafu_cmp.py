"""Compare Ma-Fu 2024 (arXiv:2411.03849) Eq. (B6) eta_+(delta) with the E3 root form eta_+(zeta)."""
import random
import mpmath as mp
mp.mp.dps = 40

def root_form(c, Pt, z):
    s = mp.sqrt(1 - Pt); K = 2/(1 - s)
    A = K - c*(1+z)**2/4; B = c*(1-z**2)/2; C = K*(1-c) + c*(1-z)**2/4
    w = (B + mp.sqrt(B*B + 4*A*C))/(2*A)
    return (1 - w*w)/c

def mafu(c, Pt, d):
    lam = Pt/(4*(1 - d*c))
    return ((1 + 2*lam*d*c) + mp.sqrt(4*lam*d*c + 1 - 4*lam))/(2*(lam*d*d*c*c + 1))

random.seed(3)
for mapping, f in [("delta=(1+z)/2", lambda z: (1+z)/2), ("delta=(1-z)/2", lambda z: (1-z)/2),
                   ("delta=((1+z)/2)^2/((1+z)^2/4+(1-z)^2/4)", lambda z: (1+z)**2/((1+z)**2+(1-z)**2))]:
    m = mp.mpf(0)
    for _ in range(2000):
        c = mp.mpf(random.uniform(0.01, 0.99)); Pt = mp.mpf(random.uniform(0.01, 1)); z = mp.mpf(random.uniform(-1, 1))
        m = max(m, abs(mafu(c, Pt, f(z)) - root_form(c, Pt, z)))
    print(mapping, "max diff", mp.nstr(m, 5))
# endpoints
for c in [mp.mpf('0.3'), mp.mpf('0.8')]:
    for Pt in [mp.mpf('0.5'), mp.mpf(1)]:
        print(f"c={c} Pt={Pt}: root(-1)={mp.nstr(root_form(c,Pt,-1),8)} mafu(0)={mp.nstr(mafu(c,Pt,0),8)} root(1)={mp.nstr(root_form(c,Pt,1),8)} mafu(1)={mp.nstr(mafu(c,Pt,1),8)}")
