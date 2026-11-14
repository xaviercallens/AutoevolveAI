"""PyCO2SYS cross-check at random points (auditor seed) + omitted-term effects."""
import sys, random, json
sys.path.insert(0, '/tmp/k2audit')
from model import *
import PyCO2SYS as pyco2
mp.dps = 30
BOX = {"T": (0.0, 30.0), "S": (30.0, 38.0), "f": (280.0, 560.0), "TA35": (2200.0, 2400.0)}
rng = random.Random(777)
pts = [tuple(rng.uniform(*BOX[k]) for k in ("T", "S", "f", "TA35")) for _ in range(200)]
pts += [(30.0, 38.0, 280.0, 2400.0), (0.0, 30.0, 560.0, 2200.0)]


def py_eta(t, s, f, ta, **extra):
    kw = dict(par1_type=1, par2=f, par2_type=5, salinity=s, temperature=t, opt_k_carbonic=10, opt_pH_scale=1,
              opt_total_borate=1)
    kw.update(extra)
    d = 0.01
    return float((pyco2.sys(par1=ta + d, **kw)["dic"] - pyco2.sys(par1=ta - d, **kw)["dic"]) / (2*d))


res = {"n": len(pts)}
worst_plain = worst_matched = 0.0
eff = {"sulf_fluor": [], "phos2_sil100": [], "phos3_sil150_full": []}
for (t, s, f, ta35) in pts:
    ta = ta35*s/35
    e, h, c = eta_point(t, s, f, ta35)
    e = float(e)
    base0 = py_eta(t, s, f, ta, total_sulfate=0, total_fluoride=0)
    worst_plain = max(worst_plain, abs(base0 - e)/e)
    m = py_eta(t, s, f, ta, total_sulfate=0, total_fluoride=0, k_water=float(c["KW"]), total_borate=float(c["BT"])*1e6)
    worst_matched = max(worst_matched, abs(m - e)/e)
    full = py_eta(t, s, f, ta)
    eff["sulf_fluor"].append(full - base0)
    eff["phos2_sil100"].append(py_eta(t, s, f, ta, total_phosphate=2, total_silicate=100) - full)
    eff["phos3_sil150_full"].append(py_eta(t, s, f, ta, total_phosphate=3, total_silicate=150) - base0)
res["worst_rel_vs_pyco2sys_sulfate_fluoride_0"] = worst_plain
res["worst_rel_vs_pyco2sys_matched_KW_BT"] = worst_matched
res["effects_abs_eta_min_max"] = {k: [min(v), max(v)] for k, v in eff.items()}
print(json.dumps(res, indent=1))
