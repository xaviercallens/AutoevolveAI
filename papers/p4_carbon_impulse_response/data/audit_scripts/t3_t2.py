"""Auditor numerics for T3 (two maxima for staircase, non-exponential CM h) and T2 (single exponential)."""
import math, random

def mk(a0, A, T):
    return lambda x: a0 + sum(a * math.exp(-x / t) for a, t in zip(A, T))

joos = mk(0.2173, [0.2240, 0.2824, 0.2763], [394.4, 36.54, 4.304])
two_a0zero = mk(0.0, [0.5, 0.5], [100.0, 5.0])

def count_extrema_staircase(h, jumps, tmax, n=200000):
    # u'(t) = sum_j c_j h(t - z_j) [t > z_j]
    def up(t):
        return sum(c * h(t - z) for z, c in jumps if t > z)
    mx, mn = [], []
    prev = up(1e-9)
    for k in range(1, n + 1):
        t = tmax * k / n
        v = up(t)
        if prev > 0 and v <= 0: mx.append(round(t, 3))
        if prev < 0 and v >= 0: mn.append(round(t, 3))
        prev = v
    return mx, mn

def t3_case(h, L, d, theta, A=1.0):
    B = theta * A
    rho = lambda x: h(x + d) / h(x)
    # x*: rho(x*) = theta (rho increasing)
    lo, hi = 0.0, 1500.0
    if not (rho(lo) < theta < rho(hi)):
        xs = None
    else:
        for _ in range(200):
            mid = (lo + hi) / 2
            if rho(mid) < theta: lo = mid
            else: hi = mid
        xs = lo
    z3 = d + (xs if xs else 50) + 50
    mx, mn = count_extrema_staircase(h, [(0.0, A), (d, -B), (z3, -(A - B))], z3 + 400)
    return xs, z3, mx, mn

# strict monotonicity of rho for joos and two_a0zero
for name, h in [('joos', joos), ('a0=0 two-exp', two_a0zero)]:
    d = 5.0
    vals = [h(x + d) / h(x) for x in [0.1 * k for k in range(0, 5001)]]
    print(name, 'rho strictly increasing on grid:', all(b > a for a, b in zip(vals, vals[1:])), 'rho(0)=h(d)=%.6f' % vals[0], 'rho(500)=%.6f' % vals[-1])

d = 5.0
print('Joos h(5)=%.6f, L=1' % joos(d))
for theta in [0.5, 0.65, 0.7, 0.8, 0.95]:
    print('Joos theta', theta, t3_case(joos, 1.0, d, theta))
L2 = math.exp(-d / 100.0)
print('a0=0 two-exp: h(5)=%.6f  L=%.6f' % (two_a0zero(d), L2))
for theta in [two_a0zero(d) - 0.02, two_a0zero(d) + 0.02, (two_a0zero(d) + L2) / 2, L2 + 0.005]:
    print('a0=0 theta %.4f' % theta, t3_case(two_a0zero, L2, d, theta))

# T2: single exponential, random weakly unimodal staircases and PL paths; count strict sign changes of u'
random.seed(12345)
tau = 30.0
single = mk(0.0, [1.0], [tau])
worst = 0
for trial in range(400):
    k = random.randint(2, 8)
    ups = sorted(random.random() for _ in range(k))
    peak = random.randint(1, k)
    levels = ups[:peak] + sorted([random.random() * ups[peak - 1] for _ in range(k - peak)], reverse=True)
    times = sorted(random.uniform(0, 300) for _ in range(k))
    jumps = []
    prev = 0.0
    for t, lv in zip(times, levels):
        jumps.append((t, lv - prev)); prev = lv
    jumps.append((times[-1] + random.uniform(1, 100), -prev))
    mx, mn = count_extrema_staircase(single, jumps, 800, n=40000)
    worst = max(worst, len(mx))
    if len(mx) > 1 or mn:
        print('T2 VIOLATION?', jumps, mx, mn)
print('T2 single-exp: max number of +/- sign changes over 400 random unimodal staircases =', worst)
# same staircases with Joos: how often 2 maxima
