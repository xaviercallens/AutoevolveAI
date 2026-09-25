def eval_python_47_burgers_hopf_cole() -> tuple[bool, float, dict[str, Any]]:
    """Non-linear viscous Burgers equation u_t + u u_x = nu u_xx linearizable via Hopf-Cole u = -2 nu phi_x / phi."""
    # For diffusion equation phi_t = nu phi_xx, fundamental solution phi(x,t) = 1/sqrt(4pi nu t) exp(-x^2 / 4 nu t)
    # Then u(x,t) = x / t
    nu = 0.1
    t = 2.0
    x = 1.0
    # Direct analytical prediction
    u_exact = x / t
    # Gradient of heat kernel
    phi = np.exp(-x**2 / (4 * nu * t))
    phi_x = -x / (2 * nu * t) * phi
    u_hopf_cole = -2 * nu * phi_x / phi
    err = abs(u_hopf_cole - u_exact)
    passed = err < 1e-12
    return passed, float(err), {"exact_hopf_cole_residual": float(err)}