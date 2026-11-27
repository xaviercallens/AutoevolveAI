"""Resumable Robertson driver.  usage: sage --python3 run_robertson.py CKPT LOG CPU_CAP_SECONDS [p] [tau] [Tlist...]
Outputs times default: 0.1,0.4,1,4,10,40,100,400,1000,4000,10000,40000.  Rerun the same command to resume."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from ph2_enclose import *

ckpt, logp, cap = sys.argv[1], sys.argv[2], float(sys.argv[3])
p = int(sys.argv[4]) if len(sys.argv) > 4 else 28
tau = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-17
def _fx(x):  # output times are the exact doubles handed to the Rust solver (0.1 and 0.4 are not 1/10, 2/5)
    n, d = float(x).as_integer_ratio()
    return QQ(n) / QQ(d)
times = [_fx(x) for x in (sys.argv[6:] or ["0.1", "0.4", "1", "4", "10", "40", "100", "400", "1000", "4000", "10000", "40000"])]
log = open(logp, "a")
if os.path.exists(ckpt):
    d = json.load(open(ckpt))
    prev = d["res"].get("cpu_s", 0.0)
else:
    prev = 0.0
res = run(robertson(), [0, 0], times, p=p, tau=tau, ckpt=ckpt, log=log, cpu_cap_s=cap)
print("DONE", {k: v for k, v in res.items() if k not in ("outputs", "history")}, file=log, flush=True)
