def eval_python_13_nmf_kullback_leibler() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-13: Non-Negative Matrix Factorization (KL Divergence Monotonicity)."""
    np.random.seed(99)
    V = np.random.uniform(0.1, 1.0, (6, 4))
    W = np.random.uniform(0.1, 1.0, (6, 2))
    H = np.random.uniform(0.1, 1.0, (2, 4))

    def kl_div(A: np.ndarray, B: np.ndarray) -> float:
        return float(np.sum(A * np.log((A + 1e-15) / (B + 1e-15)) - A + B))

    kl_0 = kl_div(V, W @ H)
    for _ in range(25):
        WH = W @ H
        H = H * ((W.T @ (V / WH)) / (np.sum(W, axis=0, keepdims=True).T + 1e-15))
        WH = W @ H
        W = W * (((V / WH) @ H.T) / (np.sum(H, axis=1, keepdims=True).T + 1e-15))

    kl_end = kl_div(V, W @ H)
    reduction = kl_0 - kl_end
    passed = reduction > 0.0 and kl_end < kl_0
    return passed, float(kl_end), {"kl_initial": kl_0, "kl_final": kl_end, "reduction": reduction}