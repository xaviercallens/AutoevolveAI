def eval_python_49_wigner_quasiprobability() -> tuple[bool, float, dict[str, Any]]:
    """Wigner phase space distribution W(x, p) = 1/pi hbar exp(-x^2 - p^2) integrating to marginal coordinate density rho(x)."""
    # For ground state: W(x,p) = 1/pi exp(-x^2 - p^2). Integral over p gives 1/sqrt(pi) exp(-x^2) = |psi_0(x)|^2
    x = 0.5
    psi_sq_exact = (1.0 / np.sqrt(np.pi)) * np.exp(-x**2)
    
    # Numerical integration over p
    p_grid = np.linspace(-5, 5, 201)
    dp = p_grid[1] - p_grid[0]
    W_vals = (1.0 / np.pi) * np.exp(-x**2 - p_grid**2)
    marginal_x = float(np.sum(W_vals) * dp)
    
    err = abs(marginal_x - psi_sq_exact)
    passed = err < 1e-6
    return passed, float(err), {"wigner_marginal_error": float(err)}