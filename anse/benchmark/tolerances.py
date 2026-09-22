"""
Domain-Specific Invariant Tolerances.
Defines acceptable error bounds for various numerical and stochastic benchmarks.
"""
from typing import Dict

# Define tolerances by domain/case
TOLERANCES: Dict[str, float] = {
    # Deterministic Exact
    "RUST-01": 1e-12, # Matrix Mult
    "RUST-02": 1e-12, # FFT
    "RUST-03": 1e-12, # LUP
    "RUST-14": 1e-12, # Cholesky
    "RUST-18": 1e-12, # QR
    "RUST-16": 1e-12, # Ray Tracing
    "RUST-04": 1e-12, # Graham Scan
    "RUST-06": 1e-12, # KD-Tree
    "RUST-07": 1e-12, # A* Search
    "RUST-11": 1e-12, # Dijkstra
    "RUST-15": 1e-12, # Convex Hull
    "RUST-19": 1e-12, # PageRank
    
    # Adaptive Numerical
    "RUST-08": 1e-6,  # RKF45
    "RUST-09": 1e-6,  # LBM D2Q9
    "RUST-10": 1e-6,  # BFGS
    "RUST-12": 1e-6,  # PCG
    "RUST-13": 1e-6,  # N-Body
    "RUST-17": 1e-6,  # Navier-Stokes MAC
    
    # Stochastic
    "RUST-05": 0.10,  # Black-Scholes MC
    "RUST-20": 0.10,  # Simulated Annealing
}

# Math/Physics usually have very small structural error bounds.
# A default of 1e-12 is used if not strictly present in this dictionary.

def normalize_error(case_id: str, error: float) -> float:
    """Normalize the raw invariant error into a [0, 1] penalty score."""
    if error == 0.0:
        return 0.0
    tol = TOLERANCES.get(case_id, 1e-12)
    
    # We apply the tolerance scaling. If it's well within tolerance, the penalty is small.
    # If it exceeds the tolerance, it ramps up to 1.0.
    normalized = error / tol
    return float(min(1.0, normalized))
