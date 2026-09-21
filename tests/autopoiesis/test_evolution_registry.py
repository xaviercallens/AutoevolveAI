"""Component registry: versioning, atomic active pointer, lineage, rollback, corruption handling."""

import json
import os

import pytest

from anse.autopoiesis.registry import (
    ComponentRegistry,
    RegistryCorruptionError,
    RegistryError,
    code_sha256,
)

PARENT = "TAG = 'parent'\n\ndef double(x):\n    return x + x\n"
CHILD = "TAG = 'child'\n\ndef double(x):\n    return 2 * x\n"
GRANDCHILD = "TAG = 'grandchild'\n\ndef double(x):\n    return x << 1\n"
RECORD = {"parent_energy": 150.0, "child_energy": 40.0, "tests_total": 6, "child_tests_passed": 6, "reason": "gain"}


@pytest.fixture
def registry(tmp_path):
    reg = ComponentRegistry(tmp_path / "registry")
    reg.register("double", PARENT)
    return reg


def test_register_creates_v0001_pointer_and_lineage_and_is_idempotent(registry):
    assert registry.versions("double") == [1]
    assert registry.active("double").sha256 == code_sha256(PARENT)
    assert [e["event"] for e in registry.lineage("double")] == ["register"]
    assert registry.register("double", CHILD) == 1  # already registered: nothing is replaced
    assert registry.versions("double") == [1]
    assert registry.active_code("double") == PARENT


def test_promote_adds_a_version_moves_the_pointer_and_records_the_decision(registry):
    assert registry.promote("double", CHILD, RECORD) == 2
    assert registry.active_version("double") == 2
    assert registry.code("double", 1) == PARENT  # the parent file is never overwritten
    entry = registry.lineage("double")[-1]
    assert (entry["event"], entry["decision"]) == ("promote", "promoted")
    assert (entry["parent_version"], entry["child_version"]) == (1, 2)
    assert (entry["parent_energy"], entry["child_energy"]) == (150.0, 40.0)
    assert (entry["parent_sha256"], entry["child_sha256"]) == (code_sha256(PARENT), code_sha256(CHILD))
    assert entry["tests_total"] == entry["child_tests_passed"] == 6


def test_rejection_is_audited_without_storing_a_version_or_moving_the_pointer(registry):
    entry = registry.record_rejection("double", CHILD, {"reason": "child passes 4/6 hidden tests"})
    assert entry["decision"] == "rejected"
    assert entry["child_version"] is None
    assert entry["child_sha256"] == code_sha256(CHILD)
    assert registry.versions("double") == [1]
    assert registry.active_version("double") == 1
    assert registry.lineage("double")[-1]["reason"] == "child passes 4/6 hidden tests"


def test_rollback_restores_parent_pointer_and_logs_it_and_keeps_every_file(registry):
    registry.promote("double", CHILD, RECORD)
    assert registry.rollback("double", reason="regression in production") == 1
    assert registry.active("double").sha256 == code_sha256(PARENT)
    assert registry.versions("double") == [1, 2]
    last = registry.lineage("double")[-1]
    assert (last["event"], last["from_version"], last["to_version"]) == ("rollback", 2, 1)
    assert last["reason"] == "regression in production"
    with pytest.raises(RegistryError, match="no parent to roll back to"):
        registry.rollback("double")
    assert len(registry.lineage("double")) == 3  # the refused rollback wrote nothing


def test_rollback_walks_the_promotion_chain_one_generation_at_a_time(registry):
    registry.promote("double", CHILD, RECORD)
    registry.promote("double", GRANDCHILD, RECORD)
    assert registry.active_version("double") == 3
    assert registry.rollback("double") == 2
    assert registry.active_code("double") == CHILD
    assert registry.rollback("double") == 1
    assert registry.active_code("double") == PARENT
    # a new promotion after rollbacks gets a fresh number; v0002/v0003 are never reused
    assert registry.promote("double", GRANDCHILD, RECORD) == 4
    assert registry.lineage("double")[-1]["parent_version"] == 1


def test_load_active_executes_whichever_version_the_pointer_names(registry):
    assert registry.load_active("double").TAG == "parent"
    registry.promote("double", CHILD, RECORD)
    child = registry.load_active("double")
    assert (child.TAG, child.double(21)) == ("child", 42)
    registry.rollback("double")
    parent = registry.load_active("double")
    assert (parent.TAG, parent.double(21)) == ("parent", 42)
    assert parent.__file__.endswith("v0001.py")


def test_pointer_update_is_atomic_a_failed_replace_leaves_the_old_pointer_intact(registry, monkeypatch):
    before = registry.pointer_path("double").read_text()
    real_replace = os.replace

    def failing_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", failing_replace)
    with pytest.raises(OSError, match="disk full"):
        registry.promote("double", CHILD, RECORD)
    # old pointer untouched and still valid JSON; no temp litter left behind
    assert registry.pointer_path("double").read_text() == before
    assert json.loads(before)["version"] == 1
    assert [p.name for p in registry.pointer_path("double").parent.glob(".active-*")] == []

    # The lineage already recorded the promotion, so the stale pointer is healed forward.
    monkeypatch.setattr(os, "replace", real_replace)
    assert registry.active_version("double") == 2
    assert json.loads(registry.pointer_path("double").read_text())["version"] == 2
    assert registry.lineage("double")[-1]["event"] == "repair"


@pytest.mark.parametrize(
    "garbage",
    ["", "{not json", '{"version": "two"}', '{"version": 9, "sha256": "abc"}', '{"version": 1, "sha256": "wrong"}', "[1, 2]"],
    ids=["empty", "truncated", "wrong-type", "missing-version", "hash-mismatch", "not-an-object"],
)
def test_corrupted_pointer_is_rebuilt_from_lineage_and_the_repair_is_logged(registry, garbage):
    registry.promote("double", CHILD, RECORD)
    registry.pointer_path("double").write_text(garbage)
    assert registry.active_version("double") == 2
    assert json.loads(registry.pointer_path("double").read_text()) == {"version": 2, "sha256": code_sha256(CHILD)}
    repair = registry.lineage("double")[-1]
    assert (repair["event"], repair["restored_version"]) == ("repair", 2)


def test_deleted_pointer_is_rebuilt_and_a_valid_but_stale_pointer_is_not_trusted(registry):
    registry.promote("double", CHILD, RECORD)
    registry.rollback("double")
    registry.pointer_path("double").unlink()
    assert registry.active_version("double") == 1  # honours the rollback, not "highest version"
    # pointer naming a real version that the lineage says is no longer active
    registry.pointer_path("double").write_text(json.dumps({"version": 2, "sha256": code_sha256(CHILD)}))
    assert registry.active_version("double") == 1
    assert [e["event"] for e in registry.lineage("double")][-2:] == ["repair", "repair"]


def test_altered_version_file_is_refused_not_executed(registry):
    registry.promote("double", CHILD, RECORD)
    registry.version_path("double", 2).write_text(CHILD + "\nTAG = 'tampered'\n")
    with pytest.raises(RegistryCorruptionError, match="missing or altered"):
        registry.active("double")
    with pytest.raises(RegistryCorruptionError, match="missing or altered"):
        registry.load_active("double")


def test_torn_trailing_lineage_line_is_ignored_and_history_stays_append_only(registry):
    registry.promote("double", CHILD, RECORD)
    with open(registry.lineage_path("double"), "a", encoding="utf-8") as handle:
        handle.write('{"event": "promote", "child_ver')  # crash mid-write
    assert [e["event"] for e in registry.lineage("double")] == ["register", "promote"]
    assert registry.active_version("double") == 2
    size_before = registry.lineage_path("double").stat().st_size
    registry.record_rejection("double", GRANDCHILD, {"reason": "slower"})
    assert registry.lineage_path("double").stat().st_size > size_before
    assert registry.lineage("double")[-1]["reason"] == "slower"  # not glued onto the torn line


def test_unknown_and_unsafe_component_names_are_rejected(registry, tmp_path):
    with pytest.raises(RegistryError, match="Unknown component"):
        registry.active("never_registered")
    with pytest.raises(RegistryError, match="Invalid component name"):
        registry.register("../escape", PARENT)
    assert not (tmp_path / "escape").exists()
    assert registry.components() == ["double"]
