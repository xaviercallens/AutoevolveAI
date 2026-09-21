"""
Unit tests for the Context Packer skeletonizer.
"""

from __future__ import annotations

from context_packer import pack_code_skeleton


def test_pack_function_skeleton() -> None:
    source = """
def calculate_metrics(values: list[float], factor: float = 1.0) -> float:
    \"\"\"Calculates physical energy metrics.\"\"\"
    total = sum(values) * factor
    normalized = total / (len(values) or 1)
    return normalized
"""
    skeleton = pack_code_skeleton(source)
    assert "def calculate_metrics(" in skeleton
    assert '"""Calculates physical energy metrics."""' in skeleton
    assert "..." in skeleton
    assert "total = sum(values)" not in skeleton


def test_pack_class_skeleton() -> None:
    source = """
class RateLimiter:
    \"\"\"Redis-backed token bucket.\"\"\"

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def acquire(self, tokens: int = 1) -> bool:
        \"\"\"Acquire token bucket permit.\"\"\"
        if self.capacity >= tokens:
            self.capacity -= tokens
            return True
        return False
"""
    skeleton = pack_code_skeleton(source)
    assert "class RateLimiter:" in skeleton
    assert "def __init__(self, capacity: int, refill_rate: float) -> None:" in skeleton
    assert "async def acquire(" in skeleton
    assert '"""Acquire token bucket permit."""' in skeleton
    assert "self.capacity -= tokens" not in skeleton


def test_pack_syntax_error_fallback() -> None:
    invalid_code = "def unclosed_func(:"
    skeleton = pack_code_skeleton(invalid_code)
    assert skeleton == invalid_code
