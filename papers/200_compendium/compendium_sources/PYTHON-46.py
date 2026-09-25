def eval_python_46_sine_gordon_soliton() -> tuple[bool, float, dict[str, Any]]:
    """Integrable Sine-Gordon field phi_tt - phi_xx + sin phi = 0 with topological charge Q = 1/2pi [phi(inf) - phi(-inf)]."""
    # Kink: phi(x) = 4 arctan(exp(x)) -> phi(-inf) = 0, phi(+inf) = 2pi => Q = 1
    # Antikink: phi(x) = 4 arctan(exp(-x)) -> Q = -1
    # Combined kink-antikink state has total Q = 0
    x = np.linspace(-20, 20, 200)
    phi_kink = 4.0 * np.arctan(np.exp(x + 5.0))
    phi_antikink = 4.0 * np.arctan(np.exp(-(x - 5.0)))
    phi_total = phi_kink + phi_antikink - 2.0 * np.pi
    
    Q = float((phi_total[-1] - phi_total[0]) / (2.0 * np.pi))
    err = abs(Q - 0.0)
    passed = err < 1e-4
    return passed, err, {"net_topological_charge": Q}