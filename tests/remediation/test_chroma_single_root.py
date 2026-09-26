"""
Tests for P3-4: Unify the two Chroma roots that never shared an index.

Verifies that Harvester and ChromaRAG, when constructed against the same
MemoryConfig, resolve to the exact same on-disk ChromaDB persist directory,
and that a record written through the Harvester is retrievable through
ChromaRAG's client against the same store.
"""

from __future__ import annotations

from pathlib import Path

from anse.config import MemoryConfig
from anse.memory.chroma_rag import ChromaRAG
from anse.memory.harvester import Harvester, LoopTrace


def test_harvester_and_chroma_rag_share_persist_directory(tmp_path: Path) -> None:
    cfg = MemoryConfig(
        interactions_log=tmp_path / "interactions.jsonl",
        persist_directory=tmp_path / "chroma",
        collection_name="test_traces",
    )

    harvester = Harvester(config=cfg, enable_chroma=True)
    rag = ChromaRAG(config=cfg)

    assert Path(harvester.config.persist_directory) == rag.persist_dir
    assert rag.persist_dir == cfg.persist_directory

    # Directory exists on disk exactly once (both instances mkdir the same path).
    assert cfg.persist_directory.is_dir()
    assert len(list(tmp_path.glob("chroma"))) == 1


def test_harvester_write_visible_through_chroma_rag_read(tmp_path: Path) -> None:
    cfg = MemoryConfig(
        interactions_log=tmp_path / "interactions.jsonl",
        persist_directory=tmp_path / "chroma",
        collection_name="test_traces",
    )

    harvester = Harvester(config=cfg, enable_chroma=True, collection_name="phase1_traces")

    trace = LoopTrace(
        task="add two numbers",
        prompt="write add(a, b)",
        code="def add(a, b):\n    return a + b",
        raw_response="```python\ndef add(a, b):\n    return a + b\n```",
        energy=0.05,
        energy_category="low",
        converged=True,
        iteration=1,
        duration_ms=12.3,
        returncode=0,
        execution_stdout="",
        execution_stderr="",
        hidden_state=[0.1, 0.2, 0.3, 0.4],
    )
    harvester.record(trace)

    # ChromaRAG opens a fresh client against the same shared persist directory.
    rag = ChromaRAG(config=cfg)
    collection = rag.client.get_collection("phase1_traces")
    result = collection.get(ids=[trace.trace_id], include=["documents", "metadatas"])

    assert result["ids"] == [trace.trace_id]
    assert result["documents"][0] == trace.code
    assert result["metadatas"][0]["task"] == trace.task
