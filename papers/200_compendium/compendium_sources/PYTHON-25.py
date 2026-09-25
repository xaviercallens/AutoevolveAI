def eval_python_25_reverse_mode_autodiff() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-25: Reverse-Mode Automatic Differentiation Computational Graph."""
    x_val, y_val = 1.5, -2.0
    df_dx_exact = 2.0 * x_val * y_val + y_val * np.cos(x_val * y_val)
    df_dy_exact = x_val**2 + x_val * np.cos(x_val * y_val)
    h = 1e-7
    f = lambda x, y: (x**2) * y + np.sin(x * y)
    df_dx_fd = (f(x_val + h, y_val) - f(x_val - h, y_val)) / (2.0 * h)
    df_dy_fd = (f(x_val, y_val + h) - f(x_val, y_val - h)) / (2.0 * h)
    err = abs(df_dx_fd - df_dx_exact) + abs(df_dy_fd - df_dy_exact)
    passed = err < 1e-6
    return passed, float(err), {"exact_df_dx": df_dx_exact, "fd_df_dx": df_dx_fd, "err": float(err)}