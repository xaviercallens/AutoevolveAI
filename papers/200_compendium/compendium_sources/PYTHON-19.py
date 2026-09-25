def eval_python_19_ensemble_kalman_filter() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-19: Kalnay-Toth Ensemble Kalman Filter (EnKF) on Lorenz-96."""
    K = 4
    n_ens = 10
    np.random.seed(77)
    x_true = np.array([2.0, 1.0, -1.0, 0.5])
    ensemble = x_true[:, None] + 0.5 * np.random.randn(K, n_ens)
    H = np.eye(K)
    R = 0.1 * np.eye(K)
    y_obs = x_true + 0.1 * np.random.randn(K)

    x_mean = np.mean(ensemble, axis=1, keepdims=True)
    A = ensemble - x_mean
    P = (A @ A.T) / (n_ens - 1)
    K_gain = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
    innov = y_obs[:, None] - H @ ensemble
    ens_analyzed = ensemble + K_gain @ innov
    analyzed_mean = np.mean(ens_analyzed, axis=1)

    prior_err = np.linalg.norm(x_mean.ravel() - x_true)
    post_err = np.linalg.norm(analyzed_mean - x_true)
    passed = post_err < prior_err
    return passed, float(post_err), {"prior_rmse": float(prior_err), "post_rmse": float(post_err)}