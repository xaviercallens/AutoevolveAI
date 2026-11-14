"""Tests for scripts/openai_math/lt_matrix/second_variation.py (H-LT3 second variation at the embedded scalar extremiser)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "openai_math" / "lt_matrix"))
import second_variation as sv  # noqa: E402
from instrument import Blobs, Grid, equality_potential, numerator_denominator, sharp_constant  # noqa: E402

GAMMA, P = 1.25, 4
GRID = Grid(12.0, 100, 800)


def test_B_of_matches_blobs_for_one_blob() -> None:
    m = 2
    mdl = Blobs(m, K=1, P=P, seed=3)
    n = sv.n_params(m, P)
    theta = torch.cat([mdl.cr.detach().reshape(-1), mdl.ci.detach().reshape(-1), mdl.logk.detach().reshape(-1), mdl.x0.detach().reshape(-1)])
    assert theta.numel() == n
    x = GRID.x
    with torch.no_grad():
        ref = mdl.B(x)
    assert torch.allclose(sv.B_of(theta, x, m, P), ref, atol=1e-13)
    assert float(ref.abs().max()) > 0.1  # the comparison is not between two zero tensors


def test_theta_star_is_the_scalar_equality_potential_and_attains_L1() -> None:
    th = sv.theta_star(GAMMA, 3, P)
    W = sv.W_of(th, GRID.x, 3, P)
    ref = equality_potential(GAMMA, GRID).reshape(-1)
    assert torch.allclose(W[:, 0, 0], ref, atol=1e-12)
    assert float(W[:, 1:, :].abs().max()) == 0.0 and float(W[:, :, 1:].abs().max()) == 0.0
    ratio = math.exp(sv.log_ratio_true(th, GAMMA, 3, P, GRID))
    assert abs(ratio / sharp_constant(GAMMA) - 1.0) < 1e-6


def test_build_H_reproduces_instrument_negative_spectrum() -> None:
    g = torch.Generator().manual_seed(11)
    theta = sv.theta_star(GAMMA, 2, P) + 0.2 * torch.randn(sv.n_params(2, P), generator=g)  # a generic matrix potential with a bound state
    W = sv.W_of(theta, GRID.x, 2, P)
    _, _, neg = numerator_denominator(W, GAMMA, GRID)
    E = torch.linalg.eigvalsh(sv.build_H(W, GRID))
    assert neg.numel() >= 1
    mine = (-E[E < 0]).sort(descending=True).values
    assert mine.shape == neg.shape
    assert torch.allclose(mine, neg.sort(descending=True).values, atol=1e-10)


@pytest.mark.parametrize("m", [1, 2, 3])
def test_flat_direction_counts_and_complement(m: int) -> None:
    flats = sv.flat_directions(GAMMA, m, P)
    assert len(flats) == 2 + (4 * m - 3)  # translation, dilation, plus left-gauge/right-rotation tangents
    names = ("translation", "dilation")
    Z = sv.complement_basis([flats[k] / flats[k].norm() for k in names])
    assert Z.shape == (sv.n_params(m, P), sv.n_params(m, P) - 2)
    assert float((Z.T @ Z - torch.eye(Z.shape[1])).abs().max()) < 1e-12
    for k in names:
        assert float((Z.T @ flats[k]).abs().max()) < 1e-12


def test_scalar_hessian_is_nonpositive_flat_directions_vanish_and_autograd_matches_fd() -> None:
    m = 1
    th0 = sv.theta_star(GAMMA, m, P)
    sur = sv.Surrogate(GAMMA, m, P, GRID, th0)
    assert abs(float(sur.log_ratio(th0)) - sv.log_ratio_true(th0, GAMMA, m, P, GRID)) < 1e-10
    H, g = sv.autograd_hessian(sur.log_ratio, th0)
    assert float(g.norm()) < 1e-6  # B* is a critical point of the proved scalar maximiser
    flats = sv.flat_directions(GAMMA, m, P)
    for name, v in flats.items():
        u = v / v.norm()
        assert abs(float(u @ H @ u)) < 1e-6, name
    Z = sv.complement_basis([flats["translation"] / flats["translation"].norm(), flats["dilation"] / flats["dilation"].norm()])
    ev = torch.linalg.eigvalsh(Z.T @ H @ Z)
    assert float(ev[-1]) < 1e-6  # all eigenvalues <= noise: proved maximiser (control a)
    assert float(ev[0]) < -1e-3  # and the spectrum is not trivially zero: some shape directions really bend
    v = torch.randn(th0.numel(), generator=torch.Generator().manual_seed(5))
    v = v / v.norm()
    f_true = lambda t: sv.log_ratio_true(t, GAMMA, m, P, GRID)
    assert abs(sv.fd_second(f_true, th0, v, 1e-3) - float(v @ H @ v)) < 1e-3 * max(1.0, abs(float(v @ H @ v)))


def test_cell_verdict_logic_covers_void_and_positive_branches() -> None:
    # Pure bookkeeping of the verdict logic; the physical negative control is run by the cell driver (needs the large grid).
    base = {"control_d_rank_one_fd_matches_autograd": True, "control_d_surrogate_fd_matches_autograd": True,
            "control_b_quad_translation_dilation_max": 1e-10, "n_positive_beyond_thr": 0, "n_confirmed_positive": 0}
    assert sv.cell_verdict(base, 1e-8) == "NONPOSITIVE_SECOND_VARIATION"
    assert sv.cell_verdict({**base, "n_positive_beyond_thr": 2}, 1e-8) == "UNDECIDED_POSITIVE_UNCONFIRMED"
    assert sv.cell_verdict({**base, "n_positive_beyond_thr": 2, "n_confirmed_positive": 1}, 1e-8) == "POSITIVE_CONFIRMED_KILLS_H_LT3"
    assert sv.cell_verdict({**base, "control_b_quad_translation_dilation_max": 1e-5}, 1e-8) == "VOID_FLAT_DIRECTION_NOT_FLAT"
    assert sv.cell_verdict({**base, "control_d_rank_one_fd_matches_autograd": False}, 1e-8) == "VOID_FD_DISAGREES"
    assert sv.cell_verdict({**base, "gradient_norm": 0.4}, 1e-8) == "VOID_NOT_CRITICAL"
    assert sv.cell_verdict({**base, "gradient_norm": 0.4, "n_confirmed_positive": 3}, 1e-8, negative_control=True) == "NEGATIVE_CONTROL_PASS"
    assert sv.cell_verdict({**base, "gradient_norm": 0.4}, 1e-8, negative_control=True) == "NEGATIVE_CONTROL_FAIL"
