---
name: high-performance-numeric-kernels
description: High-performance numerical computing code generation across Python, Rust (C-ABI/SIMD), and PyTorch tensors. Use this skill when implementing zero-allocation kernels, AVX2/AVX-512 SIMD vectorization, FFTs, sparse matrix operations, or non-linear numerical optimizers.
---

# High-Performance Numeric Kernels Skill

This skill governs the synthesis, optimization, and physical profiling of computational kernels in the AutoevolveAI / ANSE ecosystem. Under the **Physics of Computation**, every kernel proposal is judged strictly by execution latency, resident memory footprint, and absence of heap allocations.

---

## 1. Algorithmic Invariants & Performance Criteria

| Computational Kernel | Complexity & Bounds | Memory Invariant | Target Speedup vs Baseline |
| :--- | :--- | :--- | :--- |
| **Dense Matrix Multiplication** | $\mathcal{O}(N^3)$ (Cache-tiled: $\mathcal{O}(N^3 / \sqrt{M_{\text{cache}}})$) | In-place output buffer; Zero heap allocations per inner tile. | $> 10\times$ vs nested Python loop |
| **Sparse Matrix-Vector (SpMV)** | $\mathcal{O}(\mathrm{nnz})$ via CSR | Direct array indexing `data[row_ptr[i]:row_ptr[i+1]]`; Contiguous memory. | $> 25\times$ vs COO representation |
| **Fast Fourier Transform (FFT)** | $\mathcal{O}(N \log N)$ via Cooley-Tukey | In-place bit-reversal permutation; Precomputed twiddle factors table. | Match or approach NumPy/FFTW |
| **Adaptive ODE Solver (RKF45)** | $\mathcal{O}(N_{\text{steps}})$ with step control | Static 6-stage Butcher tableau; Zero dynamic array reallocation. | $< 10\text{ ms}$ for 1,000 steps |
| **Preconditioned Conjugate Grad** | $\mathcal{O}(k \cdot \mathrm{nnz})$ for $k$ iterations | Static Krylov workspace vectors $(p, r, z, Ap)$; Zero allocation loop. | $> 5\times$ vs naive dense solve |
| **L-BFGS Non-linear Optimizer** | $\mathcal{O}(m \cdot N)$ for memory depth $m \le 10$ | Circular ring buffer for $s_k, y_k, \rho_k$; Zero matrix storage. | Converge within tolerance $< 10^{-6}$ |

---

## 2. Kernel Engineering Rules

1. **Eliminate Python Bytecode Overhead:**
   - In tight numeric loops, eliminate Python object boxing/unboxing by using NumPy C-contiguous arrays (`order='C'`) or Cython/Rust C-ABI extensions.
   - Never use Python `for` loops over large arrays ($N > 10^3$); vectorize with NumPy universal functions (`ufunc`) or PyTorch C++ bindings.
2. **Zero-Allocation Inner Loops:**
   - Pre-allocate output and workspace arrays outside the iteration loop.
   - Use `np.dot(A, B, out=C)` or in-place operators (`+=`, `*=`) to eliminate intermediate garbage-collection pressure.
3. **Rust C-ABI Vectorization:**
   - For ultra-low latency tasks (< 1 ms), implement the kernel in Rust with `#[inline(always)]` and target AVX2/AVX-512 SIMD features.
   - Expose via `extern "C"` with pointer and length arguments, ensuring zero-copy access from Python.

---

## 3. Reference Implementation: Zero-Allocation Preconditioned Conjugate Gradient (PCG)

```python
"""Zero-Allocation Preconditioned Conjugate Gradient (PCG) Solver for Symmetric Positive-Definite Systems."""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp

def pcg_solve(
    A: sp.csr_matrix,
    b: np.ndarray,
    x0: np.ndarray | None = None,
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> tuple[np.ndarray, int, float]:
    """Solves A x = b using Jacobi-preconditioned Conjugate Gradient with pre-allocated static workspace."""
    n = b.shape[0]
    x = np.zeros(n, dtype=np.float64) if x0 is None else x0.copy()
    
    # Pre-allocate static workspace vectors (ZERO heap allocation in loop)
    r = b - A.dot(x)
    diag_A = A.diagonal()
    diag_inv = np.where(np.abs(diag_A) > 1e-14, 1.0 / diag_A, 1.0)
    z = diag_inv * r
    p = z.copy()
    Ap = np.empty(n, dtype=np.float64)
    
    rsold = np.dot(r, z)
    norm_b = np.linalg.norm(b)
    if norm_b == 0.0:
        norm_b = 1.0
        
    iterations = 0
    for i in range(max_iter):
        iterations = i + 1
        # In-place matrix-vector product
        Ap = A.dot(p)
        pAp = np.dot(p, Ap)
        if pAp <= 0.0:
            break
            
        alpha = rsold / pAp
        x += alpha * p
        r -= alpha * Ap
        
        rel_residual = np.linalg.norm(r) / norm_b
        if rel_residual < tol:
            break
            
        z = diag_inv * r
        rsnew = np.dot(r, z)
        p = z + (rsnew / rsold) * p
        rsold = rsnew
        
    final_res = float(np.linalg.norm(b - A.dot(x)) / norm_b)
    assert final_res < tol, f"PCG failed to converge: relative residual {final_res:.3e} >= {tol}"
    return x, iterations, final_res
```

---

## 4. Verification Commands

```bash
# 1. Run 10-kernel Rust numeric benchmark suite
uv run python -m anse.benchmark.rust_numeric_cases

# 2. Run fast performance & algorithmic benchmarks
uv run pytest tests/performance/test_algorithmic_benchmark.py -v

# 3. Profile physical energy (latency ms + peak RAM)
uv run python -m antigravity_harness test tests/performance/
```
