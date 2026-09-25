def eval_python_33_kdv_solitons() -> tuple[bool, float, dict[str, Any]]:
    """Zabusky-Kruskal pseudo-spectral solver for KdV u_t + u u_x + delta^2 u_xxx = 0 preserving mass and momentum."""
    N = 64
    L = 2.0 * np.pi
    dx = L / N
    x = np.linspace(0, L, N, endpoint=False)
    u = np.cos(x)
    mass_0 = float(np.mean(u))
    mom_0 = float(np.mean(u**2))
    
    kx = np.fft.fftfreq(N, d=dx) * 2.0 * np.pi
    dt = 0.001
    delta = 0.022
    
    for _ in range(100):
        u_hat = np.fft.fft(u)
        du_dx = np.real(np.fft.ifft(1j * kx * u_hat))
        d3u_dx3 = np.real(np.fft.ifft(-1j * (kx**3) * u_hat))
        # RK2 step
        rhs = -(u * du_dx + (delta**2) * d3u_dx3)
        u_mid = u + 0.5 * dt * rhs
        u_mid_hat = np.fft.fft(u_mid)
        du_dx_mid = np.real(np.fft.ifft(1j * kx * u_mid_hat))
        d3u_dx3_mid = np.real(np.fft.ifft(-1j * (kx**3) * u_mid_hat))
        rhs_mid = -(u_mid * du_dx_mid + (delta**2) * d3u_dx3_mid)
        u = u + dt * rhs_mid
        
    mass_end = float(np.mean(u))
    mom_end = float(np.mean(u**2))
    mass_err = abs(mass_end - mass_0)
    mom_err = abs(mom_end - mom_0)
    total_err = mass_err + mom_err * 0.1
    passed = total_err < 1e-4
    return passed, total_err, {"mass_error": mass_err, "momentum_error": mom_err}