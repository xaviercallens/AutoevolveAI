def eval_python_41_tov_polytrope() -> tuple[bool, float, dict[str, Any]]:
    """Relativistic stellar structure TOV equation integrated via 4th-order Runge-Kutta.

    dm/dr = 4 * pi * r^2 * rho
    dP/dr = - (rho + P) * (m + 4 * pi * r^3 * P) / (r * (r - 2 * m))
    """
    K = 100.0
    Gamma = 2.0
    rho_c = 1.0e-3
    P_c = K * (rho_c ** Gamma)

    # Core boundary conditions at r -> 0
    dr = 0.01
    r = dr
    m = (4.0 / 3.0) * np.pi * (r ** 3) * rho_c
    P = P_c - (2.0 / 3.0) * np.pi * (rho_c + P_c) * (rho_c + 3.0 * P_c) * (r ** 2)

    def tov_rhs(rad: float, mass: float, press: float) -> tuple[float, float]:
        if press <= 0:
            return 0.0, 0.0
        rho = (press / K) ** (1.0 / Gamma)
        dm_dr = 4.0 * np.pi * (rad ** 2) * rho
        denom = rad * (rad - 2.0 * mass)
        if denom <= 0:
            return 0.0, 0.0
        numer = (rho + press) * (mass + 4.0 * np.pi * (rad ** 3) * press)
        dp_dr = - numer / denom
        return dm_dr, dp_dr

    # RK4 outward integration until surface P <= 0
    for _ in range(2000):
        if P <= 0.0:
            break
        k1_m, k1_P = tov_rhs(r, m, P)
        k2_m, k2_P = tov_rhs(r + 0.5 * dr, m + 0.5 * dr * k1_m, P + 0.5 * dr * k1_P)
        k3_m, k3_P = tov_rhs(r + 0.5 * dr, m + 0.5 * dr * k2_m, P + 0.5 * dr * k2_P)
        k4_m, k4_P = tov_rhs(r + dr, m + dr * k3_m, P + dr * k3_P)

        m += (dr / 6.0) * (k1_m + 2.0 * k2_m + 2.0 * k3_m + k4_m)
        P += (dr / 6.0) * (k1_P + 2.0 * k2_P + 2.0 * k3_P + k4_P)
        r += dr

    R_star = float(r)
    M_star = float(m)
    compactness = 2.0 * M_star / R_star
    buchdahl_satisfied = compactness < (8.0 / 9.0)
    z_redshift = float((1.0 - compactness) ** (-0.5) - 1.0)

    passed = buchdahl_satisfied and (M_star > 0.0) and (R_star > 0.0) and (z_redshift > 0.0)
    err = abs(compactness - 0.2695)
    return passed, float(err), {
        "stellar_radius_R": R_star,
        "stellar_mass_M": M_star,
        "compactness_2M_over_R": float(compactness),
        "gravitational_redshift": z_redshift,
        "buchdahl_limit_satisfied": bool(buchdahl_satisfied),
    }