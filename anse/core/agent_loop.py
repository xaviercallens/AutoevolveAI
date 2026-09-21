"""
Agentic execution loop with symbolic grounding and pain-signal injection.

Formal Lean 4 Specification:
-----------------------------
See `formal/ANSE/Basic.lean`:
  theorem exists_minimiser (E : EnergyFn X Y) (x : X) :
    ∃ y_star : Y, ∀ y : Y, E.eval x y_star ≤ E.eval x y

In Phase 1, System 1 acts autoregressively, and the agent loop performs
discrete energy minimisation via iterative trial-and-error:
  y_0 ~ P(y|x)
  e_0 = Energy(Exec(y_0))
  If e_0 > 0:
    y_{t+1} ~ P(y | x, y_t, pain_signal(e_t, stderr_t))
Until e_t ≤ threshold (convergence) or max_retries reached.
"""

from __future__ import annotations

import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any

from anse.config import ANSEConfig, get_config
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.memory.harvester import Harvester, LoopTrace
from anse.memory.lessons import Lesson, LessonMemory, format_lessons
from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator, EnergyResult
from anse.symbolic.hidden_tests import TestReport, attach_harness, parse_report, strip_report
from anse.symbolic.parser import NoCodeFoundError, extract_code
from anse.symbolic.sandbox import ExecutionResult, SandboxExecutor

# Phase 2: optional JEPA world model for energy prediction
try:
    from anse.jepa.world_model import JEPAWorldModel
except ImportError:
    JEPAWorldModel = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# ─── Loop Result Summary ─────────────────────────────────────────────────────


@dataclass
class LoopSummary:
    """Outcome of running the agent loop on a single task."""

    task: str
    converged: bool
    iterations: int
    final_energy: float
    final_category: str
    final_code: str
    traces: list[LoopTrace]
    total_duration_ms: float
    tests_passed: int | None = None
    tests_total: int | None = None
    lessons_used: int = 0


# ─── System & Pain Prompts ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Python programmer.
Write complete, self-contained, working Python code that solves the user's task.
Include basic validation or asserts at the bottom if appropriate.
Enclose your code inside a single ```python ... ``` markdown block.
Do not output extraneous explanation outside the code block."""

SYSTEM_PROMPT_HIDDEN_TESTS = """You are an expert Python programmer.
Write complete, self-contained, working Python code that solves the user's task.
Use exactly the function names and signatures the task specifies.
Your code will be verified by hidden tests, so do not include tests, prints or example usage.
Enclose your code inside a single ```python ... ``` markdown block.
Do not output extraneous explanation outside the code block."""

RETRY_SYSTEM_PROMPT_DIAGNOSE = """You are an expert Python programmer fixing your own failed code.
First write 1-3 sentences explaining exactly why the reported failure happens.
Then give the complete corrected code in a single ```python ... ``` markdown block.
The corrected code must differ from the failed code in its logic, not just its wording.
Use exactly the function names and signatures the task specifies. Do not include tests or prints."""

STAGNATION_NOTE = """
WARNING: the code you just returned behaves identically to an attempt that already failed.
Repeating it cannot work. Re-read the failing test, find the specific input it uses, and change the logic that handles that input.
"""

PAIN_PROMPT_TEMPLATE = """TASK: {task}

PAIN SIGNAL: Your previous attempt failed with Energy {energy:.1f} ({category}).
Your previous code:
```python
{code}
```
Execution feedback:
---
{test_feedback}Return code: {returncode}
Stderr:
{stderr}
Stdout:
{stdout}
---
Analyze the failure, correct the bug, and provide the complete fixed Python code in a ```python ... ``` block."""


# ─── Agent Loop ──────────────────────────────────────────────────────────────


class AgentLoop:
    """
    Orchestrates the generate -> execute -> evaluate -> record -> retry cycle.
    """

    def __init__(
        self,
        extractor: HiddenStateExtractor | None = None,
        sandbox: SandboxExecutor | None = None,
        evaluator: EnergyEvaluator | None = None,
        harvester: Harvester | None = None,
        config: ANSEConfig | None = None,
        max_retries: int = 3,
        convergence_threshold: float = 5.0,
        world_model: Any | None = None,
        lesson_memory: LessonMemory | None = None,
        adaptive_retry: bool = False,
    ) -> None:
        self.config = config or get_config()
        self.extractor = extractor or HiddenStateExtractor(config=self.config.model)
        self.sandbox = sandbox or SandboxExecutor(config=self.config.sandbox)
        self.evaluator = evaluator or EnergyEvaluator()
        self.harvester = harvester or Harvester(config=self.config.memory)
        self.max_retries = max_retries
        self.convergence_threshold = convergence_threshold
        self.world_model = world_model  # Phase 2: optional JEPA energy predictor
        self.lesson_memory = lesson_memory
        self.adaptive_retry = adaptive_retry

    def run(
        self,
        task: str,
        expected_output: str | None = None,
        max_retries: int | None = None,
        hidden_tests: list[str] | None = None,
    ) -> LoopSummary:
        """
        Execute the agentic trial-and-error loop on *task*.

        When *hidden_tests* are given, energy is graded from those tests (run
        independently in the sandbox) instead of the model's own asserts, and a
        verified solution is stored in the lesson memory, if one is attached.

        Returns:
            LoopSummary containing all iteration traces and final convergence status.
        """
        retries_limit = max_retries if max_retries is not None else self.max_retries
        traces: list[LoopTrace] = []
        start_time = time.time()

        lessons = self.lesson_memory.retrieve(task) if self.lesson_memory is not None else []
        lesson_block = format_lessons(lessons)
        system_prompt = SYSTEM_PROMPT_HIDDEN_TESTS if hidden_tests else SYSTEM_PROMPT

        prompt = f"{lesson_block}TASK:\n{task}"
        code = ""
        last_energy: EnergyResult | None = None
        report: TestReport | None = None
        first_failure = ""
        seen_codes: set[str] = set()
        stagnation = 0

        for iteration in range(1, retries_limit + 1):
            logger.info("Task '%s...' - Iteration %d/%d", task[:40], iteration, retries_limit)
            iter_start = time.time()

            # 1. Generate code and extract hidden state
            if self.adaptive_retry and iteration > 1:
                # Let the model reason before fixing, and sample hotter each time it repeats itself.
                raw_response, hs_record = self.extractor.extract(
                    prompt=prompt,
                    system_prompt=RETRY_SYSTEM_PROMPT_DIAGNOSE,
                    temperature=min(1.0, self.config.model.temperature + 0.4 * stagnation),
                )
            else:
                raw_response, hs_record = self.extractor.extract(
                    prompt=prompt,
                    system_prompt=system_prompt,
                )

            # 2. Parse code from response
            try:
                code = extract_code(raw_response).code
            except NoCodeFoundError as exc:
                code = ""
                report = None
                exec_res = ExecutionResult(
                    stdout="",
                    stderr=str(exc),
                    returncode=1,
                    timed_out=False,
                    duration_ms=0.0,
                    tier_used=1,
                )
            else:
                # 3. Execute in Sandbox
                exec_res, report = self._execute(code, hidden_tests)

            # 4. Evaluate Energy
            if hidden_tests:
                energy_res = self.evaluator.evaluate_hidden_tests(exec_res, report)
            else:
                energy_res = self.evaluator.evaluate(
                    result=exec_res,
                    code=code,
                    expected_output=expected_output,
                )
            last_energy = energy_res

            iter_duration_ms = (time.time() - iter_start) * 1000.0
            converged = self._is_converged(energy_res, report, hidden_tests)
            if not converged and not first_failure:
                first_failure = energy_res.pain_signal

            logger.info(
                "Iteration %d: Energy=%.1f (%s) - Converged=%s (took %.1fms)",
                iteration,
                energy_res.score,
                energy_res.category.value,
                converged,
                iter_duration_ms,
            )

            normalised = " ".join(code.split())
            if normalised and normalised in seen_codes:
                stagnation += 1
            seen_codes.add(normalised)

            # 5. Build and record LoopTrace
            trace = LoopTrace(
                task=task,
                prompt=prompt,
                code=code,
                raw_response=raw_response,
                energy=energy_res.score,
                energy_category=energy_res.category.value,
                converged=converged,
                iteration=iteration,
                duration_ms=iter_duration_ms,
                returncode=exec_res.returncode,
                execution_stdout=exec_res.stdout,
                execution_stderr=exec_res.stderr,
                hidden_state=hs_record.to_embedding(),
                metadata=self._build_trace_metadata(hs_record, exec_res, energy_res),
            )
            trace.metadata["lessons_used"] = len(lessons)
            trace.metadata["stagnation"] = stagnation
            if report is not None:
                trace.metadata["tests_passed"] = report.passed
                trace.metadata["tests_total"] = report.total
            traces.append(trace)
            self.harvester.record(trace)

            if converged:
                logger.info("Task converged on iteration %d!", iteration)
                break

            # 6. Inject Pain Signal for next iteration if retries remain
            if iteration < retries_limit:
                prompt = lesson_block + PAIN_PROMPT_TEMPLATE.format(
                    task=task,
                    test_feedback=f"{energy_res.pain_signal}\n" if hidden_tests else "",
                    code=code[-4000:] if code else "(no code block was found in your reply)",
                    energy=energy_res.score,
                    category=energy_res.category.value,
                    returncode=exec_res.returncode,
                    stderr=exec_res.stderr[-1000:] if exec_res.stderr else "(empty)",
                    stdout=exec_res.stdout[-1000:] if exec_res.stdout else "(empty)",
                )
                if self.adaptive_retry and stagnation:
                    prompt += STAGNATION_NOTE

        total_duration_ms = (time.time() - start_time) * 1000.0
        final_energy = last_energy.score if last_energy else 100.0
        final_category = (
            last_energy.category.value if last_energy else EnergyCategory.RUNTIME_ERROR.value
        )
        converged = bool(traces) and traces[-1].converged

        if converged and hidden_tests and self.lesson_memory is not None:
            self.lesson_memory.add(
                Lesson(task=task, code=code, failure=first_failure, iterations=len(traces))
            )

        return LoopSummary(
            task=task,
            converged=converged,
            iterations=len(traces),
            final_energy=final_energy,
            final_category=final_category,
            final_code=code,
            traces=traces,
            total_duration_ms=total_duration_ms,
            tests_passed=report.passed if report is not None else None,
            tests_total=report.total if report is not None else None,
            lessons_used=len(lessons),
        )

    def _execute(
        self, code: str, hidden_tests: list[str] | None
    ) -> tuple[ExecutionResult, TestReport | None]:
        if not hidden_tests:
            return self.sandbox.execute(code), None
        nonce = "ANSE-" + secrets.token_hex(8)
        exec_res = self.sandbox.execute(attach_harness(code, hidden_tests, nonce))
        report = parse_report(exec_res.stdout, nonce)
        exec_res.stdout = strip_report(exec_res.stdout, nonce)
        return exec_res, report

    def _is_converged(
        self,
        energy_res: EnergyResult,
        report: TestReport | None,
        hidden_tests: list[str] | None,
    ) -> bool:
        if hidden_tests:
            return report is not None and report.all_passed and energy_res.score == 0.0
        return energy_res.score <= self.convergence_threshold

    def _build_trace_metadata(
        self,
        hs_record: HiddenStateRecord,
        exec_res: ExecutionResult,
        energy_res: EnergyResult,
    ) -> dict[str, Any]:
        """Build metadata dict for a LoopTrace, including optional JEPA predictions."""
        metadata: dict[str, Any] = {
            "timed_out": exec_res.timed_out,
            "tier_used": exec_res.tier_used,
            "dangerous_imports": exec_res.dangerous_imports,
            "model_id": hs_record.model_id,
        }

        # Phase 2: JEPA energy prediction (if world model is available)
        if self.world_model is not None:
            try:
                import torch

                embedding = hs_record.to_embedding()
                h_tensor = torch.tensor(embedding, dtype=torch.float32)
                predicted_energy = self.world_model.predict_energy_scalar(h_tensor)
                actual_energy = energy_res.score
                surprise = abs(predicted_energy - actual_energy)

                metadata["jepa_predicted_energy"] = round(predicted_energy, 2)
                metadata["jepa_surprise"] = round(surprise, 2)

                logger.info(
                    "JEPA prediction: predicted=%.1f actual=%.1f surprise=%.1f",
                    predicted_energy,
                    actual_energy,
                    surprise,
                )
            except Exception as e:
                logger.warning("JEPA prediction failed: %s", e)
                metadata["jepa_error"] = str(e)

        return metadata
