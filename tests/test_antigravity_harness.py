"""
Tests for Antigravity Harness:
Validates ContextOrchestrator, AntiStubGuard, Lean4Verifier, RedisBus,
QAAgent, OptimizerAgent, Test Runners, and DPO Pipeline.
"""

from __future__ import annotations

import json

from antigravity_harness.agents.optimizer_agent import OptimizerAgent
from antigravity_harness.agents.qa_agent import QAAgent
from antigravity_harness.core.anti_stub_guard import AntiStubGuard
from antigravity_harness.core.context_orchestrator import (
    ContextBudget,
    ContextOrchestrator,
    ContextTier,
)
from antigravity_harness.core.lean4_verifier import Lean4Verifier
from antigravity_harness.rl_pipeline.dpo_dataset_builder import (
    DPODatasetBuilder,
    DPOPreferencePair,
)
from antigravity_harness.rl_pipeline.trace_extractor import TraceExtractor
from antigravity_harness.storage.redis_bus import RedisBus, TraceRecord
from antigravity_harness.tests_runner.unit_integration import UnitIntegrationRunner
from antigravity_harness.tests_runner.visual_regression import VisualRegressionRunner

# ─── 1. Context Orchestrator Tests ───────────────────────────────────────────


def test_context_orchestrator_token_estimation():
    orchestrator = ContextOrchestrator()
    tokens = orchestrator.estimate_tokens("def hello(): return 'world'")
    assert tokens > 0


def test_context_orchestrator_skeletonize():
    code = (
        "def compute_fibonacci(n: int) -> int:\n"
        '    """Calculates n-th Fibonacci number."""\n'
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n"
    )
    orchestrator = ContextOrchestrator()
    skeleton = orchestrator.skeletonize_code(code)
    assert "Calculates n-th Fibonacci number." in skeleton
    assert "..." in skeleton
    assert "a, b = b, a + b" not in skeleton


def test_context_orchestrator_offload_scratchpad(tmp_path):
    orchestrator = ContextOrchestrator(scratchpad_dir=tmp_path)
    long_output = "\n".join(f"line {i}" for i in range(100))
    result = orchestrator.offload_large_output("test_tool", long_output, max_inline_lines=30)
    assert "[CONTEXT OFF-LOADED" in result
    assert "line 0" in result
    assert "line 99" in result
    # Assert log file created
    logs = list(tmp_path.glob("test_tool_*.log"))
    assert len(logs) == 1
    assert "line 50" in logs[0].read_text()


def test_context_orchestrator_pack_codebase():
    budget = ContextBudget(max_tokens=100)
    budget.codebase_budget = 20  # Tight budget
    orchestrator = ContextOrchestrator(budget=budget)

    files = {
        "main.py": "def main():\n    print('Hello World')\n",
        "helper.py": "def helper():\n    '''Helper docstring.'''\n    x = 100\n    return x * 2\n",
    }
    packed = orchestrator.pack_codebase(files, priority_files={"main.py"})
    assert packed["main.py"][1] == ContextTier.FULL
    assert packed["helper.py"][1] == ContextTier.SKELETON


# ─── 2. Anti-Stub Guard Tests ────────────────────────────────────────────────


def test_anti_stub_guard_clean_code():
    guard = AntiStubGuard()
    code = (
        "def add(a: int, b: int) -> int:\n"
        '    """Adds two numbers."""\n'
        "    result = a + b\n"
        "    return result\n"
    )
    audit = guard.audit_code(code)
    assert audit.is_clean
    assert audit.penalty_energy == 0.0


def test_anti_stub_guard_flags_pass_stub():
    guard = AntiStubGuard()
    code = "def stubbed_function():\n    pass\n"
    audit = guard.audit_code(code)
    assert not audit.is_clean
    assert any(v.rule == "PASS_STUB" for v in audit.violations)
    assert audit.penalty_energy == 1_000_000.0


def test_anti_stub_guard_flags_ellipsis_stub():
    guard = AntiStubGuard()
    code = "def stubbed_function():\n    ...\n"
    audit = guard.audit_code(code)
    assert not audit.is_clean
    assert any(v.rule == "ELLIPSIS_STUB" for v in audit.violations)


def test_anti_stub_guard_flags_not_implemented():
    guard = AntiStubGuard()
    code = "def pending_work():\n    raise NotImplementedError('TODO')\n"
    audit = guard.audit_code(code)
    assert not audit.is_clean
    assert any(v.rule == "NOT_IMPLEMENTED_STUB" for v in audit.violations)


def test_anti_stub_guard_flags_synthetic_mock_data():
    guard = AntiStubGuard()
    code = "def load_users():\n    mock_users = [{'id': 1}]\n    return mock_users\n"
    audit = guard.audit_code(code, filename="production/users.py")
    assert not audit.is_clean
    assert any(v.rule == "SYNTHETIC_MOCK_DATA" for v in audit.violations)


def test_anti_stub_guard_flags_sleep_simulation():
    guard = AntiStubGuard()
    code = "import time\ndef heavy_computation():\n    time.sleep(2)\n    return 42\n"
    audit = guard.audit_code(code, filename="engine.py")
    assert not audit.is_clean
    assert any(v.rule == "TIME_SLEEP_SIMULATION" for v in audit.violations)


# ─── 3. Lean 4 Verifier Tests ────────────────────────────────────────────────


def test_lean4_verifier_scan_theorems(tmp_path):
    lean_file = tmp_path / "Spec.lean"
    lean_file.write_text(
        "import Lean\n\n"
        "theorem energy_monotone (a b : Nat) : a <= b -> a + 1 <= b + 1 := by\n"
        "  intro h\n"
        "  exact Nat.succ_le_succ h\n\n"
        "lemma aux_step : True := by trivial\n"
    )
    verifier = Lean4Verifier(formal_dir=tmp_path)
    theorems = verifier.extract_theorems(tmp_path)
    assert "energy_monotone" in theorems
    assert "aux_step" in theorems


def test_lean4_verifier_detects_sorry(tmp_path):
    lean_file = tmp_path / "Unsound.lean"
    lean_file.write_text("theorem cheat : False := by\n  sorry\n")
    verifier = Lean4Verifier(formal_dir=tmp_path)
    count, occurrences = verifier.scan_for_sorry(tmp_path)
    assert count == 1
    assert len(occurrences) == 1
    assert "sorry" in occurrences[0]


# ─── 4. Redis Bus Tests ──────────────────────────────────────────────────────


def test_redis_bus_in_memory_streams():
    bus = RedisBus(use_mock=True)
    msg_id = bus.publish_event("tasks", {"task_id": "t1", "action": "benchmark"})
    assert msg_id

    events = bus.consume_events("tasks", last_id="0")
    assert len(events) == 1
    assert events[0][1]["task_id"] == "t1"
    assert events[0][1]["action"] == "benchmark"


def test_redis_bus_trace_storage():
    bus = RedisBus(use_mock=True)
    trace = TraceRecord(
        trace_id="tr_100",
        subtask_id="sub_1",
        prompt="Write sort function",
        completion="def sort_fn(arr): return sorted(arr)",
        verdict="PASSED",
        energy=12.5,
    )
    bus.record_trace(trace)

    retrieved = bus.get_trace("tr_100")
    assert retrieved is not None
    assert retrieved.trace_id == "tr_100"
    assert retrieved.verdict == "PASSED"
    assert retrieved.energy == 12.5


def test_redis_bus_vector_search():
    bus = RedisBus(use_mock=True)
    bus.store_vector("vec_1", [1.0, 0.0, 0.0], {"name": "first"})
    bus.store_vector("vec_2", [0.0, 1.0, 0.0], {"name": "second"})

    results = bus.search_vectors([0.9, 0.1, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0][0] == "vec_1"
    assert results[0][1] > 0.9


# ─── 5. QA Agent Tests ───────────────────────────────────────────────────────


def test_qa_agent_adversarial_suite():
    agent = QAAgent()
    code = (
        "def process_user_query(query: str, limit: int = 10) -> list[str]:\n"
        "    return [query] * limit\n"
    )
    report = agent.generate_adversarial_suite("my_module", code)
    assert report.target_name == "process_user_query"
    assert report.num_tests_generated >= 3
    assert "test_process_user_query_handles_none" in report.test_code
    assert "test_process_user_query_numeric_boundaries" in report.test_code
    assert "test_process_user_query_stress_scale" in report.test_code


# ─── 6. Optimizer Agent Tests ────────────────────────────────────────────────


def test_optimizer_agent_bottleneck_detection():
    agent = OptimizerAgent()
    bad_code = (
        "def find_duplicates(items: list[int]) -> list[int]:\n"
        "    dups = []\n"
        "    for i in range(len(items)):\n"
        "        for j in range(i + 1, len(items)):\n"
        "            if items[i] == items[j] and items[i] not in dups:\n"
        "                dups.append(items[i])\n"
        "    return dups\n"
    )
    bottlenecks = agent.detect_algorithmic_bottlenecks(bad_code)
    assert any("Nested loop detected" in b for b in bottlenecks)


def test_optimizer_agent_profile_callable():
    agent = OptimizerAgent()

    def sample_work():
        return sum(i * i for i in range(1000))

    energy = agent.profile_callable(sample_work, benchmark_runs=2)
    assert energy.duration_ms >= 0.0
    assert energy.peak_ram_mb >= 0.0
    assert energy.total_energy >= 0.0


# ─── 7. Unit Integration Runner Tests ────────────────────────────────────────


def test_unit_integration_runner_parsing():
    runner = UnitIntegrationRunner()
    sample_output = "===== 87 passed, 4 failed, 12 skipped in 10.20s ====="
    passed, failed, skipped = runner._parse_pytest_counts(sample_output)
    assert passed == 87
    assert failed == 4
    assert skipped == 12


# ─── 8. Visual Regression Runner Tests ───────────────────────────────────────


def test_visual_regression_identical_files(tmp_path):
    runner = VisualRegressionRunner()
    file_a = tmp_path / "baseline.png"
    file_b = tmp_path / "candidate.png"

    from PIL import Image

    img = Image.new("RGBA", (4, 4), (255, 0, 0, 255))
    img.save(file_a)
    img.save(file_b)

    res = runner.compare_images(file_a, file_b)
    assert res.passed
    assert res.mismatched_pixels == 0


# ─── 9. RL & DPO Pipeline Tests ──────────────────────────────────────────────


def test_dpo_pipeline_flow(tmp_path):
    # Setup bus and trace extractor
    bus = RedisBus(use_mock=True)

    trace_pass = TraceRecord(
        trace_id="t_pass",
        subtask_id="task_calc",
        prompt="Calculate sum",
        completion="def calc(a, b): return a + b",
        verdict="PASSED",
        energy=10.0,
    )
    trace_fail = TraceRecord(
        trace_id="t_fail",
        subtask_id="task_calc",
        prompt="Calculate sum",
        completion="def calc(a, b): pass",  # Has stub
        verdict="FAILED",
        energy=1000000.0,
    )
    bus.record_trace(trace_pass)
    bus.record_trace(trace_fail)

    extractor = TraceExtractor(bus)
    sessions = extractor.extract_from_bus()
    assert len(sessions) == 1
    session = sessions[0]
    assert session.is_dpo_ready
    assert session.best_trace().trace_id == "t_pass"

    # Build DPO dataset
    builder = DPODatasetBuilder()
    pairs = builder.build_pairs_from_sessions(sessions)
    assert len(pairs) == 1
    pair = pairs[0]
    assert pair.chosen == "def calc(a, b): return a + b"
    assert pair.rejected == "def calc(a, b): pass"
    assert pair.energy_delta < 0  # Chosen has lower energy

    # Export to jsonl
    out_file = tmp_path / "dpo_dataset.jsonl"
    builder.export_to_jsonl(pairs, out_file)
    assert out_file.exists()
    data = json.loads(out_file.read_text().splitlines()[0])
    assert data["chosen"] == pair.chosen


# ─── 10. Additional Feature Tests ─────────────────────────────────────────────


def test_context_orchestrator_sliding_window():
    orchestrator = ContextOrchestrator()
    messages = [
        {"role": "user", "parts": [{"text": "system task definition"}]},
        {"role": "model", "parts": [{"text": "turn 1 response " * 50}]},
        {"role": "user", "parts": [{"text": "turn 2 question " * 50}]},
        {"role": "model", "parts": [{"text": "turn 3 answer " * 50}]},
        {"role": "user", "parts": [{"text": "latest active request"}]},
    ]
    # Set limit to keep only first message and last message
    window = orchestrator.slide_conversation_window(messages, max_turn_tokens=50)
    assert len(window) < len(messages)
    assert window[0]["parts"][0]["text"] == "system task definition"
    assert window[-1]["parts"][0]["text"] == "latest active request"


def test_context_orchestrator_diff_compaction():
    orchestrator = ContextOrchestrator()
    huge_diff = "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n@@ -1,10 +1,50 @@\n"
    huge_diff += "\n".join(f"+ added line {i}" for i in range(50))
    compacted = orchestrator.compact_unified_diff(huge_diff, max_lines_per_hunk=10)
    assert "... [diff hunk truncated] ..." in compacted
    assert "diff --git a/file.py" in compacted


def test_context_orchestrator_tool_declaration():
    orchestrator = ContextOrchestrator()
    decl = orchestrator.format_gemini_tool_declaration(
        tool_name="execute_python",
        description="Executes python code in sandbox",
        parameters={"properties": {"code": {"type": "string"}}, "required": ["code"]},
    )
    assert decl["name"] == "execute_python"
    assert decl["parameters"]["type"] == "OBJECT"
    assert "code" in decl["parameters"]["properties"]


def test_anti_stub_guard_trivial_constant_return():
    guard = AntiStubGuard()
    code = "def check_validity(user_id: int, token: str) -> bool:\n    return True\n"
    audit = guard.audit_code(code)
    assert not audit.is_clean
    assert any(v.rule == "TRIVIAL_CONSTANT_RETURN" for v in audit.violations)


def test_anti_stub_guard_silent_try_pass():
    guard = AntiStubGuard()
    code = (
        "def safe_execute(action: str) -> None:\n"
        "    try:\n"
        "        do_work(action)\n"
        "    except Exception:\n"
        "        pass\n"
    )
    audit = guard.audit_code(code, filename="service.py")
    assert not audit.is_clean
    assert any(v.rule == "SILENT_EXCEPTION_SWALLOW" for v in audit.violations)


def test_anti_stub_guard_mock_instantiation():
    guard = AntiStubGuard()
    code = "def get_database():\n    db = MagicMock()\n    return db\n"
    audit = guard.audit_code(code, filename="database/connection.py")
    assert not audit.is_clean
    assert any(v.rule == "MOCK_INSTANTIATION" for v in audit.violations)


def test_lean4_verifier_proof_inventory_and_soundness(tmp_path):
    lean_file = tmp_path / "Model.lean"
    lean_file.write_text(
        "theorem t1 : True := by trivial\n"
        "lemma l1 : True := by trivial\n"
        "def identity (x : Nat) : Nat := x\n"
    )
    verifier = Lean4Verifier(formal_dir=tmp_path)
    inv = verifier.extract_proof_inventory(tmp_path)
    assert "t1" in inv["theorems"]
    assert "l1" in inv["lemmas"]
    assert "identity" in inv["definitions"]

    sound, msg = verifier.check_soundness(tmp_path)
    assert sound
    assert "Soundness verified" in msg


def test_redis_bus_batch_and_ttl():
    bus = RedisBus(use_mock=True)
    bus.store_vector("v1", [1.0, 0.0], {"id": 1})
    bus.store_vector("v2", [0.0, 1.0], {"id": 2})

    batch_results = bus.batch_search_vectors([[1.0, 0.0], [0.0, 1.0]], top_k=1)
    assert len(batch_results) == 2
    assert batch_results[0][0][0] == "v1"
    assert batch_results[1][0][0] == "v2"

    ttl_ok = bus.set_with_ttl("temp_key", "temporary_value", ttl_seconds=60)
    assert ttl_ok


def test_redis_bus_trim_stream():
    bus = RedisBus(use_mock=True)
    for i in range(10):
        bus.publish_event("large_stream", {"idx": str(i)})
    trimmed = bus.trim_stream("large_stream", max_len=3)
    assert trimmed == 7
    remaining = bus.consume_events("large_stream", last_id="0", count=10)
    assert len(remaining) == 3


def test_qa_agent_property_test_generation():
    agent = QAAgent()
    code = "def calculate_ratio(numerator: int, denominator: int) -> float:\n    return numerator / denominator\n"
    prop_test = agent.generate_property_tests("math_engine", code)
    assert "from hypothesis import given" in prop_test
    assert "st.integers()" in prop_test
    assert "test_calculate_ratio_fuzz_properties" in prop_test


def test_optimizer_agent_vectorization_and_speedup():
    agent = OptimizerAgent()
    source = (
        "def scale_values(items: list[float]) -> list[float]:\n"
        "    res = [x * 2.5 for x in items]\n"
        "    total = 0\n"
        "    for v in res:\n"
        "        total += v\n"
        "    return res\n"
    )
    suggestions = agent.detect_vectorization_opportunities(source)
    assert len(suggestions) >= 2
    assert any("vectorized via NumPy/PyTorch" in s for s in suggestions)
    assert any("accumulator" in s for s in suggestions)

    speedup = agent.estimate_theoretical_speedup(["Nested loop detected", "vectorized"])
    assert speedup >= 20.0


def test_unit_integration_failure_grouping():
    runner = UnitIntegrationRunner()
    sample_failures = [
        "FAILED tests/test_a.py::test_fn - ValueError: invalid literal",
        "FAILED tests/test_b.py::test_fn - TypeError: unsupported operand",
        "FAILED tests/test_c.py::test_fn - ValueError: out of bounds",
    ]
    grouped = runner.group_failures_by_exception(sample_failures)
    assert len(grouped["ValueError"]) == 2
    assert len(grouped["TypeError"]) == 1


def test_visual_regression_html_report(tmp_path):
    runner = VisualRegressionRunner()
    baseline = tmp_path / "base.png"
    cand = tmp_path / "cand.png"

    from PIL import Image

    img1 = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
    img2 = Image.new("RGBA", (2, 2), (0, 255, 0, 255))
    img1.save(baseline)
    img2.save(cand)

    diff_path = tmp_path / "diff.png"
    result = runner.compare_images(baseline, cand, diff_output_path=diff_path)
    assert not result.passed

    report_html = tmp_path / "report.html"
    report_file = runner.generate_html_report(result, baseline, cand, report_html)
    assert report_file.exists()
    html_text = report_file.read_text(encoding="utf-8")
    assert "Visual Regression Summary" in html_text
    assert "FAILED" in html_text


def test_trace_extractor_filters_and_metrics():
    bus = RedisBus(use_mock=True)
    t1 = TraceRecord("tr1", "sub1", "task 1", "code 1", "PASSED", 15.0, timestamp=100.0)
    t2 = TraceRecord("tr2", "sub1", "task 1", "code 2", "FAILED", 1000.0, timestamp=150.0)
    t3 = TraceRecord("tr3", "sub2", "task 2", "code 3", "PASSED", 200.0, timestamp=300.0)
    bus.record_trace(t1)
    bus.record_trace(t2)
    bus.record_trace(t3)

    extractor = TraceExtractor(bus)
    sessions = extractor.extract_from_bus()
    assert len(sessions) == 2

    # Test time window filter
    windowed = extractor.filter_by_time_window(sessions, start_ts=50.0, end_ts=200.0)
    assert len(windowed) == 1
    assert windowed[0].subtask_id == "sub1"

    # Test energy filter
    energy_filtered = extractor.filter_by_energy_threshold(sessions, max_energy=50.0)
    assert len(energy_filtered) == 1
    assert energy_filtered[0].subtask_id == "sub1"

    # Test metrics
    metrics = extractor.compute_dataset_metrics(sessions)
    assert metrics["total_sessions"] == 2
    assert metrics["total_traces"] == 3
    assert metrics["passed_traces"] == 2
    assert metrics["pass_rate"] == 2 / 3
    assert metrics["dpo_ready_sessions"] == 1


def test_dpo_dataset_builder_split_and_chat():
    builder = DPODatasetBuilder()
    pairs = [
        DPOPreferencePair(f"prompt {i}", f"chosen {i}", f"rejected {i}", f"sub_{i}", -10.0)
        for i in range(10)
    ]

    train_set, val_set = builder.split_train_val(pairs, val_ratio=0.3, seed=42)
    assert len(train_set) == 7
    assert len(val_set) == 3

    chat_data = builder.format_for_chat_dpo(pairs[:2], system_prompt="Coding agent")
    assert len(chat_data) == 2
    assert chat_data[0]["prompt"][0]["role"] == "system"
    assert chat_data[0]["prompt"][1]["content"] == "prompt 0"
    assert chat_data[0]["chosen"][0]["content"] == "chosen 0"
    assert chat_data[0]["rejected"][0]["content"] == "rejected 0"
