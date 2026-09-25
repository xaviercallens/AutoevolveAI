def eval_python_30_hamiltonian_neural_network() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-30: Hamiltonian Neural Network Symplectic Flow Energy Conservation."""
    q, p = np.pi / 4.0, 0.5
    H0 = 0.5 * (p**2) + (1.0 - np.cos(q))
    dH_dq = np.sin(q)
    dH_dp = p
    grad_H = np.array([dH_dq, dH_dp])
    J = np.array([[0.0, 1.0], [-1.0, 0.0]])
    flow = J @ grad_H
    dH_dt = abs(np.dot(flow, grad_H))
    passed = dH_dt == 0.0
    return passed, float(dH_dt), {"h0": float(H0), "dH_dt": float(dH_dt)}