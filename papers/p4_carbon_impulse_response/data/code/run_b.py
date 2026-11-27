"""K3 part (b): certified enclosures of the concentration-peak time and delay for Seshadri's emission family.

m(t) = (1+r)^min(t,tg) exp(-t/tau_m)   (m0 = 1, t0 = 0); IRF h = a0 + sum a_i exp(-t/tau_i).
u'(t) = m - sum_i (a_i/tau_i) x_i,  u'' = m' - m sum a_i/tau_i + sum a_i/tau_i^2 x_i,  x_i' = m - x_i/tau_i.
A peak time is enclosed by bisection on exact rational points with interval signs of u' and u'' < 0 on the bracket.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from mpmath import iv

sys.path.insert(0, str(Path(__file__).parent))
from k3lib import IRF, _iv  # noqa: E402

iv.dps = 60
OUT = Path(__file__).resolve().parents[1]


class SeshPath:
    def __init__(self, r: F, tg: F, tau_m: F) -> None:
        self.r, self.tg, self.tau_m = r, tg, tau_m
        self.alpha = iv.log(1 + _iv(r)) - 1 / _iv(tau_m)
        self.pieces = [(iv.mpf(0), _iv(tg), iv.mpf(1), self.alpha),
                       (_iv(tg), None, iv.exp(self.alpha * _iv(tg)), -1 / _iv(tau_m))]

    def piece_of(self, t):
        """Index of the piece containing the whole interval t (error if it straddles the breakpoint)."""
        tg = _iv(self.tg)
        if t.b <= tg.a:
            return 0
        if t.a >= tg.b:
            return 1
        raise ValueError("interval straddles tg")

    def x_and_m(self, irf: IRF, t):
        """Returns (m(t), m'(t), [x_i(t)]) for the decaying modes i = 1..n."""
        k = self.piece_of(t)
        xs = []
        for ti in irf.tau:
            s = 1 / _iv(ti)
            tot = iv.mpf(0)
            for j, (za, zb, ma, rate) in enumerate(self.pieces):
                if j > k:
                    break
                top = t if j == k else zb
                w = top - za
                tot += ma * iv.exp(-(t - top) * s) * (iv.exp(rate * w) - iv.exp(-s * w)) / (rate + s)
            xs.append(tot)
        za, zb, ma, rate = self.pieces[k]
        m = ma * iv.exp(rate * (t - za))
        return m, rate * m, xs

    def du(self, irf: IRF, t):
        m, mp_, xs = self.x_and_m(irf, t)
        return m - sum(_iv(a) / _iv(ti) * x for a, ti, x in zip(irf.a, irf.tau, xs))

    def ddu(self, irf: IRF, t):
        m, mp_, xs = self.x_and_m(irf, t)
        sa = sum(_iv(a) / _iv(ti) for a, ti in zip(irf.a, irf.tau))
        return mp_ - m * sa + sum(_iv(a) / _iv(ti) ** 2 * x for a, ti, x in zip(irf.a, irf.tau, xs))

    def du_float(self, irf: IRF, t: float) -> float:
        tf = F(t).limit_denominator(10**9)
        k = 0 if tf < self.tg else 1
        tt = tf if k == 0 else tf
        # use a degenerate-ish interval; fine for float scanning
        try:
            v = self.du(irf, iv.mpf(float(t)))
        except ValueError:
            v = self.du(irf, iv.mpf(float(t)) + iv.mpf([1e-12, 1e-12]))
        return float(v.mid)


def du_np(path: SeshPath, irf: IRF, ts: np.ndarray) -> np.ndarray:
    r, tg, tm = float(path.r), float(path.tg), float(path.tau_m)
    al = math.log1p(r) - 1 / tm
    out = np.zeros_like(ts)
    for idx, t in enumerate(ts):
        pieces = [(0.0, tg, 1.0, al), (tg, None, math.exp(al * tg), -1 / tm)]
        k = 0 if t <= tg else 1
        m = pieces[k][2] * math.exp(pieces[k][3] * (t - pieces[k][0]))
        acc = 0.0
        for a, ti in zip(irf.a, irf.tau):
            s = 1 / float(ti)
            x = 0.0
            for j, (za, zb, ma, rate) in enumerate(pieces):
                if j > k:
                    break
                top = t if j == k else zb
                x += ma * math.exp(-(t - top) * s) * (math.exp(rate * (top - za)) - math.exp(-s * (top - za))) / (rate + s)
            acc += float(a) * s * x
        out[idx] = m - acc
    return out


def peak(path: SeshPath, irf: IRF, tmax: float = 6000.0) -> dict:
    ts = np.concatenate([np.linspace(0.05, 400, 8000), np.linspace(400, tmax, 6000)[1:]])
    # avoid exact tg
    ts = ts[np.abs(ts - float(path.tg)) > 1e-6]
    vals = du_np(path, irf, ts)
    sc = [(i) for i in range(len(vals) - 1) if vals[i] > 0 >= vals[i + 1]]
    up = [(i) for i in range(len(vals) - 1) if vals[i] < 0 <= vals[i + 1]]
    out: dict = {"float_sign_changes_plus_to_minus": [round(float(ts[i + 1]), 3) for i in sc],
                 "float_sign_changes_minus_to_plus": [round(float(ts[i + 1]), 3) for i in up],
                 "float_u_prime_at_tmax": float(vals[-1])}
    if not sc:
        out["status"] = "NO_PEAK_FOUND_in_[0,%g] (u' stays positive); Seshadri eq.(10) regime" % tmax
        return out
    i = sc[0]
    lo, hi = F(float(ts[i])).limit_denominator(1000), F(float(ts[i + 1])).limit_denominator(1000)
    # make sure bracket does not straddle tg
    tg = path.tg
    if lo < tg < hi:
        out["status"] = "bracket straddles tg"
        return out
    lo, hi = lo - F(1, 100), hi + F(1, 100)
    if lo < tg < hi:
        lo = max(lo, tg + F(1, 1000)) if lo > tg - F(1, 50) else lo
    try:
        s_lo = path.du(irf, _iv(lo))
        s_hi = path.du(irf, _iv(hi))
        curv = path.ddu(irf, iv.mpf([float(lo) - 1e-9, float(hi) + 1e-9]))
    except ValueError as e:
        out["status"] = "straddle: " + str(e)
        return out
    ok = bool(s_lo.a > 0) and bool(s_hi.b < 0) and bool(curv.b < 0)
    out["bracket_initial"] = [str(lo), str(hi)]
    out["u_prime_lo_hi"] = [float(s_lo.mid), float(s_hi.mid)]
    out["u_second_upper_bound_on_bracket"] = float(curv.b.mid)
    if not ok:
        out["status"] = "BRACKET_NOT_CERTIFIED"
        return out
    a, b = lo, hi
    for _ in range(60):
        mid = (a + b) / 2
        s = path.du(irf, _iv(mid))
        if s.a > 0:
            a = mid
        elif s.b < 0:
            b = mid
        else:
            break
    out["status"] = "CERTIFIED"
    out["t2_enclosure"] = [str(a), str(b)]
    out["t2_enclosure_float"] = [float(a), float(b)]
    # t1
    if bool(path.alpha.a > 0):
        t1 = path.tg
        out["t1"] = "tg=%s (alpha>0 certified)" % tg
    elif bool(path.alpha.b < 0):
        t1 = F(0)
        out["t1"] = "0 (alpha<0 certified: emissions nonincreasing from t0)"
    else:
        out["status"] = "alpha sign not certified"
        return out
    out["delay_enclosure_float"] = [float(a - t1), float(b - t1)]
    out["delay_enclosure_exact"] = [str(a - t1), str(b - t1)]
    return out


def main() -> None:
    joos = IRF.joos()
    sesh_eq1 = IRF(F("0.217"), [F("0.224"), F("0.282"), F("0.276")], [F(394), F("36.5"), F("4.30")])
    sesh_44 = IRF(F("0.217"), [F("0.224"), F("0.282"), F("0.276")], [F(394), F("36.5"), F("4.4")])
    variants = {"joos_table5": joos, "seshadri_eq1_printed_tau4.30": sesh_eq1, "seshadri_text_tau4.4": sesh_44}
    res: dict = {"scenarios": {}}
    tg = F(60)
    # positive control: single exponential, m(t) = exp(-t/tau_m) only (r=0 so alpha=-1/tau_m): closed-form peak? use
    # IRF = 1 exponential tau=30, m = exp(-t/50): u' = m - x/30, x=(e^{-t/50}-e^{-t/30})/(1/30-1/50) -> u'(0)=1>0 and u'>0 for all t>0
    # (u' = e^{-t/30}... ) so NO peak: the checker must report no peak.
    one = IRF(F(0), [F(1)], [F(30)])
    res["control_single_exponential_no_peak"] = peak(SeshPath(F(0), tg, F(50)), one, 2000.0)
    # control 2: a case with exact closed form: h = e^{-t/tau}, m = e^{-t/tm} gives u = (e^{-t/tm}-e^{-t/tau})/(1/tau-1/tm)... monotone
    for name, irfx in variants.items():
        for r in (F(3, 100), F(5, 100), F(15, 1000)):
            for tm in (20, 40, 50, 60, 80, 100, 120):
                key = f"{name}|r={r}|tau_m={tm}"
                try:
                    res["scenarios"][key] = peak(SeshPath(r, tg, F(tm)), irfx)
                except Exception as e:  # noqa: BLE001
                    res["scenarios"][key] = {"status": "ERROR " + repr(e)}
                print(key, res["scenarios"][key].get("status"), res["scenarios"][key].get("delay_enclosure_float"), flush=True)
    json.dump(res, open(OUT / "data" / "results_b.json", "w"), indent=1)


if __name__ == "__main__":
    main()
