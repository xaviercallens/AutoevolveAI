"""Lesson memory: storage, retrieval and prompt rendering."""

from anse.memory.lessons import Lesson, LessonMemory, format_lessons, task_similarity

ROTATE = "Write a function `rotate_list(lst, k)` that rotates a list to the right by k positions."
ROTATE_STR = (
    "Write a function `rotate_string(s, k)` that rotates a string to the left by k positions."
)
IPV4 = "Write a function `validate_ipv4(s)` that checks a dotted IPv4 address."


def test_similarity_ranks_sibling_above_unrelated_and_is_symmetric():
    sibling = task_similarity(ROTATE, ROTATE_STR)
    unrelated = task_similarity(ROTATE, IPV4)
    assert sibling > unrelated
    assert sibling == task_similarity(ROTATE_STR, ROTATE)
    assert task_similarity(ROTATE, ROTATE) == 1.0
    assert task_similarity("", ROTATE) == 0.0


def test_retrieve_returns_only_lessons_above_threshold_best_first(tmp_path):
    memory = LessonMemory(tmp_path / "lessons.jsonl", min_similarity=0.2)
    memory.add(Lesson(task=IPV4, code="def validate_ipv4(s): return True"))
    memory.add(
        Lesson(task=ROTATE, code="def rotate_list(lst, k): return lst", failure="ZeroDivisionError")
    )
    hits = memory.retrieve(ROTATE_STR, k=2)
    assert len(hits) == 1
    assert hits[0][1].task == ROTATE
    assert hits[0][0] >= 0.2


def test_lessons_persist_and_duplicate_tasks_are_rejected(tmp_path):
    path = tmp_path / "lessons.jsonl"
    memory = LessonMemory(path)
    assert memory.add(Lesson(task=ROTATE, code="v1")) is True
    assert memory.add(Lesson(task=ROTATE, code="v2")) is False
    reloaded = LessonMemory(path)
    assert len(reloaded) == 1
    assert reloaded.retrieve(ROTATE)[0][1].code == "v1"


def test_format_lessons_includes_mistake_and_code_and_is_empty_without_hits():
    block = format_lessons(
        [
            (
                0.5,
                Lesson(
                    task=ROTATE, code="def rotate_list(): ...", failure="ZeroDivisionError on []"
                ),
            )
        ]
    )
    assert "ZeroDivisionError on []" in block
    assert "def rotate_list" in block
    assert format_lessons([]) == ""


def test_frozen_memory_serves_lessons_but_rejects_new_ones(tmp_path):
    path = tmp_path / "lessons.jsonl"
    LessonMemory(path).add(Lesson(task=ROTATE, code="v1"))
    frozen = LessonMemory(path, frozen=True)
    assert frozen.add(Lesson(task=IPV4, code="x")) is False
    assert len(frozen) == 1
    assert frozen.retrieve(ROTATE_STR)[0][1].code == "v1"
