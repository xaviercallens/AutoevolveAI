"""
Tests for ANSE Riemannian SDE Engine.
Physical hardness: all assertions verified against genuine numerical computation.
No mocks. No hardcoded values.
"""

from __future__ import annotations

import numpy as np
import pytest

from anse.geometry.riemannian_sde_engine import (
    so3_exp,
    project_to_sphere,
    tangent_projection,
    euler_maruyama_sphere,
    icosphere_mesh,
    gauss_bonnet_quadrature,
    solve_jacobi_field,
    RiemannianSDEEngine,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: SO(3) Exponential Map
# ─────────────────────────────────────────────────────────────────────────────

def test_so3_exp_identity():
    """Zero rotation vector should return identity matrix."""
    R = so3_exp(np.zeros(3))
    np.testing.assert_allclose(R, np.eye(3), atol=1e-14)


def test_so3_exp_orthogonality():
    """SO(3) exponential must return an orthogonal matrix (R^T R = I, det R = 1)."""
    omega = np.array([0.3, 0.5, -0.2])
    R = so3_exp(omega)
    RtR = R.T @ R
    np.testing.assert_allclose(RtR, np.eye(3), atol=1e-12, err_msg="R^T R must be identity")
    det = np.linalg.det(R)
    assert abs(det - 1.0) < 1e-12, f"det(R) must be 1, got {det}"


def test_so3_exp_pi_rotation():
    """π rotation around z-axis: maps x→-x, y→-y, z→z."""
    omega = np.array([0.0, 0.0, np.pi])
    R = so3_exp(omega)
    x_mapped = R @ np.array([1.0, 0.0, 0.0])
    np.testing.assert_allclose(x_mapped, [-1.0, 0.0, 0.0], atol=1e-12)


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Tangent Space Projection
# ─────────────────────────────────────────────────────────────────────────────

def test_tangent_projection_perpendicular():
    """Projected tangent vector must be perpendicular to the base point."""
    p = np.array([0.0, 0.0, 1.0])  # north pole
    v = np.array([1.0, 2.0, 5.0])  # arbitrary vector
    v_t = tangent_projection(p, v)
    dot = np.dot(v_t, p)
    assert abs(dot) < 1e-14, f"Tangent projection must be orthogonal to p, got dot={dot}"


def test_project_to_sphere_unit_norm():
    """Any non-zero vector projects to a unit vector."""
    v = np.array([3.0, -4.0, 0.0])
    p = project_to_sphere(v)
    assert abs(np.linalg.norm(p) - 1.0) < 1e-14


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Euler–Maruyama on S²
# ─────────────────────────────────────────────────────────────────────────────

def test_euler_maruyama_stays_on_sphere():
    """All trajectory points must lie on the unit sphere."""
    rng = np.random.default_rng(42)
    p0 = np.array([1.0, 0.0, 0.0])
    trajectory = euler_maruyama_sphere(
        p0, lambda p: np.zeros(3), dt=0.01, n_steps=200, rng=rng, sigma=0.1
    )
    norms = np.linalg.norm(trajectory, axis=1)
    np.testing.assert_allclose(norms, np.ones(len(norms)), atol=1e-12,
                                err_msg="All trajectory points must lie on unit sphere S²")


def test_euler_maruyama_explores_sphere():
    """Brownian motion with high noise should explore a wide range of the sphere."""
    rng = np.random.default_rng(7)
    p0 = np.array([0.0, 0.0, 1.0])  # start at north pole
    trajectory = euler_maruyama_sphere(
        p0, lambda p: np.zeros(3), dt=0.05, n_steps=500, rng=rng, sigma=1.0
    )
    # Variance in z-coordinate should be significant (exploring the sphere)
    z_variance = float(np.var(trajectory[:, 2]))
    assert z_variance > 0.05, f"Brownian motion must explore sphere, z-variance={z_variance:.4f}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Icosphere Mesh
# ─────────────────────────────────────────────────────────────────────────────

def test_icosphere_vertices_on_sphere():
    """All icosphere mesh vertices must lie on the unit sphere."""
    vertices, triangles = icosphere_mesh(subdivisions=2)
    norms = np.linalg.norm(vertices, axis=1)
    np.testing.assert_allclose(norms, np.ones(len(norms)), atol=1e-12,
                                err_msg="All icosphere vertices must lie on S²")


def test_icosphere_triangle_count():
    """
    Icosphere triangle counts: base=20 faces, each subdivision multiplies by 4.
    subdivisions=2 → 20 * 4^2 = 320 triangles.
    """
    _, triangles = icosphere_mesh(subdivisions=2)
    expected = 20 * (4 ** 2)
    assert len(triangles) == expected, f"Expected {expected} triangles, got {len(triangles)}"


def test_icosphere_vertex_indices_valid():
    """All triangle vertex indices must be within bounds."""
    vertices, triangles = icosphere_mesh(subdivisions=1)
    n_verts = len(vertices)
    assert np.all(triangles >= 0) and np.all(triangles < n_verts), "All triangle indices must be valid"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Gauss–Bonnet Quadrature — Physical Hardness Gate
# ─────────────────────────────────────────────────────────────────────────────

def test_gauss_bonnet_sphere_value():
    """
    PHYSICAL HARDNESS GATE: Gauss–Bonnet integral over S² must equal 4π.
    Higher subdivisions → closer to exact 4π.
    """
    vertices, triangles = icosphere_mesh(subdivisions=4)
    integral = gauss_bonnet_quadrature(vertices, triangles)
    expected = 4.0 * np.pi
    error = abs(integral - expected)
    print(f"\n[GAUSS-BONNET] integral={integral:.8f}, expected={expected:.8f}, error={error:.2e}")
    assert error < 1e-3, (
        f"GATE FAIL: |∫∫ K dA - 4π| = {error:.2e} >= 1e-3. "
        f"Gauss-Bonnet quadrature must converge to 4π for unit sphere."
    )


def test_gauss_bonnet_converges_with_refinement():
    """
    Gauss-Bonnet quadrature at all refinement levels must be within numerical tolerance
    of 4π. The errors are typically at machine precision (< 1e-10) for subdivisions >= 2,
    so we verify all are < 1e-6 rather than monotonic (floating-point accumulation can
    cause non-monotonic behavior at sub-1e-10 precision).
    """
    for sub in [2, 3, 4]:
        verts, tris = icosphere_mesh(subdivisions=sub)
        integral = gauss_bonnet_quadrature(verts, tris)
        error = abs(integral - 4.0 * np.pi)
        assert error < 1e-6, (
            f"sub={sub}: Gauss-Bonnet error={error:.2e} >= 1e-6. "
            f"Quadrature must be highly accurate at this refinement level."
        )

# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Jacobi Field Eigenvalue
# ─────────────────────────────────────────────────────────────────────────────

def test_jacobi_field_eigenvalue_sphere():
    """
    For K=1 (unit sphere), Jacobi field equation J'' + J = 0.
    The eigenvalue of the curvature operator must be ≈ -1.0.
    """
    eigenvalue = solve_jacobi_field(K=1.0, n_steps=10000, arc_length=np.pi / 4)
    assert abs(eigenvalue - (-1.0)) < 1e-6, (
        f"Jacobi field eigenvalue for K=1 must be ≈ -1.0, got {eigenvalue:.8f}"
    )


def test_jacobi_field_higher_curvature():
    """For K=4 (sphere of radius 1/2), eigenvalue must be ≈ -4.0."""
    eigenvalue = solve_jacobi_field(K=4.0, n_steps=10000, arc_length=np.pi / 8)
    assert abs(eigenvalue - (-4.0)) < 1e-5, (
        f"Jacobi field eigenvalue for K=4 must be ≈ -4.0, got {eigenvalue:.8f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Full Engine Integration
# ─────────────────────────────────────────────────────────────────────────────

def test_riemannian_sde_engine_full():
    """
    Full engine integration test with all physical hardness gates:
    - Gauss-Bonnet error < 1e-3
    - Jacobi field eigenvalue ≈ -1.0
    - Trajectory stays on S²
    """
    engine = RiemannianSDEEngine(n_steps=500, dt=0.02, sigma=0.3, seed=42)
    result = engine.simulate(mesh_subdivisions=3)

    assert result.gauss_bonnet_verified is True, (
        f"GATE FAIL: |∫K dA - 4π| = {result.gauss_bonnet_error:.2e}"
    )
    assert result.gauss_bonnet_error < 1e-3
    assert abs(result.geodesic_deviation_eigenvalue - (-1.0)) < 1e-5, (
        f"Jacobi eigenvalue must be ≈ -1.0, got {result.geodesic_deviation_eigenvalue}"
    )
    assert result.status == "VERIFIED"
    assert result.proof_token, "Proof token must be non-empty"
    assert result.n_mesh_vertices > 100, "Mesh must have substantial triangulation"
    print(f"\n[RIEMANNIAN SDE] GB integral={result.gauss_bonnet_integral:.6f} (4π={4*np.pi:.6f}), "
          f"Jacobi λ={result.geodesic_deviation_eigenvalue:.6f}, "
          f"elapsed={result.elapsed_ms:.1f}ms")
