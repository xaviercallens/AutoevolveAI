import os
import subprocess
import sys

H = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(H, "sweep2.py")
subprocess.run([sys.executable, S, "cpsat_smooth_cont.log", "600", "8", "smooth", "72"])
subprocess.run([sys.executable, S, "cpsat_smooth_J16.log", "120", "16", "smooth"] + [str(n) for n in range(63, 39, -1)])
