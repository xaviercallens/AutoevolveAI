"""Diagnose Eq.(13) transcription vs root form; brute-force engine optimum (floats, Tier X)."""
import numpy as np
from scipy.optimize import minimize_scalar, brentq
import mpmath as mp
import importlib.util, sys

spec = importlib.util.spec_from_file_location("link_mod", "code/link_funcs.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)


def brute(c, P, z, n=20001):
    """max eta/eta_C over (th,tc)>0 with Eq.(3) power = P*Pmax, units M=1, q=1, Qh=1/c; tau-relaxation not used."""
    Mh = (1 + z) ** 2 / 4
    Mc = (1 - z) ** 2 / 4
    q = 1.0
    Pmax = q * q / 4
    Pt = P * Pmax
    best = -1.0
    # parametrise by th; solve tc from power equation  q - Mh/th - Mc/tc = Pt (th+tc)
    for th in np.geomspace(1e-3, 1e4, n):
        # (q - Mh/th) - Mc/tc - Pt th - Pt tc = 0 -> multiply tc: (q-Mh/th-Pt th) tc - Mc - Pt tc^2 = 0
        a = -Pt
        b = q - Mh / th - Pt * th
        cc = -Mc
        disc = b * b - 4 * a * cc
        if disc < 0:
            continue
        for sgn in (1, -1):
            tc = (-b + sgn * np.sqrt(disc)) / (2 * a)
            if tc <= 0:
                continue
            W = q - Mh / th - Mc / tc
            eta = W / (q / c - Mh / th)
            best = max(best, eta / c)
    return best


pts = [(0.5, 0.5, 0.0), (0.5, 0.5, 0.5), (0.5, 0.5, 1.0), (0.5, 0.5, -1.0), (0.1, 0.9, 0.3), (0.9, 0.2, -0.4), (0.5, 1.0, 0.5)]
for c, P, z in pts:
    r = float(L.root_form(mp.mpf(c), mp.mpf(P), mp.mpf(z)))
    e = float(L.eq13(mp.mpf(c), mp.mpf(P), mp.mpf(z)))
    b = brute(c, P, z)
    print(f"c={c} P={P} zeta={z}: root={r:.6f} eq13={e:.6f} brute={b:.6f}")
