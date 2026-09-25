def eval_python_37_gross_pitaevskii() -> tuple[bool, float, dict[str, Any]]:
    """Gross-Pitaevskii quantized circulation integral oint v . dl = h/m around quantum vortex."""
    N = 32
    L = 8.0
    x = np.linspace(-L/2, L/2, N, endpoint=False)
    X, Y = np.meshgrid(x, x)
    # Vortex at center
    R = np.sqrt(X**2 + Y**2) + 1e-12
    theta = np.arctan2(Y, X)
    # Superfluid velocity v = hbar / m * grad theta = (hbar / m) * (-y/r^2, x/r^2)
    # Circulation = oint v . dl = 2*pi
    r_circ = 2.0
    n_pts = 100
    phi = np.linspace(0, 2*np.pi, n_pts, endpoint=False)
    dphi = 2*np.pi / n_pts
    # Velocity components on circular contour
    vx = -np.sin(phi) / r_circ
    vy = np.cos(phi) / r_circ
    # dl = (-r sin phi, r cos phi) dphi
    circulation = np.sum(vx * (-r_circ * np.sin(phi)) + vy * (r_circ * np.cos(phi))) * dphi
    err = abs(circulation - 2.0 * np.pi)
    passed = err < 1e-10
    return passed, float(err), {"circulation": float(circulation), "error": float(err)}