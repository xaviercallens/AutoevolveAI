def eval_python_15_vqe_molecular_h2() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-15: Variational Quantum Eigensolver (VQE) Ground State Energy for H2."""
    g0, g1, g2, g3, g4 = -1.05, 0.40, 0.40, 0.01, 0.18
    I = np.eye(2)
    Z = np.array([[1, 0], [0, -1]])
    X = np.array([[0, 1], [1, 0]])
    H_mat = g0 * np.kron(I, I) + g1 * np.kron(Z, I) + g2 * np.kron(I, Z) + g3 * np.kron(Z, Z) + g4 * np.kron(X, X)

    eigvals = np.linalg.eigvalsh(H_mat)
    fci_energy = float(eigvals[0])

    thetas = np.linspace(-np.pi, np.pi, 200)
    vqe_energies = [
        float(np.real(np.array([np.cos(t), 0, 0, np.sin(t)]) @ H_mat @ np.array([np.cos(t), 0, 0, np.sin(t)])))
        for t in thetas
    ]
    min_vqe = min(vqe_energies)
    diff = abs(min_vqe - fci_energy)
    passed = diff < 1e-3
    return passed, float(diff), {"fci_energy": fci_energy, "min_vqe": min_vqe, "error": float(diff)}