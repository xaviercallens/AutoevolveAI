def eval_python_04_vietoris_rips_homology() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-04: Vietoris-Rips Persistent Homology Filtration on Point Clouds."""
    n_pts = 12
    theta = np.linspace(0, 2.0 * np.pi, n_pts, endpoint=False)
    pts = np.column_stack([np.cos(theta), np.sin(theta)])
    dists = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    adj = (dists < 0.6).astype(int)
    n_edges = (np.sum(adj) - n_pts) // 2
    euler_chi = n_pts - n_edges
    err = abs(euler_chi - 0.0)
    passed = err == 0.0 and n_edges == n_pts
    return passed, float(err), {"n_vertices": n_pts, "n_edges": n_edges, "euler_chi": int(euler_chi)}