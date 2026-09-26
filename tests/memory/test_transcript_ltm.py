"""Tests for Claude Code transcript import into long-term memory.

Two properties matter most and are tested hardest:

  1. **Scrubbing is a gate.** Credentials, e-mail addresses and absolute home
     paths must never reach storage. `docs/ROADMAP_V1_V2_COMPANION.md` §4.5
     requires this as a hard gate with its own test suite; this is that suite.
  2. **Records are retrieval-only.** Provider terms restrict using assistant
     output as training targets, so every stored record must carry
     trainable=False. A future change that flips this should break a test, not
     slip through.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from anse.memory.transcript_ltm import (
    ScrubReport,
    TranscriptTurn,
    _text_from_content,
    iter_transcripts,
    parse_transcript,
    scrub,
)


def test_scrub_removes_anthropic_key() -> None:
    report = ScrubReport()
    cleaned = scrub("use sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAA now", report)

    assert "sk-ant" not in cleaned
    assert "[REDACTED:anthropic_key]" in cleaned
    assert report.replacements["anthropic_key"] == 1


def test_scrub_removes_multiple_secret_classes() -> None:
    report = ScrubReport()
    text = (
        "token ghp_AAAAAAAAAAAAAAAAAAAAAAAAA "
        "aws AKIAIOSFODNN7EXAMPLE "
        "mail someone@example.com "
        "path /home/someuser/project"
    )
    cleaned = scrub(text, report)

    assert "ghp_" not in cleaned
    assert "AKIAIOSFODNN7EXAMPLE" not in cleaned
    assert "someone@example.com" not in cleaned
    assert "/home/someuser" not in cleaned
    assert report.total >= 4


def test_scrub_reports_zero_on_clean_text() -> None:
    """A clean corpus must report zero, so an implausibly clean run is visible."""
    report = ScrubReport()
    cleaned = scrub("a perfectly ordinary sentence about energy descent", report)

    assert cleaned == "a perfectly ordinary sentence about energy descent"
    assert report.total == 0


def test_scrub_redacts_private_key_block() -> None:
    report = ScrubReport()
    cleaned = scrub("-----BEGIN RSA PRIVATE KEY-----\nMIIEow==\n", report)

    assert "BEGIN RSA PRIVATE KEY" not in cleaned
    assert report.replacements["private_key_block"] == 1


def test_turn_defaults_to_not_trainable() -> None:
    """The ToS constraint, enforced by the type's default."""
    turn = TranscriptTurn(
        session_id="s1", project_slug="proj", turn_index=0, role="assistant", text="hi"
    )

    assert turn.trainable is False
    assert turn.usage == "retrieval_only"


def test_turn_record_id_is_stable_and_unique() -> None:
    a = TranscriptTurn(session_id="s1", project_slug="p", turn_index=3, role="user", text="x")
    b = TranscriptTurn(session_id="s1", project_slug="p", turn_index=4, role="user", text="y")

    assert a.record_id == "s1:3"
    assert a.record_id != b.record_id


def test_text_from_content_handles_plain_string() -> None:
    text, tools = _text_from_content("just text")

    assert text == "just text"
    assert tools == []


def test_text_from_content_extracts_tool_names() -> None:
    text, tools = _text_from_content(
        [
            {"type": "text", "text": "running a check"},
            {"type": "tool_use", "name": "Bash", "input": {"command": "pytest"}},
            {"type": "tool_result", "content": "3 passed"},
        ]
    )

    assert "running a check" in text
    assert "Bash" in tools
    assert "[tool_result] 3 passed" in text


def test_parse_transcript_scrubs_and_counts(tmp_path: Path) -> None:
    """A synthetic transcript parses into scrubbed turns."""
    session = tmp_path / "proj" / "session-abc.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text(
        "\n".join(
            [
                json.dumps({"message": {"role": "user", "content": "my key is sk-ant-api03-BBBBBBBBBBBBBBBBBBBBBBBB"}}),
                json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": "noted"}]}}),
                json.dumps({"message": {"role": "system", "content": "ignored role"}}),
            ]
        )
        + "\n"
    )

    report = ScrubReport()
    turns = parse_transcript(session, report)

    assert len(turns) == 2, "only user and assistant turns are imported"
    assert all(t.session_id == "session-abc" for t in turns)
    assert "sk-ant" not in turns[0].text
    assert report.replacements["anthropic_key"] == 1
    assert all(t.trainable is False for t in turns)


def test_parse_transcript_survives_malformed_line(tmp_path: Path) -> None:
    """Transcripts are append-only logs; a truncated final line is normal."""
    session = tmp_path / "proj" / "s.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text(
        json.dumps({"message": {"role": "user", "content": "good line"}})
        + "\n{ this is not valid json\n"
    )

    turns = parse_transcript(session)

    assert len(turns) == 1
    assert turns[0].text == "good line"


def test_parse_transcript_skips_empty_content(tmp_path: Path) -> None:
    session = tmp_path / "proj" / "s.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text(
        "\n".join(
            [
                json.dumps({"message": {"role": "user", "content": ""}}),
                json.dumps({"message": {"role": "user", "content": "real content"}}),
            ]
        )
        + "\n"
    )

    turns = parse_transcript(session)

    assert len(turns) == 1
    assert turns[0].text == "real content"


def test_iter_transcripts_finds_jsonl(tmp_path: Path) -> None:
    (tmp_path / "projA").mkdir()
    (tmp_path / "projA" / "one.jsonl").write_text("{}\n")
    (tmp_path / "projA" / "notes.txt").write_text("ignore me")

    found = list(iter_transcripts(tmp_path))

    assert len(found) == 1
    assert found[0].name == "one.jsonl"


def test_iter_transcripts_on_missing_root_is_empty() -> None:
    """A box with no Claude Code history must not raise."""
    assert list(iter_transcripts(Path("/nonexistent/claude/projects"))) == []
