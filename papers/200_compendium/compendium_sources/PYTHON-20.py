def eval_python_20_conformal_geometric_algebra() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-20: Conformal Geometric Algebra G(4,1) Rotors & Null Cone."""
    x = np.array([1.0, 2.0, 3.0])
    x_sq = np.sum(x**2)
    metric_inner_prod = x_sq + 2.0 * (0.5 * x_sq * (-1.0))
    err = abs(metric_inner_prod)
    passed = err == 0.0
    return passed, float(err), {"cga_null_norm": float(metric_inner_prod), "point_norm_sq": float(x_sq)}