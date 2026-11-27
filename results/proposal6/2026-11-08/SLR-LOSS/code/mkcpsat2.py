"""Derive cpsat2.py (generalised gain g, rational open radius rp/rq) from SLR-EXT/code/cpsat_rule.py."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "../../../2026-11-07/SLR-EXT/code/cpsat_rule.py")
t = open(S).read()
reps = [
    ("def build_and_solve(N: int, J: int,", "def build_and_solve(N: int, J: int, g: int, rp: int, rq: int,"),
    ("    n = N - 1\n    D = 8", "    n = N - g\n    D = 8"),
    ("M = 2 * L * D * N  # scaled", "M = 2 * L * D * rq  # scaled"),
    ("step = D * N * f", "step = D * rq * f"),
    ("base = -a * N * f", "base = -a * rq * f"),
    ("half = D * f\n", "half = rp * D * f\n"),
    ("covers_open(v, a, D, 1, n + 1)[0]", "covers_open(v, a, D, info['rp'], info['rq'])[0]"),
    ('"delta_num": 1, "delta_den": n + 1,\n            "delta": f"1/{n + 1}"',
     '"delta_num": info["rp"], "delta_den": info["rq"],\n            "delta": f"{info[\'rp\']}/{info[\'rq\']}"'),
    ('info = {"N": N, "n": n,', 'info = {"rp": rp, "rq": rq, "g": g, "N": N, "n": n,'),
    ('info.update({"v": v, "a": a, "D": D})', 'info.update({"v": v, "a": a, "D": D, "rp": rp, "rq": rq})'),
    ('cert_n{n:03d}.json', "cert_n{n:03d}_g{info['g']}_{meta.get('tag', 'x')}.json"),
    ('    ap.add_argument("tag")',
     '    ap.add_argument("tag")\n    ap.add_argument("--g", type=int, default=1)\n    ap.add_argument("--rp", type=int, default=1)\n    ap.add_argument("--rq", type=int, default=0)'),
    ("info = build_and_solve(N, a.J, a.tlimit,", "info = build_and_solve(N, a.J, a.g, a.rp, a.rq or N, a.tlimit,"),
    ("from slr_exact import", 'sys.path.insert(0, os.path.join(HERE, "../../../2026-11-07/SLR-EXT/code"))\nfrom slr_exact import'),
    ('os.path.join(HERE, "check_cover")', 'os.path.join(HERE, "../../../2026-11-07/SLR-EXT/code/check_cover")'),
]
for a, b in reps:
    assert a in t, a
    t = t.replace(a, b)
open(os.path.join(HERE, "cpsat2.py"), "w").write(t)
print("ok")
