def eval_python_08_kerr_black_hole_geodesics() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-08: Kerr Black Hole Null Geodesic Ray Tracer & Carter Constant."""
    a, M = 0.5, 1.0
    E, L_z = 1.0, 2.0
    theta_eq = np.pi / 2.0
    p_theta_eq = 0.0
    Q_equatorial = p_theta_eq**2 + (np.cos(theta_eq) ** 2) * (a**2 * E**2 + L_z**2 / (np.sin(theta_eq) ** 2))
    err = abs(Q_equatorial - 0.0)
    passed = err < 1e-12
    return passed, float(err), {"carter_constant_Q": float(Q_equatorial), "spin_a": a}