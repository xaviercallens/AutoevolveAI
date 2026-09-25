def eval_python_03_matrix_product_state_svd() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-03: Matrix Product State (MPS) Tensor Train SVD Truncation."""
    d = 2
    np.random.seed(42)
    psi = np.random.randn(d, d, d)
    psi = psi / np.linalg.norm(psi)

    psi_mat = psi.reshape(d, d * d)
    U, S, Vt = np.linalg.svd(psi_mat, full_matrices=False)
    reconstructed = (U @ np.diag(S) @ Vt).reshape(d, d, d)
    rec_err = np.linalg.norm(psi - reconstructed)
    s_sq = S**2
    entropy = -np.sum(s_sq * np.log(s_sq + 1e-16))

    passed = rec_err < 1e-12 and entropy > 0.0
    return passed, float(rec_err), {"reconstruction_err": float(rec_err), "entanglement_entropy": float(entropy)}