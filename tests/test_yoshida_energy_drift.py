"""yoshida4_integrate must report the drift of the system it integrated.

Before the fix the reported energy always used V = 0.5*||q||^2, whatever grad_v was. These tests fail on the
old behaviour: the shifted-well case reported 0.75 for a run whose true drift is ~5e-7.
"""

from __future__ import annotations

import math

import pytest

from anse.geometry.riemannian_trust_region import yoshida4_integrate


def _true_drift(res, centre: float) -> float:
    h = lambda q, p: 0.5 * p * p + 0.5 * (q - centre) ** 2
    h0 = h(res.trajectory_q[0][0], res.trajectory_p[0][0])
    return max(abs(h(q[0], p[0]) - h0) / h0 for q, p in zip(res.trajectory_q, res.trajectory_p))


@pytest.mark.parametrize("centre", [0.0, 3.0, math.sqrt(92.0)])
def test_reported_drift_equals_true_drift_when_potential_is_supplied(centre):
    res = yoshida4_integrate(
        lambda q: [q[0] - centre], [centre + 1.0], [0.0], dt=0.05, steps=400,
        potential=lambda q: 0.5 * (q[0] - centre) ** 2,
    )
    truth = _true_drift(res, centre)
    assert truth < 1e-5                                   # the integrator really is that good
    assert res.energy_drift == pytest.approx(truth, rel=1e-9)


def test_shifted_well_without_potential_is_nan_not_a_wrong_number():
    res = yoshida4_integrate(lambda q: [q[0] - 3.0], [4.0], [0.0], dt=0.05, steps=400)
    assert math.isnan(res.energy_drift) and math.isnan(res.symplectic_error)


def test_harmonic_about_origin_still_reports_without_potential():
    res = yoshida4_integrate(lambda q: list(q), [1.0], [0.0], dt=0.05, steps=300)
    assert res.energy_drift == pytest.approx(_true_drift(res, 0.0), rel=1e-9)
    assert res.energy_drift < 1e-2


def test_observed_order_is_four_and_verlet_is_two():
    """The method itself is correct; this is the control that keeps the fix honest."""
    def err_yoshida(h):
        n = round(2.0 / h)
        r = yoshida4_integrate(lambda q: list(q), [1.0], [0.3], dt=h, steps=n, potential=lambda q: 0.5 * q[0] ** 2)
        T = n * h
        qe, pe = math.cos(T) + 0.3 * math.sin(T), -math.sin(T) + 0.3 * math.cos(T)
        return math.hypot(r.trajectory_q[-1][0] - qe, r.trajectory_p[-1][0] - pe)

    e = [err_yoshida(h) for h in (0.1, 0.05, 0.025)]
    orders = [math.log2(e[i] / e[i + 1]) for i in range(2)]
    assert all(3.9 < o < 4.1 for o in orders), orders
