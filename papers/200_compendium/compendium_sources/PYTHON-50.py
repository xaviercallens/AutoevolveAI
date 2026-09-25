def eval_python_50_lorenz96_invariant() -> tuple[bool, float, dict[str, Any]]:
    """Lorenz-96 atmospheric toy model dX_i/dt = (X_{i+1} - X_{i-2}) X_{i-1} asserting exact advective energy conservation."""
    # When forcing F=0 and damping -X_i=0, d/dt sum X_i^2 = 0 identically by cyclic cancellation
    K = 16
    np.random.seed(42)
    X = np.random.randn(K)
    e0 = float(np.sum(X**2))
    
    dt = 0.0005
    for _ in range(100):
        # RK4 step on pure advection
        def advection(x):
            return (np.roll(x, -1) - np.roll(x, 2)) * np.roll(x, 1)
        k1 = advection(X)
        k2 = advection(X + 0.5 * dt * k1)
        k3 = advection(X + 0.5 * dt * k2)
        k4 = advection(X + dt * k3)
        X += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
    e_end = float(np.sum(X**2))
    err = abs(e_end - e0) / e0
    passed = err < 1e-6
    return passed, float(err), {"advective_energy_drift": float(err)}