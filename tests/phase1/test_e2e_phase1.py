"""
Phase 1 End-to-End Integration Tests
=====================================

These tests exercise the full ANSE Phase 1 pipeline:

  Prompt → Parser → Sandbox → Evaluator → Encoder → Harvester → AgentLoop

Unlike unit tests (which mock individual components), these tests verify:
  1. Real subprocess execution (no mocking of SandboxExecutor)
  2. Energy category correctness across the full pipeline
  3. JSONL persistence round-trip fidelity
  4. AgentLoop convergence and pain-signal propagation
  5. Invariants from the Lean 4 formal specification:
     - Energy ∈ [0, 100]                  (Basic.lean, EnergyFn.eval)
     - Inference minimises energy          (Basic.lean, exists_minimiser)
     - Hidden state shape [1, d_model]     (JEPA.lean, HiddenState d)
     - Dataset traces are complete         (Basic.lean, Dataset X Y n)

Each test docstring references the corresponding Lean 4 theorem or structure.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
import torch

from anse.config import MemoryConfig, ModelConfig, SandboxConfig
from anse.core.agent_loop import AgentLoop
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.memory.harvester import Harvester, LoopTrace
from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator
from anse.symbolic.parser import extract_code
from anse.symbolic.sandbox import SandboxExecutor, scan_dangerous_imports

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sandbox():
    """Real SandboxExecutor with a 5-second timeout — no mocks."""
    return SandboxExecutor(config=SandboxConfig(timeout_seconds=5.0))


@pytest.fixture
def evaluator():
    return EnergyEvaluator()


@pytest.fixture
def mock_extractor():
    return HiddenStateExtractor(config=ModelConfig(hidden_dim=4096), mock_mode=True)


@pytest.fixture
def harvester(tmp_path):
    cfg = MemoryConfig(
        interactions_log=tmp_path / "e2e_interactions.jsonl",
        persist_directory=tmp_path / "e2e_chroma",
    )
    return Harvester(config=cfg, enable_chroma=False)


@pytest.fixture
def agent_loop(mock_extractor, sandbox, evaluator, harvester):
    return AgentLoop(
        extractor=mock_extractor,
        sandbox=sandbox,
        evaluator=evaluator,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# E2E-1: Full pipeline — parse → execute → evaluate (correct code)
#
# Lean 4 ref: EnergyCategory.PERFECT → energy = 0.0
#             EnergyFn.eval : X → Y → ℝ  (lower = better)
# ──────────────────────────────────────────────────────────────────────────────


class TestE2EPipelineCorrectCode:
    """Verifies that correct code flows cleanly through the entire pipeline."""

    def test_parse_execute_evaluate_correct_fibonacci(self, sandbox, evaluator):
        """
        Lean 4: exists_minimiser guarantees ∃ y*, E(x, y*) ≤ E(x, y) ∀ y.
        Here we produce y* directly — it should achieve energy 0.0.
        """
        raw_llm_output = (
            "Here is the solution:\n"
            "```python\n"
            "def fibonacci(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    a, b = 0, 1\n"
            "    for _ in range(2, n + 1):\n"
            "        a, b = b, a + b\n"
            "    return b\n"
            "\n"
            "assert fibonacci(0) == 0\n"
            "assert fibonacci(1) == 1\n"
            "assert fibonacci(7) == 13\n"
            "print('OK')\n"
            "```\n"
        )

        # Step 1: Parse
        parsed = extract_code(raw_llm_output)
        assert parsed.extraction_method == "fenced_python"
        assert "def fibonacci" in parsed.code

        # Step 2: Execute (real subprocess)
        exec_result = sandbox.execute(parsed.code)
        assert exec_result.returncode == 0
        assert "OK" in exec_result.stdout
        assert exec_result.timed_out is False
        assert exec_result.tier_used == 1

        # Step 3: Evaluate
        energy = evaluator.evaluate(exec_result, code=parsed.code)
        assert energy.score == 0.0
        assert energy.category == EnergyCategory.PERFECT

    def test_parse_execute_evaluate_palindrome(self, sandbox, evaluator):
        """Full pipeline for palindrome check — verifies no false-positive energy."""
        raw = (
            "```python\n"
            "def is_palindrome(s):\n"
            "    s = ''.join(c.lower() for c in s if c.isalnum())\n"
            "    return s == s[::-1]\n"
            "\n"
            "assert is_palindrome('A man, a plan, a canal: Panama') is True\n"
            "assert is_palindrome('race a car') is False\n"
            "print('tests passed')\n"
            "```\n"
        )
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.returncode == 0
        assert energy.score == 0.0
        assert energy.category == EnergyCategory.PERFECT


# ──────────────────────────────────────────────────────────────────────────────
# E2E-2: Full pipeline — parse → execute → evaluate (buggy code)
#
# Lean 4 ref: _DEFAULT_ENERGY maps categories to scalar scores ∈ [0, 100]
# ──────────────────────────────────────────────────────────────────────────────


class TestE2EPipelineBuggyCode:
    """Verifies that buggy code produces the correct energy category."""

    def test_syntax_error_pipeline(self, sandbox, evaluator):
        """
        Lean 4: EnergyCategory.SYNTAX_ERROR → score = 100.0 (maximum penalty)
        """
        raw = "```python\ndef foo(:\n    pass\n```"
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.returncode != 0
        assert energy.score == 100.0
        assert energy.category == EnergyCategory.SYNTAX_ERROR

    def test_runtime_error_pipeline(self, sandbox, evaluator):
        """
        Lean 4: EnergyCategory.RUNTIME_ERROR → score = 60.0
        """
        raw = "```python\nx = 1 / 0\n```"
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.returncode != 0
        assert energy.score == 60.0
        assert energy.category == EnergyCategory.RUNTIME_ERROR

    def test_assertion_failure_pipeline(self, sandbox, evaluator):
        """
        Lean 4: EnergyCategory.TEST_FAILURE → score = 50.0
        """
        raw = "```python\nassert 2 + 2 == 5, 'math is wrong'\n```"
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.returncode != 0
        assert energy.score == 50.0
        assert energy.category == EnergyCategory.TEST_FAILURE

    def test_import_error_pipeline(self, sandbox, evaluator):
        """
        Lean 4: EnergyCategory.IMPORT_ERROR → score = 40.0
        """
        raw = "```python\nimport totally_fake_nonexistent_module_xyz\n```"
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.returncode != 0
        assert energy.score == 40.0
        assert energy.category == EnergyCategory.IMPORT_ERROR

    def test_timeout_pipeline(self):
        """
        Lean 4: EnergyCategory.TIMEOUT → score = 80.0
        Uses a short timeout to verify timed_out = True.
        """
        short_timeout_sandbox = SandboxExecutor(config=SandboxConfig(timeout_seconds=1.0))
        evaluator = EnergyEvaluator()

        raw = "```python\nimport time\ntime.sleep(10)\n```"
        parsed = extract_code(raw)
        exec_result = short_timeout_sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        assert exec_result.timed_out is True
        assert energy.score == 80.0
        assert energy.category == EnergyCategory.TIMEOUT

    def test_wrong_output_pipeline(self, sandbox, evaluator):
        """
        Lean 4: EnergyCategory.WRONG_OUTPUT → score = 30.0
        """
        raw = "```python\nprint('42')\n```"
        parsed = extract_code(raw)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code, expected_output="100")

        assert energy.score == 30.0
        assert energy.category == EnergyCategory.WRONG_OUTPUT


# ──────────────────────────────────────────────────────────────────────────────
# E2E-3: Energy invariants from Lean 4
#
# Lean 4 ref: EnergyFn.eval : X → Y → ℝ
#             "lower energy = more compatible" (Basic.lean, §1.1)
# ──────────────────────────────────────────────────────────────────────────────


class TestEnergyInvariants:
    """Verify energy scale invariants matching the Lean 4 specification."""

    def test_energy_monotonicity_correct_vs_syntax_error(self, sandbox, evaluator):
        """
        Lean 4: exists_minimiser guarantees correct code has strictly
        lower energy than broken code.
        E(y*) ≤ E(y_wrong) for all y_wrong ≠ y*.
        """
        # Good code
        good = "assert True\nprint('ok')"
        r_good = sandbox.execute(good)
        e_good = evaluator.evaluate(r_good, code=good)

        # Bad code
        bad = "def foo(:"
        r_bad = sandbox.execute(bad)
        e_bad = evaluator.evaluate(r_bad, code=bad)

        assert e_good.score < e_bad.score
        assert e_good.score == 0.0
        assert e_bad.score == 100.0

    def test_energy_bounded_0_100(self, sandbox, evaluator):
        """
        Lean 4: Energy score ∈ [0, 100] for all categories.
        Verify all default energy levels.
        """
        from anse.symbolic.evaluator import _DEFAULT_ENERGY

        for cat, score in _DEFAULT_ENERGY.items():
            assert 0.0 <= score <= 100.0, f"{cat} has out-of-range energy {score}"

    def test_energy_ordering_matches_severity(self):
        """
        Verify the energy scale is ordered by severity:
        PERFECT < NO_TESTS < WRONG_OUTPUT < IMPORT_ERROR < TEST_FAILURE
                < RUNTIME_ERROR < TIMEOUT < SYNTAX_ERROR
        """
        from anse.symbolic.evaluator import _DEFAULT_ENERGY

        expected_order = [
            EnergyCategory.PERFECT,
            EnergyCategory.NO_TESTS,
            EnergyCategory.WRONG_OUTPUT,
            EnergyCategory.IMPORT_ERROR,
            EnergyCategory.TEST_FAILURE,
            EnergyCategory.RUNTIME_ERROR,
            EnergyCategory.TIMEOUT,
            EnergyCategory.SYNTAX_ERROR,
        ]
        scores = [_DEFAULT_ENERGY[c] for c in expected_order]
        assert scores == sorted(scores), f"Energy scale is not monotonically ordered: {scores}"


# ──────────────────────────────────────────────────────────────────────────────
# E2E-4: Hidden state extraction invariants
#
# Lean 4 ref: JEPA.lean §1
#   abbrev HiddenState (d : ℕ) := EuclideanSpace ℝ (Fin d)
#   d = 4096 for Qwen-7B
# ──────────────────────────────────────────────────────────────────────────────


class TestHiddenStateInvariants:
    """Verify hidden state extraction matches the Lean 4 HiddenState(d) specification."""

    def test_hidden_state_shape_matches_spec(self, mock_extractor):
        """
        Lean 4: HiddenState(d) ∈ ℝ^d, d=4096
        """
        text, record = mock_extractor.extract("Write fibonacci")
        assert record.hidden_state.shape == (1, 4096)
        assert record.hidden_state.dtype == torch.float32

    def test_hidden_state_embedding_dimension(self, mock_extractor):
        """
        Lean 4: LatentCode(k) — the embedding vector must have d elements.
        """
        _, record = mock_extractor.extract("Test prompt")
        embedding = record.to_embedding()
        assert len(embedding) == 4096
        assert all(isinstance(v, float) for v in embedding)

    def test_hidden_state_content_dependent(self, mock_extractor):
        """
        Lean 4: EnergyFn.eval : X → Y → ℝ
        Different inputs must produce different hidden states (content-dependent).
        """
        _, r1 = mock_extractor.extract("Write fibonacci")
        _, r2 = mock_extractor.extract("Write palindrome checker")
        assert not torch.equal(r1.hidden_state, r2.hidden_state)

    def test_hidden_state_deterministic_same_input(self, mock_extractor):
        """
        Mock mode must be deterministic for reproducibility.
        """
        _, r1 = mock_extractor.extract("Same prompt")
        _, r2 = mock_extractor.extract("Same prompt")
        assert torch.equal(r1.hidden_state, r2.hidden_state)


# ──────────────────────────────────────────────────────────────────────────────
# E2E-5: Harvester / Dataset persistence round-trip
#
# Lean 4 ref: Basic.lean §5
#   structure Dataset (X Y : Type*) (n : ℕ) where
#     inputs  : Fin n → X
#     targets : Fin n → Y
# ──────────────────────────────────────────────────────────────────────────────


class TestDatasetPersistence:
    """Verify JSONL persistence matches the Lean 4 Dataset structure."""

    def test_full_trace_round_trip(self, harvester, sandbox, evaluator, mock_extractor):
        """
        E2E: generate → execute → evaluate → persist → reload
        Verify all fields survive the JSON round-trip.
        """
        text, hs_record = mock_extractor.extract("Write hello world")
        parsed = extract_code(text)
        exec_result = sandbox.execute(parsed.code)
        energy = evaluator.evaluate(exec_result, code=parsed.code)

        trace = LoopTrace(
            task="Hello World",
            prompt="Write hello world",
            code=parsed.code,
            raw_response=text,
            energy=energy.score,
            energy_category=energy.category.value,
            converged=energy.score <= 5.0,
            iteration=1,
            duration_ms=exec_result.duration_ms,
            returncode=exec_result.returncode,
            execution_stdout=exec_result.stdout,
            execution_stderr=exec_result.stderr,
            hidden_state=hs_record.to_embedding(),
        )

        harvester.record(trace)

        # Reload and validate
        loaded = harvester.load_traces(limit=1)
        assert len(loaded) == 1
        rt = loaded[0]
        assert rt.task == "Hello World"
        assert rt.energy == energy.score
        assert rt.converged == (energy.score <= 5.0)
        assert len(rt.hidden_state) == 4096  # Lean 4: HiddenState(4096)

    def test_multiple_traces_form_dataset(self, harvester, sandbox, evaluator, mock_extractor):
        """
        Lean 4: Dataset(X, Y, n) requires n labelled pairs.
        Verify we can persist and reload n_traces traces.
        """
        n_traces = 5
        for i in range(n_traces):
            text, hs = mock_extractor.extract(f"Task {i}")
            parsed = extract_code(text)
            exec_result = sandbox.execute(parsed.code)
            energy = evaluator.evaluate(exec_result, code=parsed.code)

            trace = LoopTrace(
                task=f"Task {i}",
                prompt=f"Task {i}",
                code=parsed.code,
                raw_response=text,
                energy=energy.score,
                energy_category=energy.category.value,
                converged=True,
                iteration=1,
                duration_ms=exec_result.duration_ms,
                returncode=exec_result.returncode,
                execution_stdout=exec_result.stdout,
                execution_stderr=exec_result.stderr,
                hidden_state=hs.to_embedding(),
            )
            harvester.record(trace)

        assert harvester.get_trace_count() == n_traces
        loaded = harvester.load_traces(limit=n_traces)
        assert len(loaded) == n_traces

        # Verify JSONL file is well-formed line-by-line
        with open(harvester.log_path) as f:
            lines = f.readlines()
        assert len(lines) == n_traces
        for line in lines:
            obj = json.loads(line.strip())
            assert "task" in obj
            assert "energy" in obj
            assert "hidden_state" in obj


# ──────────────────────────────────────────────────────────────────────────────
# E2E-6: AST safety scanner → tier escalation
#
# Lean 4 ref: sandbox.py implements the bounded oracle E(x, y)
# ──────────────────────────────────────────────────────────────────────────────


class TestSafetyEscalation:
    """Verify the AST scanner detects dangerous imports and triggers tier escalation."""

    def test_import_os_triggers_tier2(self, sandbox):
        code = "import os\nprint(os.getcwd())"
        result = sandbox.execute(code)
        assert "os" in result.dangerous_imports
        assert result.tier_used == 2  # escalated to Docker (or Docker fallback)

    def test_from_subprocess_triggers_tier2(self, sandbox):
        code = "from subprocess import run\nprint('test')"
        result = sandbox.execute(code)
        assert "subprocess" in result.dangerous_imports
        assert result.tier_used == 2

    def test_safe_code_stays_tier1(self, sandbox):
        code = "print(sum(range(100)))"
        result = sandbox.execute(code)
        assert result.dangerous_imports == []
        assert result.tier_used == 1

    def test_scan_multiple_dangerous_imports(self):
        code = "import os\nimport sys\nfrom shutil import copy2\nimport subprocess"
        found = scan_dangerous_imports(code, ["os", "sys", "shutil", "subprocess"])
        assert set(found) == {"os", "sys", "shutil", "subprocess"}


# ──────────────────────────────────────────────────────────────────────────────
# E2E-7: Agent loop convergence
#
# Lean 4 ref: exists_minimiser (Energy converges to minimum)
#             AgentLoop implements iterative energy descent
# ──────────────────────────────────────────────────────────────────────────────


class MockExtractorForE2E:
    """Mock extractor that returns specific code responses for E2E agent loop tests."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_idx = 0

    def extract(self, prompt: str, system_prompt: str | None = None):
        resp = self.responses[min(self.call_idx, len(self.responses) - 1)]
        self.call_idx += 1
        record = MagicMock(spec=HiddenStateRecord)
        record.to_embedding.return_value = [0.0] * 64
        record.model_id = "e2e-mock"
        return resp, record


class TestAgentLoopE2E:
    """End-to-end agent loop tests with real sandbox and evaluator."""

    def test_convergence_on_first_try(self, sandbox, evaluator, harvester):
        """
        Lean 4: If y* achieves E(y*) ≤ threshold, loop terminates after 1 iteration.
        """
        code = "```python\nassert 1 + 1 == 2\nprint('passed')\n```"
        extractor = MockExtractorForE2E([code])

        loop = AgentLoop(
            extractor=extractor,
            sandbox=sandbox,
            evaluator=evaluator,
            harvester=harvester,
            max_retries=3,
            convergence_threshold=5.0,
        )

        summary = loop.run("Add 1+1 and assert")
        assert summary.converged is True
        assert summary.iterations == 1
        assert summary.final_energy == 0.0

    def test_convergence_after_retry_with_pain_signal(self, sandbox, evaluator, harvester):
        """
        Lean 4: Pain signal injection — the agent loop injects error context
        into the prompt to guide the next attempt toward lower energy.
        """
        bad_code = "```python\nx = 1 / 0\n```"
        good_code = "```python\nassert 3 * 3 == 9\nprint('ok')\n```"
        extractor = MockExtractorForE2E([bad_code, good_code])

        loop = AgentLoop(
            extractor=extractor,
            sandbox=sandbox,
            evaluator=evaluator,
            harvester=harvester,
            max_retries=3,
            convergence_threshold=5.0,
        )

        summary = loop.run("Multiply 3*3")
        assert summary.converged is True
        assert summary.iterations == 2

        # Verify pain signal was injected
        assert "PAIN SIGNAL" in summary.traces[1].prompt
        assert "ZeroDivisionError" in summary.traces[1].prompt

        # Verify energy decreased monotonically
        assert summary.traces[0].energy > summary.traces[1].energy
        assert summary.traces[0].energy == 60.0  # RuntimeError
        assert summary.traces[1].energy == 0.0  # Perfect

    def test_exhaust_retries_on_persistent_failure(self, sandbox, evaluator, harvester):
        """
        Lean 4: If no y achieves E(y) ≤ threshold within max_retries,
        the loop terminates with converged=False.
        """
        failing_code = "```python\nassert False, 'always fails'\n```"
        extractor = MockExtractorForE2E([failing_code])

        loop = AgentLoop(
            extractor=extractor,
            sandbox=sandbox,
            evaluator=evaluator,
            harvester=harvester,
            max_retries=2,
            convergence_threshold=5.0,
        )

        summary = loop.run("Impossible task")
        assert summary.converged is False
        assert summary.iterations == 2
        assert summary.final_energy == 50.0  # TEST_FAILURE

    def test_all_traces_persisted_to_harvester(self, sandbox, evaluator, harvester):
        """
        Lean 4: Dataset(X, Y, n) — every iteration must produce a persisted trace.
        """
        bad_code = "```python\nraise ValueError('oops')\n```"
        good_code = "```python\nassert True\nprint('done')\n```"
        extractor = MockExtractorForE2E([bad_code, good_code])

        loop = AgentLoop(
            extractor=extractor,
            sandbox=sandbox,
            evaluator=evaluator,
            harvester=harvester,
            max_retries=3,
            convergence_threshold=5.0,
        )

        summary = loop.run("Multi-step task")
        assert harvester.get_trace_count() == summary.iterations

        loaded = harvester.load_traces()
        assert len(loaded) == summary.iterations
        for t in loaded:
            assert t.task == "Multi-step task"
            assert t.energy >= 0.0
            assert t.energy <= 100.0


# ──────────────────────────────────────────────────────────────────────────────
# E2E-8: Benchmark subset smoke test
#
# Lean 4 ref: Phase 1 DoD: convergence rate ≥ 70%
# ──────────────────────────────────────────────────────────────────────────────


class TestBenchmarkSmoke:
    """Verify the benchmark runner works end-to-end with mock LLM."""

    def test_mock_benchmark_converges(self, tmp_path):
        """
        The mock extractor produces working code with asserts.
        It should achieve 100% convergence on any task.
        """
        from main import run_benchmark

        extractor = HiddenStateExtractor(mock_mode=True)
        harvester = Harvester(enable_chroma=False)
        harvester.log_path = tmp_path / "benchmark.jsonl"

        loop = AgentLoop(
            extractor=extractor,
            harvester=harvester,
            max_retries=2,
        )

        tasks = [
            {"name": "T1", "task": "Return True"},
            {"name": "T2", "task": "Return True"},
            {"name": "T3", "task": "Return True"},
        ]

        summaries, rate = run_benchmark(loop, tasks, max_retries=1)
        assert len(summaries) == 3
        assert rate == 100.0  # Mock always generates correct code


"""
End-to-end test summary
========================
| Test class                 | Tests | Lean 4 ref                          |
|:---------------------------|:-----:|:------------------------------------|
| TestE2EPipelineCorrectCode | 2     | exists_minimiser, EnergyFn.eval     |
| TestE2EPipelineBuggyCode   | 6     | _DEFAULT_ENERGY categories          |
| TestEnergyInvariants       | 3     | EnergyFn bounded ∈ [0,100]          |
| TestHiddenStateInvariants  | 4     | HiddenState(d), LatentCode(k)       |
| TestDatasetPersistence     | 2     | Dataset(X, Y, n)                    |
| TestSafetyEscalation       | 4     | SandboxExecutor tier escalation     |
| TestAgentLoopE2E           | 4     | exists_minimiser, pain signal       |
| TestBenchmarkSmoke         | 1     | Phase 1 DoD: rate ≥ 70%             |
| **Total**                  | **26**|                                     |
"""
