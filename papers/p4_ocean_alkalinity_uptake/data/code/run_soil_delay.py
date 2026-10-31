"""Part (b) soil/dilute water (Tier X: freshwater K1,K2 only from PyCO2SYS's M79 transcription) and part (c) delay."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from mpmath import iv

sys.path.insert(0, str(Path(__file__).parent))
import k2lib as K  # noqa: E402

PK_FW_SIGMA = 0.02  # ASSUMED +-pK on the freshwater K1, K2 (not sourced)


def fresh_consts(t_rng: tuple[float, float], nsigma: float) -> dict:
    t = iv.mpf(t_rng)
    parts = []
    nt = 20
    for i in range(nt):
        ti = iv.mpf([t.a + (t.b - t.a) * i / nt, t.a + (t.b - t.a) * (i + 1) / nt])
        TK = ti + iv.mpf("273.15")
        ln_k0, _, _, _, ln_kw = K._logs(ti, iv.mpf(0), {})
        lnK1 = iv.mpf("290.9097") - iv.mpf("14554.21") / TK - iv.mpf("45.0575") * iv.log(TK)
        lnK2 = iv.mpf("207.6548") - iv.mpf("11843.79") / TK - iv.mpf("33.6485") * iv.log(TK)
        parts.append((ln_k0, lnK1, lnK2, ln_kw))
    ln_k0, lnK1, lnK2, ln_kw = (K._hull([p[k] for p in parts]) for k in range(4))
    dd = iv.mpf([-nsigma * PK_FW_SIGMA, nsigma * PK_FW_SIGMA]) * K.LN10
    return {"K0": iv.exp(ln_k0), "K1": iv.exp(lnK1 + dd), "K2": iv.exp(lnK2 + dd), "KW": iv.exp(ln_kw),
            "KB": iv.mpf(1), "BT": iv.mpf(0)}


def eta_f(h: object, c: dict, f: float) -> object:
    return K.eta_at(h, c, iv.mpf(f))


def decreasing_cert(h: object, c: dict, f: float) -> bool:
    C = c["K0"] * iv.mpf(f) * iv.mpf("1e-6")
    k1, k2, kw = c["K1"], c["K2"], c["KW"]
    absq = 2 * k2 * kw / h**2 + 2 * h + 6 * k2
    return (2 * C * k1 * k2 / h**2 - absq).b < 0  # d eta/dh < 0


def threshold(c: dict, f: float, eps: float, tmid: float) -> dict:
    # float bisection on the nominal midpoint constants
    cm = {k: iv.mpf(float(v.a) / 2 + float(v.b) / 2) if k != "BT" else v for k, v in c.items()}
    lo, hi = 1e-7, 1e-2
    for _ in range(200):
        mid = (lo * hi) ** 0.5
        e = eta_f(iv.mpf(mid), cm, f)
        if float(e.mid) > eps:
            lo = mid
        else:
            hi = mid
    h0 = (lo * hi) ** 0.5
    delta = 1e-3
    for _ in range(30):
        h1, h2 = iv.mpf(h0 * (1 - delta)), iv.mpf(h0 * (1 + delta))
        if eta_f(h1, c, f).a > eps and eta_f(h2, c, f).b < eps and decreasing_cert(iv.mpf([h0 * (1 - delta), h0 * (1 + delta)]), c, f):
            ph_lo = float(-iv.log(h2) / K.LN10 * 1) if False else float((-iv.log(iv.mpf(h0 * (1 + delta))) / iv.log(iv.mpf(10))).a)
            ph_hi = float((-iv.log(iv.mpf(h0 * (1 - delta))) / iv.log(iv.mpf(10))).b)
            return {"pH_lo": ph_lo, "pH_hi": ph_hi, "delta": delta}
        delta *= 2
    return {"pH_lo": None, "pH_hi": None, "note": "not certified"}


def soil() -> dict:
    out = {}
    for ns in (0.0, 1.0):
        for (t0, t1) in ((0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)):
            c = fresh_consts((t0, t1), ns)
            for f in (420.0, 2000.0, 10000.0, 50000.0):
                for eps in (0.01, 0.1, 0.5):
                    out[f"ns={ns}|T=[{t0},{t1}]|f={f}|eps={eps}"] = threshold(c, f, eps, 0.5 * (t0 + t1))
    return out


# --- part (c) -------------------------------------------------------------------------------------------------
def delay_closed_form() -> dict:
    """T = (L/q) (eps_w + 10 dbeta (1-eps) rho CEC / dc);  R = 1 + dq/dc;  dq = 10 dbeta CEC (1-eps) rho / eps_w."""
    f = iv.mpf
    db, por, ew, rho, dc, v = f("0.44"), f("0.3"), f("0.1"), f("2.65"), f("0.8"), f(5)
    res = {}
    for name, cec in (("sum_CEC_0.56", f("0.56")), ("direct_CEC_1.6", f("1.6"))):
        dq = 10 * db * cec * (1 - por) * rho / ew
        R = 1 + dq / dc
        vf = v / R
        res[name] = {"dq_meq_per_L": [float(dq.a), float(dq.b)], "R": [float(R.a), float(R.b)],
                     "v_cm_per_yr": [float(vf.a) * 100, float(vf.b) * 100], "yr_per_m": [float((R / v).a), float((R / v).b)]}
    res["printed"] = {"dq": [45.4, 131.3], "R": [58, 165], "v_cm_per_yr": [3.0, 8.7], "yr_per_m": "12-34"}
    # delay table T(CEC, L, q) over a grid of boxes: monotone, so corner values; intervals for rigor
    tab = {}
    for (c0, c1) in ((0.5, 1.0), (1.0, 2.0), (2.0, 5.0)):
        for (q0, q1) in ((0.25, 0.5), (0.5, 1.0)):
            cec, L, q = f([c0, c1]), f(1), f([q0, q1])
            T = L / q * (ew + 10 * db * (1 - por) * rho * cec / dc)
            tab[f"CEC=[{c0},{c1}]|q=[{q0},{q1}] m/yr|L=1m"] = [float(T.a), float(T.b)]
    res["delay_yr_per_m_table"] = tab
    # sensitivity (Tier X, assumed +-10% on the other inputs)
    s10 = lambda x: f([float(x.mid) * 0.9, float(x.mid) * 1.1])
    cec = f([0.56, 1.6])
    T = (1 / v) * (1 + 10 * s10(db) * cec * (1 - por) * rho / (ew * s10(dc)))  # v = q/ew with q = v*ew
    res["sensitivity_X_10pct_on_dbeta_dc_yr_per_m"] = [float(T.a), float(T.b)]
    return res


if __name__ == "__main__":
    outdir = Path(sys.argv[1])
    (outdir / "delay_result.json").write_text(json.dumps(delay_closed_form(), indent=1))
    print(json.dumps(delay_closed_form(), indent=1)[:1500])
    s = soil()
    (outdir / "soil_result.json").write_text(json.dumps(s, indent=1))
    for k in list(s)[:12]:
        print(k, s[k])
