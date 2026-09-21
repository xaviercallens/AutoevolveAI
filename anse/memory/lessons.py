"""
Lesson memory: verified solutions that the agent loop reads back on similar tasks.

Only trajectories verified by hidden tests are stored, so self-graded (possibly
wrong) code never enters memory. Retrieval is lexical and deterministic.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

_STOPWORDS = frozenset(
    "a an and are as at be by for from if in into is it its must not of on or that the "
    "then this to when where which with write function functions return returns returned "
    "returning given python e g i example examples should".split()
)


@dataclass
class Lesson:
    task: str
    code: str
    failure: str = ""
    """First failure feedback that had to be overcome ('' if solved first try)."""
    iterations: int = 1
    timestamp: float = field(default_factory=time.time)


def _tokens(text: str) -> set[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    words = re.split(r"[^A-Za-z0-9]+", text.lower())
    return {w for w in words if len(w) > 1 and w not in _STOPWORDS}


def task_similarity(a: str, b: str) -> float:
    """Jaccard similarity over content words (identifiers are split on case and underscores)."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


class LessonMemory:
    """Append-only JSONL store of verified lessons with similarity retrieval."""

    def __init__(self, path: Path, min_similarity: float = 0.12, frozen: bool = False) -> None:
        self.path = Path(path)
        self.frozen = frozen
        self.min_similarity = min_similarity
        self._lessons: list[Lesson] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._lessons.append(Lesson(**json.loads(line)))

    def __len__(self) -> int:
        return len(self._lessons)

    def add(self, lesson: Lesson) -> bool:
        """Store *lesson* unless the memory is frozen or the identical task is already stored."""
        if self.frozen or any(existing.task == lesson.task for existing in self._lessons):
            return False
        self._lessons.append(lesson)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(lesson)) + "\n")
        return True

    def retrieve(self, task: str, k: int = 2) -> list[tuple[float, Lesson]]:
        """Return up to *k* (similarity, lesson) pairs above the threshold, best first."""
        scored = [(task_similarity(task, lesson.task), lesson) for lesson in self._lessons]
        scored = [pair for pair in scored if pair[0] >= self.min_similarity]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:k]


def format_lessons(lessons: list[tuple[float, Lesson]], max_code_chars: int = 1200) -> str:
    """Render retrieved lessons as a prompt block ('' when there are none)."""
    if not lessons:
        return ""
    parts = ["LESSONS FROM SIMILAR TASKS YOU SOLVED BEFORE (verified by tests):"]
    for i, (_, lesson) in enumerate(lessons, 1):
        parts.append(f"--- Lesson {i} ---\nTask: {lesson.task.strip()}")
        if lesson.failure:
            parts.append(f"Mistake made first: {lesson.failure.strip()[:400]}")
        parts.append(f"Verified solution:\n```python\n{lesson.code[:max_code_chars]}\n```")
    parts.append("--- End of lessons. Apply what is relevant; now solve the new task. ---\n")
    return "\n".join(parts)
