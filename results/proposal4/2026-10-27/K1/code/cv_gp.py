"""Python re-fit of MOF_Cv_Extrapolate.jl: GP with zero mean, kernel SE(ell, sf) + Const(sc), fixed
heteroscedastic observation noise sigma_Cv (noise=false in GaussianProcesses.optimize!), kernel log-parameters
fitted by maximising the log marginal likelihood from the Julia initial point (log 10, log 100, log 500).
Returns the latent mean, as predict_f does. Validated against the stored Cv arrays (see run_pc.py).

Change notice (NIST software licence): derived from NIST IntrinsicDACCycle v0.0.2, src/MOF_Cv_Extrapolate.jl
(NIST-developed software; NIST is acknowledged as the source; notice in NIST_NOTICE.txt). Modified work: translated
from Julia to Python by an AI agent on 2026-10-27; no change of the fitted model intended."""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def _kernel(x1: np.ndarray, x2: np.ndarray, p: np.ndarray) -> np.ndarray:
    ell, sf, sc = np.exp(p)
    d = x1[:, None] - x2[None, :]
    return sf ** 2 * np.exp(-0.5 * d ** 2 / ell ** 2) + sc ** 2


class CvGP:
    def __init__(self, temps: list[float], cv: list[float], cv_err: list[float]) -> None:
        self.x = np.asarray(temps, dtype=float)
        self.y = np.asarray(cv, dtype=float)
        self.noise = np.asarray(cv_err, dtype=float) ** 2
        p0 = np.log([10.0, 100.0, 500.0])
        res = minimize(self._nlml, p0, method="CG")  # GaussianProcesses.jl uses Optim ConjugateGradient
        self.p = res.x
        K = _kernel(self.x, self.x, self.p) + np.diag(self.noise)
        self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.y))

    def _nlml(self, p: np.ndarray) -> float:
        K = _kernel(self.x, self.x, p) + np.diag(self.noise)
        try:
            L = np.linalg.cholesky(K)
        except np.linalg.LinAlgError:
            return 1e30
        a = np.linalg.solve(L.T, np.linalg.solve(L, self.y))
        return float(0.5 * self.y @ a + np.log(np.diag(L)).sum() + 0.5 * len(self.y) * np.log(2 * np.pi))

    def __call__(self, t: np.ndarray) -> np.ndarray:
        ks = _kernel(np.asarray(t, dtype=float), self.x, self.p)
        return ks @ self.alpha
