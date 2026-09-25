def eval_python_10_dual_quaternion_screw() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-10: Dual Quaternion Spatial Screw Kinematics."""
    def quat_mult(p: np.ndarray, q: np.ndarray) -> np.ndarray:
        w1, x1, y1, z1 = p
        w2, x2, y2, z2 = q
        return np.array([
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ])

    theta = np.pi / 2.0
    q_r = np.array([np.cos(theta / 2.0), 0.0, 0.0, np.sin(theta / 2.0)])
    t_quat = np.array([0.0, 0.0, 0.0, 2.0])
    q_d = 0.5 * quat_mult(t_quat, q_r)
    norm_r = np.dot(q_r, q_r)
    ortho_err = abs(np.dot(q_r, q_d))
    norm_err = abs(norm_r - 1.0)
    total_err = ortho_err + norm_err
    passed = total_err < 1e-12
    return passed, float(total_err), {"plucker_orthogonality_err": float(ortho_err), "unit_norm_err": float(norm_err)}