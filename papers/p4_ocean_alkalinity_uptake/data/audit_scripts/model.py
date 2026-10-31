"""Independent auditor model (constants typed from the Dickson 2007 Guide ch.5 text, eqs 30,37,40,43,62)."""
from mpmath import mp, iv, mpf
import mpmath
mp.dps = 50
iv.dps = 40
SIG = {"K0": 0.002, "K1": 0.0075, "K2": 0.015, "KB": 0.01, "KW": 0.01}


def logs(T_c, S, X):
    """X = mp or iv context. returns lnK0, log10K1, log10K2, lnKB, lnKW"""
    m = X.mpf
    T = T_c + m("273.15")
    lnT = X.log(T)
    lnK0 = m("93.4517")*(m(100)/T) - m("60.2409") + m("23.3585")*X.log(T/m(100)) \
        + S*(m("0.023517") - m("0.023656")*(T/m(100)) + m("0.0047036")*(T/m(100))**2)
    l10K1 = m("-3633.86")/T + m("61.2172") - m("9.67770")*lnT + m("0.011555")*S - m("0.0001152")*S**2
    l10K2 = m("-471.78")/T - m("25.9290") + m("3.16967")*lnT + m("0.01781")*S - m("0.0001122")*S**2
    sq = X.sqrt(S)
    lnKB = (m("-8966.90") - m("2890.53")*sq - m("77.942")*S + m("1.728")*S*sq - m("0.0996")*S**2)/T \
        + (m("148.0248") + m("137.1942")*sq + m("1.62142")*S) \
        + (m("-24.4344") - m("25.085")*sq - m("0.2474")*S)*lnT + m("0.053105")*sq*T
    lnKW = m("-13847.26")/T + m("148.9652") - m("23.6521")*lnT \
        + (m("118.67")/T - m("5.977") + m("1.0495")*lnT)*sq - m("0.01615")*S
    return lnK0, l10K1, l10K2, lnKB, lnKW


def consts_mp(T_c, S, dpk=None, bt_coef="0.000416", kw_const_shift=0):
    dpk = dpk or {}
    a = logs(mpf(T_c), mpf(S), mp)
    K0 = mp.exp(a[0]) * mpf(10)**(-dpk.get("K0", 0))
    K1 = mpf(10)**(a[1] - dpk.get("K1", 0))
    K2 = mpf(10)**(a[2] - dpk.get("K2", 0))
    KB = mp.exp(a[3]) * mpf(10)**(-dpk.get("KB", 0))
    KW = mp.exp(a[4] + kw_const_shift) * mpf(10)**(-dpk.get("KW", 0))
    BT = mpf(bt_coef)*mpf(S)/35
    return dict(K0=K0, K1=K1, K2=K2, KB=KB, KW=KW, BT=BT)


def TA_of_h(h, c, f):
    C = c["K0"]*f*mpf("1e-6")
    return C*(c["K1"]/h + 2*c["K1"]*c["K2"]/h**2) + c["BT"]*c["KB"]/(c["KB"]+h) + c["KW"]/h - h


def DIC_of_h(h, c, f):
    C = c["K0"]*f*mpf("1e-6")
    return C*(1 + c["K1"]/h + c["K1"]*c["K2"]/h**2)


def solve_h(c, f, TA):
    g = lambda lh: TA_of_h(mp.exp(lh), c, f) - TA
    lo, hi = mp.log(mpf("1e-12")), mp.log(mpf("1e-4"))
    for _ in range(200):
        mid = (lo+hi)/2
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return mp.exp((lo+hi)/2)


def eta_closed(h, c, f):
    """own derivation: eta = (dDIC/dh)/(dTA/dh) at fixed C"""
    C = c["K0"]*f*mpf("1e-6")
    K1, K2 = c["K1"], c["K2"]
    num = C*(K1/h**2 + 2*K1*K2/h**3)
    den = C*(K1/h**2 + 4*K1*K2/h**3) + c["BT"]*c["KB"]/(c["KB"]+h)**2 + c["KW"]/h**2 + 1
    return num/den


def eta_point(T, S, f, TA35, **kw):
    c = consts_mp(T, S, **kw)
    TA = mpf(S)/35*mpf(TA35)*mpf("1e-6")
    h = solve_h(c, mpf(f), TA)
    return eta_closed(h, c, mpf(f)), h, c
