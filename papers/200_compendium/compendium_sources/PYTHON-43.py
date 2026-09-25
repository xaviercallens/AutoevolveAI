def eval_python_43_dirac_spectral_flow() -> tuple[bool, float, dict[str, Any]]:
    """Spectral flow of 1D Dirac operator H(Phi) = -i d/dx + Phi on circle S^1 under 2pi flux threading."""
    # Eigenvalues E_n(Phi) = 2pi n / L + Phi. Under Phi -> Phi + 2pi/L, spectrum shifts by 1 unit
    L = 1.0
    flux_0 = 0.0
    flux_1 = 2.0 * np.pi / L
    n_modes = 11
    evals_0 = [2.0 * np.pi * n / L + flux_0 for n in range(-5, 6)]
    evals_1 = [2.0 * np.pi * n / L + flux_1 for n in range(-5, 6)]
    # Shift of index
    flow = round((evals_1[5] - evals_0[5]) / (2 * np.pi / L))
    err = abs(flow - 1)
    passed = err == 0
    return passed, float(err), {"spectral_flow": flow}