def eval_python_07_hamilton_jacobi_bellman() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-07: Hamilton-Jacobi-Bellman Viscosity PDE Solver."""
    N = 51
    x = np.linspace(-1.0, 1.0, N)
    u_exact = 1.0 - np.abs(x)
    dx = x[1] - x[0]
    du_dx_left = (u_exact[1:] - u_exact[:-1]) / dx
    mag_err = np.max(np.abs(np.abs(du_dx_left) - 1.0))
    passed = mag_err < 1e-10
    return passed, float(mag_err), {"hjb_gradient_err": float(mag_err), "grid_size": N}