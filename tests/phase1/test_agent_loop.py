"""Tests for AgentLoop and pain-signal injection."""

from unittest.mock import MagicMock

from anse.core.agent_loop import AgentLoop
from anse.core.encoder import HiddenStateRecord
from anse.memory.harvester import Harvester


class MockExtractorSequential:
    """Mock extractor that returns different responses per attempt."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def extract(self, prompt: str, system_prompt: str | None = None):
        resp = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        record = MagicMock(spec=HiddenStateRecord)
        record.to_embedding.return_value = [0.0] * 64
        record.model_id = "mock-seq"
        return resp, record


def test_agent_loop_immediate_convergence(tmp_path):
    # Response produces energy 0 (asserts pass)
    code = "```python\nassert 1 + 1 == 2\n```"
    extractor = MockExtractorSequential([code])
    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Simple task")
    assert summary.converged is True
    assert summary.iterations == 1
    assert summary.final_energy == 0.0
    assert len(summary.traces) == 1


def test_agent_loop_retry_and_converge(tmp_path):
    # First response fails with ZeroDivisionError, second succeeds
    code_bad = "```python\nx = 1 / 0\n```"
    code_good = "```python\nassert 2 * 2 == 4\n```"
    extractor = MockExtractorSequential([code_bad, code_good])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Task that needs retry")
    assert summary.converged is True
    assert summary.iterations == 2
    assert summary.traces[0].energy == 60.0  # ZeroDivisionError
    assert summary.traces[1].energy == 0.0  # Converged
    assert "PAIN SIGNAL" in summary.traces[1].prompt
    assert "ZeroDivisionError" in summary.traces[1].prompt


def test_agent_loop_exhaust_retries(tmp_path):
    # Code always fails
    code_fail = "```python\nassert False, 'Never works'\n```"
    extractor = MockExtractorSequential([code_fail])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Failing task")
    assert summary.converged is False
    assert summary.iterations == 3
    assert summary.final_energy == 50.0  # Test failure
    assert harvester.get_trace_count() == 3


def test_agent_loop_custom_convergence_threshold(tmp_path):
    # Code has no asserts (energy = 5.0)
    code_no_tests = "```python\nprint('Done without asserts')\n```"
    extractor = MockExtractorSequential([code_no_tests])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    # Strict threshold 0.0 -> does NOT converge on 5.0
    loop_strict = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=2,
        convergence_threshold=0.0,
    )
    s_strict = loop_strict.run("No asserts task")
    assert s_strict.converged is False
    assert s_strict.final_energy == 5.0

    # Relaxed threshold 10.0 -> CONVERGES on 5.0
    loop_relaxed = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=2,
        convergence_threshold=10.0,
    )
    s_relaxed = loop_relaxed.run("No asserts task")
    assert s_relaxed.converged is True
    assert s_relaxed.final_energy == 5.0


def test_agent_loop_survives_reply_without_code_and_does_not_converge(tmp_path):
    extractor = MockExtractorSequential(["Sorry, I cannot help with that."])
    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"
    loop = AgentLoop(extractor=extractor, harvester=harvester, max_retries=2)

    summary = loop.run("Any task")
    assert summary.converged is False
    assert summary.iterations == 2
    assert "No Python code block" in summary.traces[0].execution_stderr


def test_agent_loop_pain_prompt_contains_previous_failing_code(tmp_path):
    prompts: list[str] = []

    class Recording(MockExtractorSequential):
        def extract(self, prompt, system_prompt=None):
            prompts.append(prompt)
            return super().extract(prompt, system_prompt)

    bad = "```python\nvalue = 1 / 0\n```"
    good = "```python\nassert 2 * 2 == 4\n```"
    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"
    loop = AgentLoop(extractor=Recording([bad, good]), harvester=harvester, max_retries=3)

    summary = loop.run("Divide things")
    assert summary.converged is True
    assert "value = 1 / 0" in prompts[1]
    assert "ZeroDivisionError" in prompts[1]


ROTATE_TASK = "Write a function `rotate_list(lst, k)` that rotates a list to the right by k positions."
ROTATE_TESTS = ["assert rotate_list([1, 2, 3], 1) == [3, 1, 2]", "assert rotate_list([], 4) == []"]
ROTATE_BAD = "```python\ndef rotate_list(lst, k):\n    k %= len(lst)\n    return lst[-k:] + lst[:-k]\n```"
ROTATE_GOOD = "```python\ndef rotate_list(lst, k):\n    if not lst:\n        return []\n    k %= len(lst)\n    return lst[-k:] + lst[:-k] if k else list(lst)\n```"


def _loop(tmp_path, replies, memory=None):
    from anse.memory.lessons import LessonMemory  # noqa: F401

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"
    return AgentLoop(extractor=MockExtractorSequential(replies), harvester=harvester, max_retries=3, lesson_memory=memory)


def test_hidden_tests_grade_partial_failure_then_verified_fix_is_stored_as_lesson(tmp_path):
    from anse.memory.lessons import LessonMemory

    memory = LessonMemory(tmp_path / "lessons.jsonl")
    summary = _loop(tmp_path, [ROTATE_BAD, ROTATE_GOOD], memory).run(ROTATE_TASK, hidden_tests=ROTATE_TESTS)

    assert [t.energy for t in summary.traces] == [25.0, 0.0]
    assert summary.converged is True and (summary.tests_passed, summary.tests_total) == (2, 2)
    assert "ZeroDivisionError" in summary.traces[1].prompt
    stored = memory.retrieve(ROTATE_TASK)[0][1]
    assert stored.iterations == 2 and "ZeroDivisionError" in stored.failure


def test_self_asserting_cheat_never_converges_and_never_enters_memory(tmp_path):
    from anse.memory.lessons import LessonMemory

    memory = LessonMemory(tmp_path / "lessons.jsonl")
    cheat = "```python\ndef rotate_list(lst, k):\n    return lst\n\nassert True\n```"
    summary = _loop(tmp_path, [cheat], memory).run(ROTATE_TASK, hidden_tests=ROTATE_TESTS)

    assert summary.converged is False
    assert summary.final_energy == 25.0
    assert len(memory) == 0


def test_retrieved_lesson_is_injected_into_first_prompt_of_a_sibling_task(tmp_path):
    from anse.memory.lessons import Lesson, LessonMemory

    memory = LessonMemory(tmp_path / "lessons.jsonl", frozen=True)
    LessonMemory(tmp_path / "lessons.jsonl").add(Lesson(task=ROTATE_TASK, code="def rotate_list(lst, k): ...", failure="ZeroDivisionError on []"))
    memory = LessonMemory(tmp_path / "lessons.jsonl", frozen=True)
    sibling = "Write a function `rotate_string(s, k)` that rotates a string to the left by k positions."
    good = "```python\ndef rotate_string(s, k):\n    return s[k % len(s):] + s[:k % len(s)] if s else ''\n```"

    summary = _loop(tmp_path, [good], memory).run(sibling, hidden_tests=["assert rotate_string('abc', 1) == 'bca'", "assert rotate_string('', 2) == ''"])

    assert summary.lessons_used == 1 and summary.converged is True
    assert "ZeroDivisionError on []" in summary.traces[0].prompt
    assert len(memory) == 1


def test_adaptive_retry_detects_repeated_code_escalates_temperature_and_warns(tmp_path):
    calls: list[dict] = []

    class Recording(MockExtractorSequential):
        def extract(self, prompt, system_prompt=None, temperature=None):
            calls.append({"prompt": prompt, "system": system_prompt, "temperature": temperature})
            return super().extract(prompt, system_prompt)

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"
    reworded = ROTATE_BAD.replace("    k %= len(lst)", "    k  %=  len(lst)")
    loop = AgentLoop(extractor=Recording([ROTATE_BAD, reworded, ROTATE_GOOD]), harvester=harvester,
                     max_retries=3, adaptive_retry=True)

    summary = loop.run(ROTATE_TASK, hidden_tests=ROTATE_TESTS)

    assert summary.converged is True and summary.iterations == 3
    assert calls[0]["temperature"] is None and "fixing your own failed code" not in calls[0]["system"]
    assert calls[1]["temperature"] == 0.2 and "fixing your own failed code" in calls[1]["system"]
    assert calls[2]["temperature"] == 0.6000000000000001 or abs(calls[2]["temperature"] - 0.6) < 1e-9
    assert "behaves identically" in calls[2]["prompt"] and "behaves identically" not in calls[1]["prompt"]


def test_plain_retry_never_passes_temperature_or_stagnation_note(tmp_path):
    prompts: list[str] = []

    class Recording(MockExtractorSequential):
        def extract(self, prompt, system_prompt=None):
            prompts.append(prompt)
            return super().extract(prompt, system_prompt)

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"
    loop = AgentLoop(extractor=Recording([ROTATE_BAD, ROTATE_BAD, ROTATE_BAD]), harvester=harvester, max_retries=3)

    summary = loop.run(ROTATE_TASK, hidden_tests=ROTATE_TESTS)
    assert summary.converged is False and summary.iterations == 3
    assert all("behaves identically" not in p for p in prompts)
    assert summary.traces[-1].metadata["stagnation"] == 2
