def eval_python_23_sinkhorn_optimal_transport() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-23: Sinkhorn-Knopp Entropic Optimal Transport Wasserstein-2."""
    N = 10
    a = np.ones(N) / N
    b = np.ones(N) / N
    x = np.linspace(0, 1, N)
    y = np.linspace(0.5, 1.5, N)
    M = (x[:, None] - y[None, :]) ** 2
    eps = 0.1
    K = np.exp(-M / eps)
    u = np.ones(N)
    for _ in range(50):
        v = b / (K.T @ u + 1e-15)
        u = a / (K @ v + 1e-15)

    P = np.diag(u) @ K @ np.diag(v)
    row_err = np.max(np.abs(np.sum(P, axis=1) - a))
    col_err = np.max(np.abs(np.sum(P, axis=0) - b))
    total_err = row_err + col_err
    passed = total_err < 1e-6
    return passed, float(total_err), {"marginal_row_err": float(row_err), "marginal_col_err": float(col_err)}