from fractions import Fraction as F
import numpy as np
from k3lib import IRF
from k3lib import from_nodes
irf=IRF.joos()
for L in [F(1,10),F(15,100),F(2,10),F(25,100),F(3,10)]:
  for zd in [12,20]:
    nodes=[(F(0),F(0)),(F(10),F(1)),(F(10+zd),L),(F(300),L),(F(310),F(0))]
    p=from_nodes(nodes)
    ts=np.linspace(0.05,700,14000)
    u=np.array([p.u_float(irf,t) for t in ts]); d=np.diff(u)
    print(L,zd,[(round(ts[i+1],1),round(u[i+1],3)) for i in range(len(d)-1) if d[i]>0>=d[i+1]], [round(ts[i+1],1) for i in range(len(d)-1) if d[i]<0<=d[i+1]])
