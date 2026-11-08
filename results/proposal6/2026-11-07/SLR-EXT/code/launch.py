"""Launch detached run_even.py jobs. usage: launch.py budget seed logname n:core:rm n:core:rm ..."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
budget, seed, logname = sys.argv[1], sys.argv[2], sys.argv[3]
log = open(os.path.join(os.path.dirname(HERE), "logs", logname), "a")
for spec in sys.argv[4:]:
    n, core, *rm = spec.split(":")
    assert core != "0"
    subprocess.Popen(["python3", os.path.join(HERE, "run_even.py"), n, budget, core, seed] + [x for x in rm if x],
                     stdout=log, stderr=log, start_new_session=True)
print("launched", len(sys.argv) - 4)
