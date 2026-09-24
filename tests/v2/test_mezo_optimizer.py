"""Tests for ANSE 2.0 Zeroth-Order MeZO Plasticity Optimizer."""

import torch
import torch.nn as nn

from anse.v2.mezo_optimizer import EdgeContinuousPlasticityEngine, MeZOOptimizer


class SimpleToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(8, 1)

    def forward(self, x):
        return self.fc(x)


def test_mezo_step_convergence():
    torch.manual_seed(42)
    model = SimpleToyModel()
    optimizer = MeZOOptimizer(model, lr=0.05, epsilon=1e-3)

    x = torch.randn(16, 8)
    target = torch.randn(16, 1)

    def loss_fn():
        pred = model(x)
        return nn.functional.mse_loss(pred, target)

    initial_loss = float(loss_fn().item())

    # Run multiple MeZO steps
    for _ in range(20):
        step_res = optimizer.step(loss_fn)

    final_loss = float(loss_fn().item())

    # Loss should descend using only forward passes
    assert final_loss < initial_loss
    assert step_res.step == 20


def test_mezo_zero_gradient_allocation():
    model = SimpleToyModel()
    optimizer = MeZOOptimizer(model, lr=0.01)

    x = torch.randn(4, 8)
    target = torch.randn(4, 1)

    def loss_fn():
        pred = model(x)
        return nn.functional.mse_loss(pred, target)

    step_res = optimizer.step(loss_fn)
    assert step_res.loss_positive is not None

    # All parameter gradients should remain None because MeZO never calls loss.backward()
    for p in model.parameters():
        assert p.grad is None


def test_edge_continuous_plasticity():
    class TwoInputNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Linear(16, 8)

        def forward(self, s, a):
            return self.net(torch.cat([s, a], dim=-1))

    model = TwoInputNet()
    engine = EdgeContinuousPlasticityEngine(model, lr=0.05)

    s = torch.randn(4, 8)
    a = torch.randn(4, 8)
    actual = torch.randn(4, 8)

    res = engine.adapt_on_prediction_surprise(s, a, actual)
    assert res.step == 1
    assert len(engine.history) == 1
