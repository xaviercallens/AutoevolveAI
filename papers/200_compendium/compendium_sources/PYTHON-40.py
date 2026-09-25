def eval_python_40_gray_scott() -> tuple[bool, float, dict[str, Any]]:
    """Two-component Gray-Scott reaction-diffusion system checking chemical bounding u, v in [0, 1]."""
    N = 32
    u = np.ones((N, N))
    v = np.zeros((N, N))
    u[14:18, 14:18] = 0.5
    v[14:18, 14:18] = 0.25
    
    Du = 0.16
    Dv = 0.08
    F = 0.035
    k = 0.065
    dt = 1.0
    
    for _ in range(20):
        lap_u = (np.roll(u, 1, 0) + np.roll(u, -1, 0) + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4*u)
        lap_v = (np.roll(v, 1, 0) + np.roll(v, -1, 0) + np.roll(v, 1, 1) + np.roll(v, -1, 1) - 4*v)
        uvv = u * v * v
        u += (Du * lap_u - uvv + F * (1.0 - u)) * dt
        v += (Dv * lap_v + uvv - (F + k) * v) * dt
        
    bounded = bool(np.all(u >= 0.0) and np.all(u <= 1.0) and np.all(v >= 0.0) and np.all(v <= 1.0))
    min_val = float(min(np.min(u), np.min(v)))
    max_val = float(max(np.max(u), np.max(v)))
    err = max(0.0, -min_val) + max(0.0, max_val - 1.0)
    passed = bounded and err == 0.0
    return passed, err, {"physically_bounded": bounded}