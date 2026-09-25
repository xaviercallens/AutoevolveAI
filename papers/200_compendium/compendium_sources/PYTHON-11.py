def eval_python_11_fast_multipole_potential() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-11: 2D Fast Multipole Method Potential Evaluation."""
    n_src = 8
    theta = np.linspace(0, 2 * np.pi, n_src, endpoint=False)
    src_pos = 0.5 * np.column_stack([np.cos(theta), np.sin(theta)])
    charges = np.ones(n_src) / n_src
    target = np.array([10.0, 10.0])
    r_direct = np.linalg.norm(target - src_pos, axis=1)
    pot_direct = np.sum(charges * np.log(r_direct))
    center = np.mean(src_pos, axis=0)
    pot_fmm = np.sum(charges) * np.log(np.linalg.norm(target - center))
    rel_err = abs(pot_fmm - pot_direct) / abs(pot_direct)
    passed = rel_err < 1e-3
    return passed, float(rel_err), {"pot_direct": float(pot_direct), "pot_fmm": float(pot_fmm), "rel_err": float(rel_err)}