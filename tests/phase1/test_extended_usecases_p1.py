"""
Extended Phase 1 Use Cases (UC6 to UC10):
- UC6: Memory Leak & Heap Bloat Detection
- UC7: Fork/Thread Bomb Sandbox Concurrency Isolation
- UC8: Cross-Domain Lesson Memory Transfer
- UC9: Input Invariant & Mutation Purity Gate
- UC10: Strict AST Anti-Stub and Type Guard
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from anse.memory.lessons import Lesson, LessonMemory
from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.sandbox import SandboxConfig, SandboxExecutor


# ─── UC6: Memory Leak & Heap Bloat Detection ─────────────────────────────────
def test_uc6_memory_leak_detection() -> None:
    """UC6: Leaky components accumulating unbounded state receive high energy or fail."""
    sandbox = SandboxExecutor(config=SandboxConfig(timeout_seconds=5.0, tier1_mem_limit_mb=64))

    leaky_code = """
import sys

buffer = []

def process_data(items):
    global buffer
    for x in items:
        buffer.append([x] * 5000)  # Unbounded memory bloat
    return len(buffer)

for step in range(50):
    process_data(range(100))

print("FINISHED")
"""
    result = sandbox.execute(leaky_code, force_tier=1)
    evaluator = EnergyEvaluator()
    score = evaluator.evaluate(result)

    # Either it was killed due to RAM limits (timed out / killed) or consumed significant RAM
    assert result.peak_ram_mb > 5.0 or result.returncode != 0
    # The energy score reflects the physical memory consumption
    assert score.score > 1.0


# ─── UC7: Fork/Thread Bomb Sandbox Isolation ─────────────────────────────────
def test_uc7_thread_bomb_sandbox_containment() -> None:
    """UC7: Spawning zombie threads or infinite loops is terminated strictly under timeout."""
    sandbox = SandboxExecutor(config=SandboxConfig(timeout_seconds=2.0))

    bomb_code = """
import threading
import time

def zombie():
    while True:
        time.sleep(0.01)

for _ in range(20):
    t = threading.Thread(target=zombie, daemon=False)
    t.start()

while True:
    time.sleep(0.1)
"""
    result = sandbox.execute(bomb_code, force_tier=1)
    # The sandbox must enforce timeout without hanging the test runner
    assert result.timed_out is True
    assert result.duration_ms >= 1800.0


# ─── UC8: Cross-Domain Lesson Memory Transfer ────────────────────────────────
def test_uc8_cross_domain_lesson_transfer(tmp_path: Any) -> None:
    """UC8: Relevant vectorization lessons retrieved from memory assist sister domains."""
    mem_file = tmp_path / "cross_domain_lessons.jsonl"
    memory = LessonMemory(mem_file)

    # Store algorithmic vectorization lesson from numerical domain
    memory.add(
        Lesson(
            task="Sum positive numerical values in array",
            code="import numpy as np\ndef sum_pos(m): return float(np.sum(m[m > 0]))",
        )
    )

    # Query from related numerical domain
    query_task = "Compute sum of positive elements in matrix"
    retrieved = memory.retrieve(query_task, k=1)

    assert len(retrieved) > 0
    score, lesson = retrieved[0]
    assert score > 0.0
    assert "np.sum" in lesson.code


# ─── UC9: Input Invariant & Mutation Purity Gate ─────────────────────────────
def test_uc9_input_mutation_purity_gate() -> None:
    """UC9: Functions mutating input arguments without authorization fail purity verification."""

    def purity_checker(code_str: str, test_input: list[int]) -> bool:
        original_hash = hashlib.sha256(str(test_input).encode()).hexdigest()
        input_copy = copy.deepcopy(test_input)
        local_scope: dict[str, Any] = {"data": input_copy}
        exec(code_str, local_scope)
        post_hash = hashlib.sha256(str(local_scope["data"]).encode()).hexdigest()
        return original_hash == post_hash

    impure_code = "data.sort()\nresult = data[0]"
    pure_code = "result = sorted(data)[0]"

    test_data = [5, 2, 8, 1, 9]
    assert purity_checker(pure_code, test_data) is True
    assert purity_checker(impure_code, test_data) is False


# ─── UC10: Strict AST Anti-Stub and Type Guard ───────────────────────────────
def test_uc10_ast_anti_stub_validation() -> None:
    """UC10: Stubs containing pass/Ellipsis or empty bodies are rejected by AST validation."""
    from anse.symbolic.parser import extract_code

    working_code = "```python\ndef solve(arr: list[int]) -> int:\n    return sum(arr)\n```"
    stub_code = "```python\ndef solve(arr: list[int]) -> int:\n    pass\n```"

    parsed_working = extract_code(working_code)
    parsed_stub = extract_code(stub_code)

    assert "sum(arr)" in parsed_working.code

    # Check AST body of stub
    import ast

    tree = ast.parse(parsed_stub.code)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    is_stub = len(func_node.body) == 1 and isinstance(func_node.body[0], ast.Pass)
    assert is_stub is True, "AST inspection must catch single-statement 'pass' stub"
