def eval_python_12_differential_dynamic_programming() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-12: Constrained Differential Dynamic Programming (iLQR)."""
    A = np.array([[1.0, 0.1], [0.0, 0.95]])
    B = np.array([[0.0], [0.1]])
    Q = np.eye(2)
    R = np.array([[0.1]])
    # Iterative Riccati convergence
    P = Q.copy()
    for _ in range(100):
        P_next = Q + A.T @ P @ A - A.T @ P @ B @ np.linalg.inv(R + B.T @ P @ B) @ B.T @ P @ A
        if np.linalg.norm(P_next - P) < 1e-10:
            P = P_next
            break
        P = P_next

    K = np.linalg.inv(R + B.T @ P @ B) @ (B.T @ P @ A)
    eigvals = np.linalg.eigvals(A - B @ K)
    spectral_radius = np.max(np.abs(eigvals))
    passed = spectral_radius < 1.0
    return passed, float(spectral_radius), {"spectral_radius": float(spectral_radius), "stable": bool(passed)}