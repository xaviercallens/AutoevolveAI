"""
Unit tests for RCUComponentProxy and AutopoiesisHypervisor zero-downtime hot-swapping.
"""

from __future__ import annotations

import concurrent.futures
import time
from typing import Any

import pytest

from anse.autopoiesis.hypervisor import AutopoiesisHypervisor, RCUComponentProxy
from anse.autopoiesis.registry import ComponentRegistry


def test_rcu_proxy_lifecycle() -> None:
    def v1_add(a: int, b: int) -> int:
        return a + b

    def v2_add(a: int, b: int) -> int:
        return (a + b) * 10

    proxy = RCUComponentProxy(v1_add, name="add_comp", version=1)
    assert proxy.name == "add_comp"
    assert proxy.version == 1
    assert proxy.call_count == 0

    # Call v1
    res1 = proxy(2, 3)
    assert res1 == 5
    assert proxy.call_count == 1

    # Atomic swap to v2
    new_ver = proxy.swap(v2_add, new_version=2)
    assert new_ver == 2
    assert proxy.version == 2

    # Call v2
    res2 = proxy(2, 3)
    assert res2 == 50
    assert proxy.call_count == 2


def test_rcu_proxy_non_callable_rejection() -> None:
    proxy = RCUComponentProxy(lambda x: x, name="echo")
    with pytest.raises(TypeError, match="must be callable"):
        proxy.swap("not a function")  # type: ignore[arg-type]


def test_rcu_proxy_multithreaded_concurrency() -> None:
    """Stress test: 10 worker threads concurrently calling proxy while main thread hot-swaps versions."""

    def fn_v1(x: int) -> tuple[int, int]:
        time.sleep(0.0001)
        return 1, x * 2

    def fn_v2(x: int) -> tuple[int, int]:
        time.sleep(0.0001)
        return 2, x * 2

    def fn_v3(x: int) -> tuple[int, int]:
        time.sleep(0.0001)
        return 3, x * 2

    proxy = RCUComponentProxy(fn_v1, name="multithreaded", version=1)

    errors: list[str] = []
    iterations_per_worker = 100

    def worker_loop() -> None:
        for i in range(iterations_per_worker):
            try:
                version_tag, val = proxy(i)
                if val != i * 2:
                    errors.append(f"Inconsistent calculation: {val} != {i * 2}")
                if version_tag not in (1, 2, 3):
                    errors.append(f"Invalid version tag: {version_tag}")
            except Exception as exc:
                errors.append(f"Exception during call: {exc}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker_loop) for _ in range(10)]

        # Rapid hot-swaps across live threads
        time.sleep(0.002)
        proxy.swap(fn_v2, new_version=2)
        time.sleep(0.002)
        proxy.swap(fn_v3, new_version=3)

        for fut in futures:
            fut.result()

    assert not errors, f"Concurrency errors observed: {errors[:5]}"
    assert proxy.call_count == 10 * iterations_per_worker
    assert proxy.version == 3


def test_hypervisor_proxy_integration(tmp_path: Any) -> None:
    """Test that AutopoiesisHypervisor automatically updates registered proxies on promotion."""
    reg = ComponentRegistry(tmp_path / "registry")

    parent_code = "def fast_sum(n):\n    s = 0\n    for i in range(n):\n        s += i\n    return s\n"
    reg.register("fast_sum", parent_code)

    def initial_impl(n: int) -> int:
        return sum(range(n))

    hv = AutopoiesisHypervisor(reg)
    proxy = hv.register_proxy("fast_sum", initial_impl)
    assert proxy.version == 1
    assert hv.get_proxy("fast_sum") is proxy

    # Check calling through proxy
    assert proxy(10) == 45

    # Child code that vectorizes or multiplies by 2
    child_code = "def fast_sum(n):\n    return sum(range(n))\n"
    tests = ["assert fast_sum(5) == 10", "assert fast_sum(10) == 45"]
    workload = "BENCH_RESULT = fast_sum(1000)"

    decision = hv.evolve("fast_sum", child_code, tests, workload)
    if decision.promoted:
        # Proxy should have been automatically swapped to version 2
        assert proxy.version == 2
