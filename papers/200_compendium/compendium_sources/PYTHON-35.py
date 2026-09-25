def eval_python_35_kuramoto_sivashinsky() -> tuple[bool, float, dict[str, Any]]:
    """Kuramoto-Sivashinsky PDE u_t + u u_x + u_xx + u_xxxx = 0 with exact spatial zero-mode conservation."""
    N = 64
    L = 32.0 * np.pi
    dx = L / N
    x = np.linspace(0, L, N, endpoint=False)
    u = np.cos(x / 16.0) * (1.0 + np.sin(x / 16.0))
    mean_0 = float(np.mean(u))
    
    kx = np.fft.fftfreq(N, d=dx) * 2.0 * np.pi
    # In ETDRK or simple spectral, zero frequency mode k=0 has rhs = 0 because d/dx (u^2/2 + u_x + u_xxx) averages to 0
    dt = 0.01
    for _ in range(50):
        u_hat = np.fft.fft(u)
        nl_hat = np.fft.fft(0.5 * u**2)
        rhs_hat = -1j * kx * nl_hat + (kx**2 - kx**4) * u_hat
        u_hat = u_hat + dt * rhs_hat
        u = np.real(np.fft.ifft(u_hat))
        
    mean_end = float(np.mean(u))
    err = abs(mean_end - mean_0)
    passed = err < 1e-10
    return passed, err, {"spatial_mean_drift": err}