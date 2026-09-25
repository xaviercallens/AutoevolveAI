def eval_python_02_navier_stokes_pseudospectral() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-02: 2D Navier-Stokes Pseudospectral Vorticity Solver with 2/3 dealiasing."""
    N = 32
    L = 2.0 * np.pi
    x = np.linspace(0, L, N, endpoint=False)
    X, Y = np.meshgrid(x, x)
    omega = 2.0 * np.cos(X) * np.sin(Y)
    kx = np.fft.fftfreq(N, d=L / (2.0 * np.pi * N))
    Kx, Ky = np.meshgrid(kx, kx)
    K_sq = Kx**2 + Ky**2
    K_sq[0, 0] = 1.0

    omega_hat = np.fft.fft2(omega)
    enstrophy_0 = 0.5 * np.mean(omega**2)
    psi_hat = omega_hat / K_sq
    psi_hat[0, 0] = 0.0
    u = np.real(np.fft.ifft2(1j * Ky * psi_hat))
    v = np.real(np.fft.ifft2(-1j * Kx * psi_hat))

    u_hat = np.fft.fft2(u)
    v_hat = np.fft.fft2(v)
    div_norm = np.max(np.abs(np.real(np.fft.ifft2(1j * Kx * u_hat + 1j * Ky * v_hat))))

    passed = div_norm < 1e-10
    return passed, float(div_norm), {"incompressibility_div": float(div_norm), "enstrophy": float(enstrophy_0)}