"""Run cover_ls_fast from even-base init, one process per core. usage: run_even.py n budget core seed rm... -> prints END line."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mk_even_init import make  # noqa: E402

n, budget, core, seed = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rm = {int(x) for x in sys.argv[5:]}
tmp = os.path.join(os.path.dirname(HERE), "logs", "tmp")
os.makedirs(tmp, exist_ok=True)
tag = f"n{n}_c{core}_s{seed}_" + "-".join(map(str, sorted(rm)))
init = os.path.join(tmp, f"init_{tag}.txt")
out = os.path.join(tmp, f"out_{tag}.txt")
make(n, init, rm)
q = n + 1
env = dict(os.environ, SLR_INIT=init, SLR_FREE=str(max(len(rm) - 1, 1)))
r = subprocess.run(["taskset", "-c", str(core), os.path.join(HERE, "cover_ls_fast"), str(n), str(8 * q - 1), str(8 * q * q),
                    str(seed), str(budget), out, f"swap{2 * q + 4}"], capture_output=True, text=True, env=env)
print(tag, r.returncode, [ln for ln in r.stderr.splitlines() if ln.startswith("END")][-1:] or r.stderr[-200:])
