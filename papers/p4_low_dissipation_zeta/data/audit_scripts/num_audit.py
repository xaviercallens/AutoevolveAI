"""Independent numerics: (a) zeta-monotonicity grid (mpmath), (b) Eq.(1) on random engines from Eqs.(3)-(4),
(c) brute-force max efficiency at exactly given power vs root form, (d) negative controls."""
import random
import mpmath as mp
mp.mp.dps = 40

def root_form(c, Pt, z):
    s = mp.sqrt(1 - Pt); K = 2/(1 - s)
    A = K - c*(1+z)**2/4; B = c*(1-z**2)/2; C = K*(1-c) + c*(1-z)**2/4
    w = (B + mp.sqrt(B*B + 4*A*C))/(2*A)
    return (1 - w*w)/c

# (a) monotonicity grid
bad = 0; n = 0; mind = mp.mpf(1)
cs = [mp.mpf(i)/40 for i in range(1, 40)] + [mp.mpf('0.001'), mp.mpf('0.999')]
Ps = [mp.mpf(i)/40 for i in range(1, 41)] + [mp.mpf('1e-6')]
zs = [mp.mpf(-1) + mp.mpf(2)*k/200 for k in range(201)]
for c in cs:
    for Pt in Ps:
        prev = None
        for z in zs:
            v = root_form(c, Pt, z)
            if prev is not None:
                n += 1
                if v - prev <= 0: bad += 1
                mind = min(mind, v - prev)
            prev = v
print(f"(a) grid pairs {n}, non-increasing {bad}, min consecutive diff {mp.nstr(mind, 4)}")

# (b) random engines: a,b,q,c,th,tc ; keep P>0 and Qh>0
random.seed(11)
viol = 0; kept = 0; maxlhs = 0.0; viol_pert = 0; viol_rf = 0
for _ in range(200000):
    a = 10**random.uniform(-2, 2); b = 10**random.uniform(-2, 2); q = 10**random.uniform(-2, 2)
    c = random.uniform(1e-3, 1 - 1e-3); th = 10**random.uniform(-3, 3); tc = 10**random.uniform(-3, 3)
    W = q - a*a/th - b*b/tc
    Qh = q/c - a*a/th
    if W <= 0 or Qh <= 0: continue
    P = W/(th + tc); e = W/Qh; M = (a + b)**2
    Pt = P*4*M/q**2
    kept += 1
    s = (1 - Pt)**0.5
    lhs = e/c + (1 - c)*Pt/(2*(1 + s) - c*Pt)
    maxlhs = max(maxlhs, lhs)
    if lhs > 1 + 1e-12: viol += 1
    if e/c + (1 + c)*Pt/(2*(1 + s) - c*Pt) > 1 + 1e-12: viol_pert += 1
    z = (a - b)/(a + b)
    if e/c > float(root_form(mp.mpf(c), mp.mpf(Pt), mp.mpf(z))) + 1e-9: viol_rf += 1
print(f"(b) engines {kept}, Eq.(1) violations {viol}, max LHS {maxlhs:.8f}; zeta-specific root-form violations {viol_rf}; perturbed (1+c) violations {viol_pert}")

# (c) brute force: fix a,b,q,c,Pt; scan th, solve tc from P(th,tc)=P exactly (quadratic in tc), maximise eta
def brute(a, b, q, c, Pt, N=40000):
    M = (a + b)**2; P = Pt*q*q/(4*M); best = -1.0
    # P (th+tc) = q - a^2/th - b^2/tc  ->  P tc^2 + (P th - q + a^2/th) tc + b^2 = 0
    tau_p = q*(1 + (1 - Pt)**0.5)/(2*P)
    for i in range(1, N):
        th = tau_p*i/N
        B = P*th - q + a*a/th; disc = B*B - 4*P*b*b
        if disc < 0: continue
        for tc in ((-B + disc**0.5)/(2*P), (-B - disc**0.5)/(2*P)):
            if tc <= 0: continue
            W = q - a*a/th - b*b/tc; Qh = q/c - a*a/th
            if W > 0 and Qh > 0: best = max(best, W/Qh)
    return best/c
random.seed(5)
for _ in range(8):
    a = 10**random.uniform(-1, 1); b = 10**random.uniform(-1, 1); q = 10**random.uniform(-1, 1)
    c = random.uniform(0.05, 0.95); Pt = random.uniform(0.05, 1.0)
    z = (a - b)/(a + b)
    rf = float(root_form(mp.mpf(c), mp.mpf(Pt), mp.mpf(z))); bf = brute(a, b, q, c, Pt)
    print(f"(c) c={c:.3f} Pt={Pt:.3f} z={z:+.3f}: root {rf:.6f} brute {bf:.6f} root-brute {rf-bf:.2e}")
