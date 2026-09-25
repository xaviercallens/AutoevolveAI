def eval_python_21_fractional_diffusion_caputo() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-21: Fractional Diffusion Equation Solver via Caputo Derivative."""
    t = 1.0
    alpha = 0.5
    analytic = (math.gamma(3.0) / math.gamma(3.0 - alpha)) * (t ** (2.0 - alpha))
    N = 100
    dt = t / N
    t_grid = np.linspace(0, t, N + 1)
    f_vals = t_grid**2
    k = np.arange(N)
    b = (k + 1) ** (1.0 - alpha) - k ** (1.0 - alpha)
    diffs = f_vals[1:] - f_vals[:-1]
    approx = (1.0 / (math.gamma(2.0 - alpha) * (dt**alpha))) * np.sum(b * diffs[::-1])
    err = abs(approx - analytic) / analytic
    passed = err < 0.05
    return passed, float(err), {"analytic": float(analytic), "approx": float(approx), "rel_err": float(err)}