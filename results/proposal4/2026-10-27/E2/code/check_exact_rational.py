"""Exact-rational check of the seconds columns in certified_t_star.json (audit correction 1).
Usage: python3 check_exact_rational.py certified_t_star.json [auditor_mpmath_iv_json]
For each of 24 cases: Fraction(float t_lo_s) <= tau_lo*R^2/D and tau_hi*R^2/D <= Fraction(float t_hi_s),
with R^2/D from the decimal parameter strings in exact rational arithmetic. If an auditor JSON is given
(fields my_t = [lower-interval, upper-interval] strings), also checks it lies inside the seconds interval."""
import json
import re
import sys
from decimal import Decimal
from fractions import Fraction

P = json.load(open("results/proposal4/2026-10-27/E2/data/params_chen2020.json"))


def fr(s: str) -> Fraction:
    return Fraction(Decimal(s))


scale = fr(P["Negative particle radius [m]"]) ** 2 / fr(P["Negative particle diffusivity [m2.s-1]"])
recs = json.load(open(sys.argv[1]))
aud = json.load(open(sys.argv[2]))["cases"] if len(sys.argv) > 2 else None


def num(s: str) -> list:
    return [Fraction(Decimal(x)) for x in re.findall(r"-?\d+\.\d+(?:[eE][+-]?\d+)?", s)]


ok_tau = ok_aud = 0
for i, r in enumerate(recs):
    tl = Fraction(*map(int, r["tau_lo"].split("/"))) * scale
    th = Fraction(*map(int, r["tau_hi"].split("/"))) * scale
    a, b = Fraction(float(r["t_lo_s"])), Fraction(float(r["t_hi_s"]))
    c1 = a <= tl and th <= b
    ok_tau += c1
    c2 = None
    if aud:
        lo = min(num(aud[i]["my_t"][0]))
        hi = max(num(aud[i]["my_t"][1]))
        c2 = a <= lo and hi <= b
        ok_aud += c2
    print(r["C"], r["x0"], r["x_star"], "producer_tau*scale inside seconds:", c1, "| auditor inside seconds:", c2)
print("SUMMARY tau-interval inside seconds interval: %d/%d" % (ok_tau, len(recs)),
      "auditor enclosure inside: %s" % (("%d/%d" % (ok_aud, len(recs))) if aud else "n/a"))
