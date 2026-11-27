"""Verify one new certificate: both exact checkers at the stated radius, exact gamma, failure at gamma, cover just above.
usage: verify_cert.py cert.json  -> JSON line"""
import json
import os
import subprocess
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "../../../2026-11-07/SLR-EXT/code")
sys.path.insert(0, HERE)
sys.path.insert(0, EXT)
from gamma_fast import gamma_exact  # noqa: E402
from slr_exact import covers_open  # noqa: E402

p = sys.argv[1]
c = json.load(open(p))
v = [int(x) for x in c["v"]]
a = [int(x) for x in c["a"]]
D = int(c["D"])
r = Fr(int(c["delta_num"]), int(c["delta_den"]))
assert len(v) == len(set(v)) == int(c["n"]) and min(v) >= 1
ck1 = covers_open(v, a, D, r.numerator, r.denominator)[0]
ck2 = subprocess.run([os.path.join(EXT, "check_cover"), p], capture_output=True, text=True).stdout.strip()
g = gamma_exact(v, a, D, r)
n = len(v)
print(json.dumps({"file": os.path.basename(p), "n": n, "radius": str(r), "checker1": ck1, "checker2": ck2,
                  "gamma": str(g["gamma"]), "gamma_float": float(g["gamma"]), "inv_gamma": float(1 / g["gamma"]),
                  "E_cert": float(1 / g["gamma"]) - n - 1, "fails_at_gamma": not g["open_cover_at_gamma"],
                  "covers_above": g["open_cover_above"], "exact_ok": g["ok"]}))
