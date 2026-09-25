def eval_python_39_fokker_planck_norm() -> tuple[bool, float, dict[str, Any]]:
    """Fokker-Planck p_t = - (mu(x) p)_x + D p_xx preserving unit probability integral int p(x) dx = 1."""
    N = 100
    L = 10.0
    dx = L / N
    x = np.linspace(-L/2, L/2, N)
    # Initial Gaussian
    p = np.exp(-x**2) / np.sqrt(np.pi)
    norm_0 = float(np.sum(p) * dx)
    
    dt = 0.001
    D = 0.1
    # Ornstein-Uhlenbeck drift mu(x) = -x
    mu = -x
    for _ in range(100):
        flux = mu * p - D * (np.roll(p, -1) - np.roll(p, 1)) / (2 * dx)
        p -= (dt / (2 * dx)) * (np.roll(flux, -1) - np.roll(flux, 1))
        
    norm_end = float(np.sum(p) * dx)
    err = abs(norm_end - norm_0)
    passed = err < 1e-10
    return passed, err, {"prob_norm_error": err}