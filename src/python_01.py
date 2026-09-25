import numpy as np
grad_v = lambda q: q + np.array([0.2 * q[0] * (q[1] ** 2), 0.2 * (q[0] ** 2) * q[1]])
print("Gradient function compiled.")