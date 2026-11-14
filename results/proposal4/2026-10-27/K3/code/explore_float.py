import sys
sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal4/2026-10-27/K3/code")
from fractions import Fraction as F
import numpy as np
from k3lib import IRF, Path
irf = IRF.joos()
for B1, z2, z3 in [(F(9,10),5,200),(F(8,10),5,200),(F(9,10),10,300),(F(95,100),5,300)]:
    p = Path(steps=[(F(0),F(1)),(F(z2),-B1),(F(z3),-(1-B1))])
    ts = np.linspace(0.01, 600, 6000)
    u = np.array([p.u_float(irf, t) for t in ts])
    d = np.diff(u)
    mx = [(round(ts[i+1],1), round(u[i+1],4)) for i in range(len(d)-1) if d[i]>0>=d[i+1]]
    print(B1, z2, z3, mx)
