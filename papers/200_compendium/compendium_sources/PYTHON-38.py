def eval_python_38_shallow_water_fvm() -> tuple[bool, float, dict[str, Any]]:
    """1D Saint-Venant shallow water equations total fluid mass conservation across discontinuous dam-break shock."""
    N = 100
    L = 10.0
    dx = L / N
    h = np.ones(N)
    h[:50] = 2.0
    h[50:] = 1.0
    hu = np.zeros(N)
    mass_0 = float(np.sum(h) * dx)
    
    dt = 0.005
    for _ in range(50):
        # Simple Lax-Friedrichs numerical flux
        f_h = hu
        f_hu = hu**2 / h + 0.5 * 9.81 * h**2
        
        flux_h = 0.5 * (f_h[:-1] + f_h[1:]) - 0.5 * (dx / dt) * 0.2 * (h[1:] - h[:-1])
        h[1:-1] -= (dt / dx) * (flux_h[1:] - flux_h[:-1])
        
    mass_end = float(np.sum(h) * dx)
    err = abs(mass_end - mass_0) / mass_0
    passed = err < 1e-10
    return passed, err, {"mass_conservation_error": err}