def eval_python_05_se3_lie_algebra_exponential() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-05: SE(3) Lie Algebra Exponential & Rodrigues Map Invariance."""
    omega = np.array([0.1, -0.2, 0.3])
    theta = np.linalg.norm(omega)
    K = np.array([[0, -omega[2], omega[1]], [omega[2], 0, -omega[0]], [-omega[1], omega[0], 0]])
    R_rodrigues = np.eye(3) + (np.sin(theta) / theta) * K + ((1.0 - np.cos(theta)) / (theta**2)) * (K @ K)
    # Series expansion: sum K^m / m!
    R_series = np.eye(3)
    K_power = np.eye(3)
    factorial = 1.0
    for m in range(1, 14):
        factorial *= m
        K_power = K_power @ K
        R_series = R_series + K_power / factorial

    diff = np.linalg.norm(R_rodrigues - R_series, ord="fro")
    det_err = abs(np.linalg.det(R_rodrigues) - 1.0)
    total_err = diff + det_err
    passed = total_err < 1e-12
    return passed, float(total_err), {"rodrigues_diff": float(diff), "det_error": float(det_err)}