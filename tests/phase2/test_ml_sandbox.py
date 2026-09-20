import pytest

from anse.config import SandboxConfig
from anse.symbolic.ml_sandbox import MLSandboxExecutor


@pytest.fixture
def sandbox():
    cfg = SandboxConfig(timeout_seconds=30.0)
    return MLSandboxExecutor(cfg=cfg)


class TestMLSandboxExecutor:
    def test_successful_training(self, sandbox):
        code = """
import torch.nn as nn
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(20, 2)
    def forward(self, x):
        return self.fc(x)
"""
        result = sandbox.execute(code)
        assert result.returncode == 0
        assert result.parameters == 42  # (20 * 2) + 2
        assert result.val_loss < float("inf")
        assert not result.is_shape_mismatch

    def test_shape_mismatch_detection(self, sandbox):
        code = """
import torch.nn as nn
class BadModel(nn.Module):
    def __init__(self):
        super().__init__()
        # Intentional shape mismatch (input is 20)
        self.fc = nn.Linear(15, 2)
    def forward(self, x):
        return self.fc(x)
"""
        result = sandbox.execute(code)
        assert result.returncode != 0
        assert result.is_shape_mismatch
