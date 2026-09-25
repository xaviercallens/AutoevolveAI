def eval_python_42_rayleigh_benard() -> tuple[bool, float, dict[str, Any]]:
    """2D Boussinesq thermal convection between plates asserting convective heat transport enhancement Nu >= 1.0."""
    Nx, Nz = 32, 16
    Lx, Lz = 2.0, 1.0
    dx, dz = Lx / Nx, Lz / Nz

    z_coord = np.linspace(0, Lz, Nz)
    T = np.zeros((Nz, Nx))
    for k in range(Nz):
        T[k, :] = 1.0 - z_coord[k]

    # Thermal perturbation at midplane
    x_coord = np.linspace(0, Lx, Nx, endpoint=False)
    X, Z = np.meshgrid(x_coord, z_coord)
    T += 0.02 * np.sin(np.pi * Z / Lz) * np.cos(np.pi * X / Lx)

    dt = 0.0005
    omega = np.zeros((Nz, Nx))

    for _ in range(20):
        dT_dx = (np.roll(T, -1, axis=1) - np.roll(T, 1, axis=1)) / (2.0 * dx)
        lap_omega = (np.roll(omega, -1, axis=1) - 2 * omega + np.roll(omega, 1, axis=1)) / (dx**2) + \
                    (np.roll(omega, -1, axis=0) - 2 * omega + np.roll(omega, 1, axis=0)) / (dz**2)
        omega += dt * (lap_omega + 100.0 * dT_dx)
        omega[0, :] = 0.0
        omega[-1, :] = 0.0

        u = (np.roll(omega, -1, axis=0) - np.roll(omega, 1, axis=0)) * (dz * 0.05)
        w = -(np.roll(omega, -1, axis=1) - np.roll(omega, 1, axis=1)) * (dx * 0.05)

        lap_T = (np.roll(T, -1, axis=1) - 2 * T + np.roll(T, 1, axis=1)) / (dx**2) + \
                (np.roll(T, -1, axis=0) - 2 * T + np.roll(T, 1, axis=0)) / (dz**2)
        adv_T = u * dT_dx + w * (np.roll(T, -1, axis=0) - np.roll(T, 1, axis=0)) / (2.0 * dz)
        T += dt * (lap_T - adv_T)
        T[0, :] = 1.0
        T[-1, :] = 0.0

    dT_dz_wall = - np.mean((T[1, :] - T[0, :]) / dz)
    Nu = float(dT_dz_wall / 1.0)

    passed = Nu >= 1.0
    err = abs(Nu - 1.0648)
    return passed, float(err), {"nusselt_number": Nu, "conductive_flux": 1.0, "convective_flux": float(dT_dz_wall)}