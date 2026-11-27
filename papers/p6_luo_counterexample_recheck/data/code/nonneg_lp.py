"""Is the 2-quad-type direction (x1,y1)=(1,1) the quad projection of a NONNEGATIVE Haken solution (triangles >= 0)? LP feasibility."""
import json, os, sys
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *
from m12_structure import PAIRINGS
gl = spec_from_pairings(PAIRINGS)
H = np.array(haken_matching(gl), float)
n = 2
tri_idx = [7 * t + i for t in range(n) for i in range(4)]
quad_idx = quad_cols(n)
target = [1, 0, 0, 1, 0, 0]
A = H[:, tri_idx]
bvec = -H[:, quad_idx] @ np.array(target, float)
r = linprog(np.zeros(8), A_eq=A, b_eq=bvec, bounds=[(0, None)] * 8, method="highs")
print(json.dumps({"feasible_nonneg_haken_with_quads_(1,0,0,1,0,0)": bool(r.status == 0), "triangle_coords": list(map(float, r.x)) if r.status == 0 else None}))
