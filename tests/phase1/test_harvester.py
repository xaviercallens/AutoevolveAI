"""Tests for Harvester and LoopTrace storage."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from anse.config import MemoryConfig
from anse.memory.harvester import Harvester, LoopTrace


@pytest.fixture
def temp_memory(tmp_path):
    cfg = MemoryConfig(
        interactions_log=tmp_path / "interactions.jsonl",
        persist_directory=tmp_path / "chroma",
        collection_name="test_traces",
    )
    return cfg


def test_harvester_record_jsonl(temp_memory):
    harvester = Harvester(config=temp_memory, enable_chroma=False)
    trace = LoopTrace(
        task="Test task",
        prompt="TASK: Test task",
        code="print('ok')",
        raw_response="```python\nprint('ok')\n```",
        energy=0.0,
        energy_category="perfect",
        converged=True,
        iteration=1,
        duration_ms=45.0,
        returncode=0,
        execution_stdout="ok\n",
        execution_stderr="",
        hidden_state=[0.1] * 4096,
    )

    harvester.record(trace)

    assert temp_memory.interactions_log.exists()
    assert harvester.get_trace_count() == 1

    traces = harvester.load_traces()
    assert len(traces) == 1
    loaded = traces[0]
    assert loaded.task == "Test task"
    assert loaded.energy == 0.0
    assert loaded.converged is True
    assert len(loaded.hidden_state) == 4096


def test_harvester_roundtrip_multiple(temp_memory):
    harvester = Harvester(config=temp_memory, enable_chroma=False)
    for i in range(5):
        trace = LoopTrace(
            task=f"Task {i}",
            prompt=f"Prompt {i}",
            code=f"print({i})",
            raw_response=f"print({i})",
            energy=float(i * 10),
            energy_category="test",
            converged=i == 0,
            iteration=1,
            duration_ms=10.0,
            returncode=0,
            execution_stdout=f"{i}\n",
            execution_stderr="",
        )
        harvester.record(trace)

    assert harvester.get_trace_count() == 5
    loaded = harvester.load_traces(limit=3)
    assert len(loaded) == 3
    assert loaded[-1].task == "Task 4"


def test_harvester_chromadb_upsert_and_query(temp_memory):
    harvester = Harvester(config=temp_memory, enable_chroma=True)
    if harvester._chroma_collection is None:
        pytest.skip("ChromaDB not available in current test environment")

    trace = LoopTrace(
        task="Vector similarity test",
        prompt="Prompt vector",
        code="def solve(): return 42",
        raw_response="def solve(): return 42",
        energy=0.0,
        energy_category="perfect",
        converged=True,
        iteration=1,
        duration_ms=15.0,
        returncode=0,
        execution_stdout="42\n",
        execution_stderr="",
        hidden_state=[0.05] * 128,  # test vector
    )
    harvester.record(trace)

    query_vec = [0.05] * 128
    hits = harvester.query_similar(query_vec, n_results=1)
    assert len(hits) == 1
    assert hits[0]["metadata"]["task"] == "Vector similarity test"
    assert hits[0]["metadata"]["converged"] is True


def test_harvester_empty_log(tmp_path):
    cfg = MemoryConfig(interactions_log=tmp_path / "nonexistent.jsonl")
    harvester = Harvester(config=cfg, enable_chroma=False)
    assert harvester.get_trace_count() == 0
    assert harvester.load_traces() == []


def test_harvester_disabled_chroma_query(temp_memory):
    harvester = Harvester(config=temp_memory, enable_chroma=False)
    results = harvester.query_similar([0.1] * 128)
    assert results == []


def test_harvester_chroma_init_exception(temp_memory, monkeypatch):
    import sys
    # Ensure chromadb is imported so we can mock it
    import chromadb
    monkeypatch.setattr(chromadb, "PersistentClient", MagicMock(side_effect=Exception("Mock Init Error")))
    
    # Should silently fallback to JSONL
    harvester = Harvester(config=temp_memory, enable_chroma=True)
    assert harvester._chroma_collection is None


def test_harvester_chroma_upsert_exception(temp_memory, monkeypatch):
    import chromadb
    
    mock_collection = MagicMock()
    mock_collection.upsert.side_effect = Exception("Mock Upsert Error")
    
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    monkeypatch.setattr(chromadb, "PersistentClient", lambda path: mock_client)
    
    harvester = Harvester(config=temp_memory, enable_chroma=True)
    
    trace = LoopTrace(
        task="Test task", prompt="P", code="C", raw_response="R",
        energy=0.0, energy_category="C", converged=True, iteration=1,
        duration_ms=10.0, returncode=0, execution_stdout="", execution_stderr="",
        hidden_state=[0.1] * 128
    )
    
    # Should not raise exception, but log it and continue writing to jsonl
    harvester.record(trace)
    assert harvester.get_trace_count() == 1


def test_harvester_chroma_query_exception(temp_memory, monkeypatch):
    import chromadb
    
    mock_collection = MagicMock()
    mock_collection.query.side_effect = Exception("Mock Query Error")
    
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    monkeypatch.setattr(chromadb, "PersistentClient", lambda path: mock_client)
    
    harvester = Harvester(config=temp_memory, enable_chroma=True)
    
    results = harvester.query_similar([0.1] * 128)
    # Should return empty list gracefully
    assert results == []


def test_harvester_json_load_exception(temp_memory):
    harvester = Harvester(config=temp_memory, enable_chroma=False)
    
    # Write a malformed json line
    temp_memory.interactions_log.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_memory.interactions_log, "w") as f:
        f.write("{malformed json\n")
        
    # Should skip the bad line
    traces = harvester.load_traces()
    assert traces == []
