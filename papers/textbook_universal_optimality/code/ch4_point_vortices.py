"""N point vortices in the plane (Kirchhoff): conservation checks with a known answer and a negative control."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import OptimizeResult as OdeResult


def rhs(t: float, z: np.ndarray, gam: np.ndarray, power: int = 2) -> np.ndarray:
    """Velocity of each vortex: u_i = -(1/2pi) sum_j G_j (y_i-y_j)/r^p, v_i = (1/2pi) sum_j G_j (x_i-x_j)/r^p."""
    x, y = z[0::2], z[1::2]
    dx, dy = x[:, None] - x[None, :], y[:, None] - y[None, :]
    r2 = dx**2 + dy**2
    np.fill_diagonal(r2, 1.0)
    k = gam[None, :] / (2 * np.pi * r2 ** (power / 2))
    np.fill_diagonal(k, 0.0)
    out = np.empty_like(z)
    out[0::2], out[1::2] = -(k * dy).sum(1), (k * dx).sum(1)
    return out


def invariants(z: np.ndarray, gam: np.ndarray) -> tuple[float, float, float, float]:
    """Hamiltonian H = -(1/2pi) sum_{i<j} G_i G_j log r_ij, impulses P, Q and angular impulse I."""
    x, y = z[0::2], z[1::2]
    r = np.hypot(x[:, None] - x[None, :], y[:, None] - y[None, :])
    iu = np.triu_indices(len(gam), 1)
    h = -np.sum(np.outer(gam, gam)[iu] * np.log(r[iu])) / (2 * np.pi)
    return h, float(gam @ x), float(gam @ y), float(gam @ (x**2 + y**2))


def drift(sol: OdeResult, gam: np.ndarray) -> list[float]:
    """Max over output times of |invariant(t) - invariant(0)| (relative for H and I)."""
    inv = np.array([invariants(sol.y[:, k], gam) for k in range(sol.y.shape[1])])
    d = np.abs(inv - inv[0]).max(0)
    return [d[0] / abs(inv[0, 0]), d[1], d[2], d[3] / abs(inv[0, 3])]


# Known answer: a ring of n equal vortices (G = 1, radius R) rotates rigidly at omega = (n-1)/(4 pi R^2).
n, R, T = 5, 1.0, 20.0
th = 2 * np.pi * np.arange(n) / n
z0 = np.column_stack([R * np.cos(th), R * np.sin(th)]).ravel()
ring = solve_ivp(rhs, (0, T), z0, args=(np.ones(n),), method="DOP853", rtol=1e-12, atol=1e-12)
angle = np.unwrap(np.arctan2(ring.y[1], ring.y[0]))[-1]
print(f"ring n=5: omega numeric {angle / T:.12f}  exact {(n - 1) / (4 * np.pi * R**2):.12f}")

# Random mixed-sign system, two integrators.
rng = np.random.default_rng(2026)
N = 8
gam = rng.choice([-1.0, 1.0], N) * rng.uniform(0.5, 1.5, N)
z0 = rng.uniform(-1, 1, 2 * N)
t_eval = np.linspace(0, 10, 201)
for method in ("DOP853", "BDF"):
    sol = solve_ivp(rhs, (0, 10), z0, args=(gam,), method=method, rtol=1e-10, atol=1e-12, t_eval=t_eval)
    dH, dP, dQ, dI = drift(sol, gam)
    print(f"{method:6s} nfev={sol.nfev:6d}  rel dH={dH:.2e}  dP={dP:.2e}  dQ={dQ:.2e}  rel dI={dI:.2e}")

# Negative control: a 1/r kernel instead of 1/r^2 is not the gradient of the log Hamiltonian.
bad = solve_ivp(rhs, (0, 10), z0, args=(gam, 1), method="DOP853", rtol=1e-10, atol=1e-12, t_eval=t_eval)
print("control (1/r kernel): rel dH={:.2e}  dP={:.2e}  dQ={:.2e}  rel dI={:.2e}".format(*drift(bad, gam)))
