"""
Evolution Lab data layer: read-only access to results/<phaseN>_evolution/results.json.

Plain functions, no web framework import, so they are testable under the project venv.
web/server.py exposes them through thin GET routes. Nothing here launches a run,
executes a command or writes a file.

Every number returned comes verbatim from a results file written by a runner
(run_phaseN_evolution.py). This module only reshapes; it never computes, estimates
or fills in a metric. The only derived values are row counts, the file age and
the pairing of metrics that already exist (see find_comparisons).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

PHASES: tuple[int, ...] = (1, 2, 3)
DEFAULT_RESULTS_ROOT: Path = Path(__file__).resolve().parent.parent / "results"
DEFAULT_MAX_ROWS: int = 200
MAX_ROWS_LIMIT: int = 2000
MAX_CELL_CHARS: int = 4000
UC_KEYS: tuple[str, ...] = ("uc1", "uc2", "uc3", "uc4", "uc5")

Scalar = str | int | float | bool | None

WORKFLOW_STEPS: list[dict[str, str]] = [
    {
        "step": "Baseline",
        "detail": "Measure the existing behaviour on a real model before changing anything.",
    },
    {
        "step": "Evolve behind a parameter",
        "detail": "Add the improvement as an opt-in parameter so the old path stays intact and comparable.",
    },
    {
        "step": "Run 5 use cases",
        "detail": "Each use case asks one question and records raw per-item evidence rows, not just an average.",
    },
    {
        "step": "Gate",
        "detail": "Every goal is a boolean computed from the measured numbers. PASS or FAIL, nothing in between.",
    },
    {
        "step": "Promote or report failure",
        "detail": "A passing gate promotes the change. A failing gate is kept and shown as an honest result.",
    },
]

GOALS: dict[int, dict[str, Any]] = {
    1: {
        "name": "Phase 1: Symbolic sandbox and agent loop",
        "goal": (
            "Make the generate, execute, feel-pain, retry loop honest and make it learn. The agent used to grade "
            "its own work; now convergence is decided by hidden tests it never sees, the pain prompt carries the "
            "failing code back to the model, and lessons from past failures are recalled on new tasks. The use "
            "cases measure how often the old loop claimed success falsely, how much retries and memory really help, "
            "and whether the loop survives hostile model output."
        ),
        "runner": "run_phase1_evolution.py",
        "workflow": WORKFLOW_STEPS,
    },
    2: {
        "name": "Phase 2: JEPA world model and latent space",
        "goal": (
            "Make the latent world model earn its place. The JEPA predictor should forecast, from real model "
            "embeddings, how much symbolic pain a piece of code will cause before it is executed, without "
            "collapsing its representation. The use cases measure that prediction against sandbox ground truth "
            "on held-out data and check that using it changes what the agent does, compared with not using it."
        ),
        "runner": "run_phase2_evolution.py",
        "workflow": WORKFLOW_STEPS,
    },
    3: {
        "name": "Phase 3: Autopoietic self-modification",
        "goal": (
            "Make self-modification safe and measurable. When the agent rewrites one of its own components, the "
            "child must be verified equivalent to the parent, measured against it under noisy CPU conditions, and "
            "hot-swapped only when it is really better, with rollback when it is not. The use cases measure "
            "correctness of the swap decision, real speed and memory deltas, and rejection of broken or "
            "dishonest children."
        ),
        "runner": "run_phase3_evolution.py",
        "workflow": WORKFLOW_STEPS,
    },
}

# Phase 1 results written before titles were added to the checkpoint lack them.
DEFAULT_UC_META: dict[int, dict[str, tuple[str, str]]] = {
    1: {
        "uc1": (
            "Honest energy",
            "How often does the self-graded loop claim convergence that hidden tests refute?",
        ),
        "uc2": (
            "Learning from pain",
            "How much do pain-driven retries raise the hidden-test pass rate over the first attempt?",
        ),
        "uc3": (
            "Pain prompt ablation",
            "Does showing the model its own failing code fix more failures than the error alone?",
        ),
        "uc4": (
            "Memory transfer",
            "Do lessons stored from earlier failures improve results on the same tasks later?",
        ),
        "uc5": (
            "Robustness",
            "Does the loop survive hostile or malformed model output without crashing or lying?",
        ),
    },
}

# Token pairs that mark two metrics as a before/after style comparison.
PAIR_TOKENS: tuple[tuple[str, str], ...] = (
    ("1", "n"),
    ("off", "on"),
    ("without", "with"),
    ("before", "after"),
    ("baseline", "evolved"),
    ("legacy", "evolved"),
    ("legacy", "verified"),
    ("parent", "child"),
    ("old", "new"),
    ("cold", "warm"),
    ("claimed", "verified"),
    ("untrained", "trained"),
    ("random", "trained"),
    ("train", "heldout"),
    ("train", "test"),
)

_RESERVED_TOP: frozenset[str] = frozenset(
    {"phase", "model", "backend", "started", "finished", "gate", *UC_KEYS}
)


def results_path(phase: int, results_root: Path | None = None) -> Path:
    """Location of one phase's results file under the given (or default) results root."""
    root = Path(results_root) if results_root is not None else DEFAULT_RESULTS_ROOT
    return root / f"phase{phase}_evolution" / "results.json"


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _clip(text: str) -> str:
    if len(text) <= MAX_CELL_CHARS:
        return text
    return text[:MAX_CELL_CHARS] + f"... [{len(text) - MAX_CELL_CHARS} more chars]"


def _to_cell(value: Any) -> Scalar:
    """One table cell: scalars pass through, anything nested becomes compact JSON text."""
    if isinstance(value, str):
        return _clip(value)
    if _is_scalar(value):
        return value
    return _clip(json.dumps(value, default=str, ensure_ascii=False))


def _normalise_metric(value: Any) -> Scalar | dict[str, Scalar]:
    """Metrics are scalars or flat dicts of scalars; deeper structure is flattened to text."""
    if isinstance(value, dict):
        return {str(k): _to_cell(v) for k, v in value.items()}
    return _to_cell(value)


def _normalise_rows(raw: Any, max_rows: int) -> tuple[list[dict[str, Scalar]], int]:
    if not isinstance(raw, list):
        return [], 0
    rows: list[dict[str, Scalar]] = []
    for item in raw[:max_rows]:
        if isinstance(item, dict):
            rows.append({str(k): _to_cell(v) for k, v in item.items()})
        else:
            rows.append({"value": _to_cell(item)})
    return rows, len(raw)


def find_comparisons(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Pair up metrics that are obviously comparable, for side-by-side bars.

    Two sources: scalar keys that differ by one marker token (pass_at_1 / pass_at_n,
    latency_parent / latency_child) and flat-dict metrics whose names differ by one
    marker token (memory_off / memory_on), compared on every numeric key they share.
    Values are copied, never computed.
    """
    comparisons: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for key_a in metrics:
        tokens = key_a.split("_")
        for left, right in PAIR_TOKENS:
            for idx, token in enumerate(tokens):
                if token != left:
                    continue
                key_b = "_".join(tokens[:idx] + [right] + tokens[idx + 1 :])
                if key_b not in metrics or key_b == key_a:
                    continue
                val_a, val_b = metrics[key_a], metrics[key_b]
                if _is_number(val_a) and _is_number(val_b):
                    pairs = [(key_a, val_a, val_b)]
                elif isinstance(val_a, dict) and isinstance(val_b, dict):
                    pairs = [
                        (k, val_a[k], val_b[k])
                        for k in val_a
                        if _is_number(val_a[k]) and _is_number(val_b.get(k))
                    ]
                else:
                    pairs = []
                for label, num_a, num_b in pairs:
                    ident = (key_a, key_b, label)
                    if ident in seen:
                        continue
                    seen.add(ident)
                    comparisons.append(
                        {
                            "label": label if label != key_a else f"{key_a} vs {key_b}",
                            "bars": [
                                {"name": key_a, "value": num_a},
                                {"name": key_b, "value": num_b},
                            ],
                        }
                    )
    return comparisons


def _normalise_use_case(phase: int, uc_id: str, raw: Any, max_rows: int) -> dict[str, Any]:
    default_title, default_question = DEFAULT_UC_META.get(phase, {}).get(uc_id, (uc_id.upper(), ""))
    body: dict[str, Any] = raw if isinstance(raw, dict) else {}
    title = (
        body.get("title")
        if isinstance(body.get("title"), str) and body.get("title")
        else default_title
    )
    question = (
        body.get("question")
        if isinstance(body.get("question"), str) and body.get("question")
        else default_question
    )
    metrics = {
        str(k): _normalise_metric(v)
        for k, v in body.items()
        if k not in ("title", "question", "rows")
    }
    rows, total = _normalise_rows(body.get("rows"), max_rows)
    return {
        "id": uc_id,
        "title": title,
        "question": question,
        "metrics": metrics,
        "comparisons": find_comparisons(metrics),
        "rows": rows,
        "rows_total": total,
        "rows_truncated": total > len(rows),
    }


def _empty_phase(phase: int, status: str, error: str | None = None) -> dict[str, Any]:
    return {
        "phase": phase,
        "status": status,
        "error": error,
        "backend": None,
        "backend_kind": None,
        "started": None,
        "finished": None,
        "updated": None,
        "age_seconds": None,
        "params": {},
        "gate": [],
        "gate_passed": 0,
        "gate_total": 0,
        "use_cases": [],
        "use_cases_pending": list(UC_KEYS),
    }


def load_phase(
    phase: int, results_root: Path | None = None, max_rows: int = DEFAULT_MAX_ROWS
) -> dict[str, Any]:
    """
    Read and normalise one phase's results file.

    status is "missing" (no file), "invalid" (file exists but is not a JSON object, which
    also happens for a moment while a runner rewrites it), "running" (no "finished"
    timestamp yet) or "finished".
    """
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {PHASES}, got {phase!r}")
    max_rows = max(1, min(int(max_rows), MAX_ROWS_LIMIT))
    path = results_path(phase, results_root)
    try:
        text = path.read_text(encoding="utf-8")
        mtime = path.stat().st_mtime
    except (FileNotFoundError, NotADirectoryError):
        return _empty_phase(phase, "missing")
    except (OSError, UnicodeDecodeError) as exc:
        return _empty_phase(phase, "invalid", f"cannot read {path.name}: {exc}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return _empty_phase(phase, "invalid", f"{path.name} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        return _empty_phase(
            phase, "invalid", f"{path.name} holds a JSON {type(data).__name__}, expected an object"
        )

    out = _empty_phase(phase, "finished" if data.get("finished") else "running")
    for kind in ("model", "backend"):
        if data.get(kind):
            out["backend"] = _to_cell(data[kind])
            out["backend_kind"] = kind
            break
    out["started"] = _to_cell(data.get("started"))
    out["finished"] = _to_cell(data.get("finished")) if data.get("finished") else None
    out["updated"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
    out["age_seconds"] = max(0, int(time.time() - mtime))
    out["params"] = {str(k): _to_cell(v) for k, v in data.items() if k not in _RESERVED_TOP}

    gate_raw = data.get("gate")
    if isinstance(gate_raw, dict):
        out["gate"] = [
            {"goal": str(goal), "passed": value is True} for goal, value in gate_raw.items()
        ]
    out["gate_total"] = len(out["gate"])
    out["gate_passed"] = sum(1 for g in out["gate"] if g["passed"])

    out["use_cases"] = [
        _normalise_use_case(phase, key, data[key], max_rows)
        for key in UC_KEYS
        if isinstance(data.get(key), dict)
    ]
    done = {uc["id"] for uc in out["use_cases"]}
    out["use_cases_pending"] = [key for key in UC_KEYS if key not in done]
    return out


def load_all(results_root: Path | None = None, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """All phases plus their goals, keyed by phase number as a string (JSON object keys)."""
    phases = {str(p): load_phase(p, results_root, max_rows) for p in PHASES}
    return {
        "phases": phases,
        "goals": {str(p): GOALS[p] for p in PHASES},
        "any_running": any(ph["status"] in ("running", "invalid") for ph in phases.values()),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
