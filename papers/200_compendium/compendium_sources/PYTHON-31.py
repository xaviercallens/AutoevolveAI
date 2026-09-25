def eval_python_31_chorin_projection() -> tuple[bool, float, dict[str, Any]]:
    """Chorin fractional step projection method: u* = u - dt*(u.grad u - nu lap u), p solved via Poisson lap p = div u* / dt, u^{n+1} = u* - dt grad p. Div u^{n+1} == 0."""
    N = 32
    L = 2.0 * np.pi
    dx = L / N
    dt = 0.005
    x = np.linspace(0, L, N, endpoint=False)
    X, Y = np.meshgrid(x, x)
    
    # Taylor-Green vortex intermediate state with non-zero divergence
    u_star = np.sin(X) * np.cos(Y) + 0.1 * np.cos(X)
    v_star = -np.cos(X) * np.sin(Y) + 0.1 * np.sin(Y)
    
    # Spectral Poisson solve: lap p = div u* / dt
    kx = np.fft.fftfreq(N, d=dx) * 2.0 * np.pi
    Kx, Ky = np.meshgrid(kx, kx)
    K_sq = Kx**2 + Ky**2
    K_sq[0, 0] = 1.0
    
    div_hat = 1j * Kx * np.fft.fft2(u_star) + 1j * Ky * np.fft.fft2(v_star)
    p_hat = - (div_hat / dt) / K_sq
    p_hat[0, 0] = 0.0
    
    grad_p_x = np.real(np.fft.ifft2(1j * Kx * p_hat))
    grad_p_y = np.real(np.fft.ifft2(1j * Ky * p_hat))
    
    # Projection step
    u_next = u_star - dt * grad_p_x
    v_next = v_star - dt * grad_p_y
    
    # Invariant: divergence of projected velocity is identically zero
    div_next = np.real(np.fft.ifft2(1j * Kx * np.fft.fft2(u_next) + 1j * Ky * np.fft.fft2(v_next)))
    max_div = float(np.max(np.abs(div_next)))
    passed = max_div < 1e-10
    return passed, max_div, {"max_divergence": max_div}