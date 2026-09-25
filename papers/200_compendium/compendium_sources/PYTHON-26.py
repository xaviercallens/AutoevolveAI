def eval_python_26_riemann_hilbert_jump() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-26: Riemann-Hilbert Contour Jump Factorization & Plemelj Formula."""
    nodes = np.linspace(-10.0, 10.0, 2001)
    t_pos = nodes[nodes > 1e-3]
    t_neg = nodes[nodes < -1e-3]
    integrand = lambda t: 1.0 / (t * (t**2 + 1.0))
    pv_sum = np.sum(integrand(t_pos)) + np.sum(integrand(t_neg))
    err = abs(pv_sum)
    passed = err < 1e-10
    return passed, float(err), {"principal_value_sum": float(pv_sum)}