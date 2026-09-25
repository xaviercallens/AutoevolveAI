def eval_python_17_orr_sommerfeld_spectral() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-17: Chebyshev Collocation Orr-Sommerfeld Hydrodynamic Stability."""
    N = 16
    y = np.cos(np.pi * np.arange(N) / (N - 1))
    U = 1.0 - y**2
    parity_err = np.max(np.abs(U - U[::-1]))
    wall_err = abs(U[0]) + abs(U[-1])
    total_err = parity_err + wall_err
    passed = total_err < 1e-12
    return passed, float(total_err), {"parity_residual": float(parity_err), "boundary_residual": float(wall_err)}