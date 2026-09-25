def eval_python_27_spherical_harmonics_wigner() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-27: Spherical Harmonics Addition Theorem Invariance."""
    # Addition theorem for l=1: sum_{m=-1}^1 |Y_1^m(theta, phi)|^2 = (2*1 + 1) / (4 pi) = 3 / (4 pi)
    theta = np.pi / 4.0
    phi = np.pi / 3.0
    # Analytic Y_1^0 = 0.5 * sqrt(3 / pi) * cos(theta)
    # Y_1^{1} = -0.5 * sqrt(3 / (2 pi)) * sin(theta) e^{i phi}
    # Y_1^{-1} = 0.5 * sqrt(3 / (2 pi)) * sin(theta) e^{-i phi}
    y_1_0 = 0.5 * np.sqrt(3.0 / np.pi) * np.cos(theta)
    y_1_1 = -0.5 * np.sqrt(3.0 / (2.0 * np.pi)) * np.sin(theta) * np.exp(1j * phi)
    y_1_m1 = 0.5 * np.sqrt(3.0 / (2.0 * np.pi)) * np.sin(theta) * np.exp(-1j * phi)

    sum_y_sq = np.abs(y_1_0) ** 2 + np.abs(y_1_1) ** 2 + np.abs(y_1_m1) ** 2
    expected = 3.0 / (4.0 * np.pi)
    err = abs(sum_y_sq - expected)
    passed = err < 1e-12
    return passed, float(err), {"sum_y_sq": float(sum_y_sq), "expected": float(expected), "err": float(err)}