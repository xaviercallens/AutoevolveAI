def eval_python_36_cahn_hilliard() -> tuple[bool, float, dict[str, Any]]:
    """Cahn-Hilliard spinodal decomposition u_t = lap (u^3 - u - gamma lap u) with free energy monotonicity dF/dt <= 0."""
    N = 32
    L = 10.0
    dx = L / N
    np.random.seed(42)
    u = 0.05 * (np.random.rand(N, N) - 0.5)
    gamma = 0.1
    
    def free_energy(c):
        grad_x = (np.roll(c, -1, axis=1) - np.roll(c, 1, axis=1)) / (2*dx)
        grad_y = (np.roll(c, -1, axis=0) - np.roll(c, 1, axis=0)) / (2*dx)
        f_bulk = 0.25 * (c**2 - 1.0)**2
        return float(np.sum(f_bulk + 0.5 * gamma * (grad_x**2 + grad_y**2)) * dx * dx)
        
    f0 = free_energy(u)
    # Simple dissipative gradient step
    for _ in range(20):
        lap_u = (np.roll(u, 1, 0) + np.roll(u, -1, 0) + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4*u) / (dx**2)
        mu = u**3 - u - gamma * lap_u
        lap_mu = (np.roll(mu, 1, 0) + np.roll(mu, -1, 0) + np.roll(mu, 1, 1) + np.roll(mu, -1, 1) - 4*mu) / (dx**2)
        u = u + 0.001 * lap_mu
        
    f_end = free_energy(u)
    delta_f = f_end - f0
    passed = delta_f <= 1e-12
    return passed, max(0.0, delta_f), {"delta_free_energy": delta_f, "monotone_decay": delta_f <= 0}