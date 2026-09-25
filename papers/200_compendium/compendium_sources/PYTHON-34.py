def eval_python_34_ginzburg_landau_defect() -> tuple[bool, float, dict[str, Any]]:
    """Complex Ginzburg-Landau equation spiral defect with topological winding number around vortex core."""
    N = 32
    L = 10.0
    x = np.linspace(-L/2, L/2, N, endpoint=False)
    X, Y = np.meshgrid(x, x)
    theta = np.arctan2(Y, X)
    r = np.sqrt(X**2 + Y**2)
    # Vortex profile A(r) exp(i theta)
    A = np.tanh(r)
    psi = A * np.exp(1j * theta)
    
    # Compute topological charge via contour loop around origin
    # Circle of radius 3
    n_loop = 64
    phi_loop = np.linspace(0, 2*np.pi, n_loop, endpoint=False)
    x_c = 3.0 * np.cos(phi_loop)
    y_c = 3.0 * np.sin(phi_loop)
    phase = np.arctan2(y_c, x_c)
    dphase = np.diff(np.unwrap(phase))
    total_winding = float(np.sum(dphase) + (phase[0] - phase[-1])) / (2 * np.pi)
    
    err = abs(round(total_winding) - 1.0)
    passed = err == 0
    return passed, float(err), {"topological_charge": total_winding}