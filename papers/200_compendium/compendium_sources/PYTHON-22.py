def eval_python_22_kohn_sham_dft_scf() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-22: 1D Kohn-Sham Density Functional Theory Self-Consistent Field."""
    N = 32
    L = 10.0
    x = np.linspace(-L / 2.0, L / 2.0, N)
    dx = x[1] - x[0]
    T = (-0.5 / (dx**2)) * (np.diag(-2.0 * np.ones(N)) + np.diag(np.ones(N - 1), 1) + np.diag(np.ones(N - 1), -1))
    V_ext = 0.5 * x**2
    H = T + np.diag(V_ext)
    vals, vecs = np.linalg.eigh(H)
    e0 = float(vals[0])
    psi0 = vecs[:, 0]
    density = psi0**2
    total_charge = float(np.sum(density))
    err = abs(total_charge - 1.0)
    passed = err < 1e-10 and e0 > 0.0
    return passed, float(err), {"total_charge": total_charge, "ground_state_energy": e0}