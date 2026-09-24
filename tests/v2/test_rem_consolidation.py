"""Tests for ANSE 2.0 Biological REM Sleep & EWC Consolidation."""

import torch
import torch.nn as nn

from anse.v2.rem_consolidation import REMSleepDaemon


class SimpleLinearNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(8, 4)

    def forward(self, x):
        return self.fc(x)


def test_fisher_information_computation():
    model = SimpleLinearNet()
    daemon = REMSleepDaemon(model, ewc_lambda=100.0)

    # Log several wake episodes across different domains
    for d in ["pure_math", "pure_physics", "rust_numeric", "complex_python"]:
        s = torch.randn(4, 8)
        t = torch.randn(4, 4)
        daemon.log_wake_episode(domain=d, input_state=s, target_output=t)

    assert len(daemon.hippocampus) == 4

    mean_fisher = daemon.ewc.compute_fisher_information(daemon.hippocampus)
    assert mean_fisher >= 0.0

    # Every parameter should have a non-negative Fisher diagonal
    for name, f_diag in daemon.ewc.fisher_matrix.items():
        assert bool((f_diag >= 0.0).all())


def test_rem_sleep_consolidation_cycle():
    model = SimpleLinearNet()
    daemon = REMSleepDaemon(model, ewc_lambda=200.0)

    # Log 6 anchor traces
    for i in range(6):
        s = torch.randn(4, 8)
        t = torch.randn(4, 4)
        daemon.log_wake_episode(domain=f"domain_{i % 2}", input_state=s, target_output=t)

    summary = daemon.execute_rem_sleep_cycle(epochs=3)

    assert summary.cycle_id == 1
    assert summary.anchor_traces_replayed == 6
    assert summary.mean_fisher_diagonal >= 0.0
    assert summary.orthogonal_projection_applied is True
