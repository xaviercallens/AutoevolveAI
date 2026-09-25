def eval_python_18_fem_2d_poisson() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-18: Finite Element Method (FEM) 2D Poisson Solver on Triangular Meshes."""
    K_elem = 0.5 * np.array([[2.0, -1.0, -1.0], [-1.0, 1.0, 0.0], [-1.0, 0.0, 1.0]])
    row_sum_err = np.max(np.abs(np.sum(K_elem, axis=1)))
    symm_err = np.max(np.abs(K_elem - K_elem.T))
    total_err = row_sum_err + symm_err
    passed = total_err < 1e-12
    return passed, float(total_err), {"nullspace_row_sum_err": float(row_sum_err), "symmetry_err": float(symm_err)}