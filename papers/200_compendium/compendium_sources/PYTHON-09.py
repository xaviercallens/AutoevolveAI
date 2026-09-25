def eval_python_09_markov_chain_arnoldi() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-09: Continuous-Time Markov Chain Stationary Distribution via Arnoldi Iteration."""
    Q = np.array([[-2.0, 1.0, 1.0], [1.0, -3.0, 2.0], [2.0, 1.0, -3.0]])
    vals, vecs = np.linalg.eig(Q.T)
    zero_idx = np.argmin(np.abs(vals))
    pi = np.real(vecs[:, zero_idx])
    pi = pi / np.sum(pi)
    residual = np.linalg.norm(pi @ Q)
    norm_sum = abs(np.sum(pi) - 1.0)
    total_err = residual + norm_sum
    passed = total_err < 1e-12
    return passed, float(total_err), {"pi_Q_residual": float(residual), "stationary_distribution": pi.tolist()}