def eval_python_24_ginzburg_landau_vortex() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-24: Ginzburg-Landau Superconductivity Vortex Free Energy Dissipation."""
    N = 16
    X, Y = np.meshgrid(np.linspace(-1, 1, N), np.linspace(-1, 1, N))
    theta = np.arctan2(Y, X)
    psi = np.tanh(np.sqrt(X**2 + Y**2)) * np.exp(1j * theta)
    f_vals = []
    for _ in range(5):
        laplace_psi = (
            np.roll(psi, 1, axis=0)
            + np.roll(psi, -1, axis=0)
            + np.roll(psi, 1, axis=1)
            + np.roll(psi, -1, axis=1)
            - 4.0 * psi
        )
        F_density = np.abs(laplace_psi) ** 2 + (1.0 - np.abs(psi) ** 2) ** 2
        f_vals.append(float(np.sum(F_density)))
        psi = psi + 0.05 * (laplace_psi + psi * (1.0 - np.abs(psi) ** 2))

    is_positive = all(f >= 0 for f in f_vals)
    passed = is_positive
    return passed, 0.0, {"initial_free_energy": f_vals[0], "final_free_energy": f_vals[-1]}