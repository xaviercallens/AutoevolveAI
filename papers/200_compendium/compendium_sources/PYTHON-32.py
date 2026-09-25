def eval_python_32_nlse_soliton() -> tuple[bool, float, dict[str, Any]]:
    """Split-step Fourier method for cubic NLSE i psi_t + 1/2 psi_xx + |psi|^2 psi = 0 preserving L^2 norm."""
    N = 128
    L = 20.0
    dx = L / N
    x = np.linspace(-L/2, L/2, N, endpoint=False)
    # Fundamental bright soliton: psi(x,0) = sech(x)
    psi = 1.0 / np.cosh(x) + 0.0j
    n0 = float(np.sum(np.abs(psi)**2) * dx)
    
    dt = 0.01
    kx = np.fft.fftfreq(N, d=dx) * 2.0 * np.pi
    dispersion_op = np.exp(-0.5j * (kx**2) * dt)
    
    for _ in range(50):
        # Half step linear
        psi = np.fft.ifft(dispersion_op * np.fft.fft(psi))
        # Nonlinear step
        psi = psi * np.exp(1.0j * np.abs(psi)**2 * dt)
        # Half step linear
        psi = np.fft.ifft(dispersion_op * np.fft.fft(psi))
        
    n_end = float(np.sum(np.abs(psi)**2) * dx)
    norm_drift = abs(n_end - n0) / n0
    passed = norm_drift < 1e-10
    return passed, norm_drift, {"norm_drift": norm_drift, "initial_norm": n0, "final_norm": n_end}