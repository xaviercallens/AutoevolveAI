def eval_python_16_quasi_monte_carlo_sobol() -> tuple[bool, float, dict[str, Any]]:
    """PYTHON-16: High-Dimensional Quasi-Monte Carlo Integration with Low-Discrepancy Sequence."""
    # Halton / Van der Corput low discrepancy sequence in 4D
    def van_der_corput(n: int, base: int) -> np.ndarray:
        seq = np.zeros(n)
        for i in range(n):
            f = 1.0 / base
            val = 0.0
            idx = i + 1
            while idx > 0:
                val += f * (idx % base)
                idx //= base
                f /= base
            seq[i] = val
        return seq

    N = 1000
    bases = [2, 3, 5, 7]
    sample = np.column_stack([van_der_corput(N, b) for b in bases])
    integrand = np.prod(2.0 * sample, axis=1)
    qmc_estimate = float(np.mean(integrand))
    err = abs(qmc_estimate - 1.0)
    passed = err < 0.05
    return passed, float(err), {"qmc_estimate": qmc_estimate, "sample_size": N, "error": float(err)}