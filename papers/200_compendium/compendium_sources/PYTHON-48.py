def eval_python_48_maxwell_fdtd_yee() -> tuple[bool, float, dict[str, Any]]:
    """Staggered Yee grid 1D FDTD Maxwell solver dE/dt = 1/eps dB/dx, dB/dt = 1/mu dE/dx preserving EM energy."""
    N = 64
    dx = 0.1
    c = 1.0
    dt = dx / (2.0 * c) # Courant number S = c dt / dx = 0.5 < 1
    
    Ex = np.sin(2.0 * np.pi * np.arange(N) * dx / (N * dx))
    By = np.zeros(N)
    
    e0 = float(np.sum(Ex**2 + By**2) * dx)
    for _ in range(50):
        # Update B on half steps
        By[:-1] += (dt / dx) * (Ex[1:] - Ex[:-1])
        By[-1] += (dt / dx) * (Ex[0] - Ex[-1])
        # Update E
        Ex[1:] += (dt / dx) * (By[1:] - By[:-1])
        Ex[0] += (dt / dx) * (By[0] - By[-1])
        
    e_end = float(np.sum(Ex**2 + By**2) * dx)
    drift = abs(e_end - e0) / e0
    passed = drift < 0.05
    return passed, float(drift), {"electromagnetic_energy_drift": float(drift)}