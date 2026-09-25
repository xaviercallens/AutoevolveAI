def eval_python_45_lotka_volterra_symplectic() -> tuple[bool, float, dict[str, Any]]:
    """Symplectic preservation of Lotka-Volterra first integral V(x,y) = delta x - gamma ln x + beta y - alpha ln y."""
    alpha, beta, gamma, delta = 1.0, 0.5, 0.5, 1.0
    x, y = 1.0, 1.0
    v0 = delta * x - gamma * np.log(x) + beta * y - alpha * np.log(y)
    
    # Symplectic Euler integration
    dt = 0.001
    for _ in range(500):
        # dx/dt = x (alpha - beta y) => d(ln x)/dt = alpha - beta y
        # dy/dt = -y (gamma - delta x) => d(ln y)/dt = -gamma + delta x
        u = np.log(x)
        v = np.log(y)
        u += dt * (alpha - beta * np.exp(v))
        v += dt * (-gamma + delta * np.exp(u))
        x = np.exp(u)
        y = np.exp(v)
        
    v_end = delta * x - gamma * np.log(x) + beta * y - alpha * np.log(y)
    drift = abs(v_end - v0) / v0
    passed = drift < 1e-3
    return passed, float(drift), {"hamiltonian_drift": float(drift)}