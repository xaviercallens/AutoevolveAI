"""
Episodic trace harvester: records interaction traces to JSONL and vector database.

Formal Lean 4 Specification:
-----------------------------
See `formal/ANSE/Basic.lean`:
  structure Dataset (X Y : Type*) (n : ℕ) where
    inputs  : Fin n → X
    targets : Fin n → Y

The Harvester records every execution trajectory:
  (prompt, code, hidden_state, energy, execution_result)
forming the empirical dataset D used in Phase 2 for JEPA training and
EBM loss minimization:
  L_JEPA = ‖Ê(x, z) − E_actual(x, y)‖²
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from anse.config import MemoryConfig, get_config

logger = logging.getLogger(__name__)


# ─── Loop Trace Dataclass ────────────────────────────────────────────────────

@dataclass
class LoopTrace:
    """
    Complete trace of a single agent interaction attempt.

    Corresponds to a sample in Lean 4 `Dataset X Y n`.
    """
    task: str
    prompt: str
    code: str
    raw_response: str
    energy: float
    energy_category: str
    converged: bool
    iteration: int
    duration_ms: float
    returncode: int
    execution_stdout: str
    execution_stderr: str
    hidden_state: list[float] = field(default_factory=list)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to a JSON-serializable dictionary."""
        d = asdict(self)
        return d


# ─── Trace Harvester ─────────────────────────────────────────────────────────

class Harvester:
    """
    Harvests execution traces and persists them to disk:
      1. An append-only JSONL log (ground-truth dataset for JEPA training).
      2. ChromaDB vector database (collection 'phase1_traces') indexed by hidden state embeddings.
    """

    def __init__(
        self,
        config: MemoryConfig | None = None,
        enable_chroma: bool = True,
        collection_name: str = "phase1_traces",
    ) -> None:
        self.config = config or get_config().memory
        self.enable_chroma = enable_chroma
        self.collection_name = collection_name
        self._chroma_client = None
        self._chroma_collection = None

        # Ensure directory exists for JSONL logging
        self.log_path = Path(self.config.interactions_log)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        if self.enable_chroma:
            self._init_chroma()

    def _init_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            persist_dir = str(self.config.persist_directory)
            Path(persist_dir).mkdir(parents=True, exist_ok=True)

            self._chroma_client = chromadb.PersistentClient(path=persist_dir)
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "ChromaDB initialized at %s (collection: %s)",
                persist_dir,
                self.collection_name,
            )
        except Exception as e:
            logger.warning("Failed to initialize ChromaDB (%s). Running with JSONL only.", e)
            self._chroma_client = None
            self._chroma_collection = None

    def record(self, trace: LoopTrace) -> None:
        """
        Record a loop trace to both JSONL and ChromaDB.
        """
        # 1. Append to JSONL log
        self._append_jsonl(trace)

        # 2. Index in ChromaDB if enabled and available
        if self._chroma_collection is not None and trace.hidden_state:
            self._upsert_chroma(trace)

    def _append_jsonl(self, trace: LoopTrace) -> None:
        """Append trace as a single line JSON."""
        data = trace.to_dict()
        line = json.dumps(data) + "\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

    def _upsert_chroma(self, trace: LoopTrace) -> None:
        """Upsert trace vector and metadata into ChromaDB."""
        try:
            metadata = {
                "trace_id": trace.trace_id,
                "task": trace.task[:200],  # truncated for metadata limits
                "energy": float(trace.energy),
                "energy_category": str(trace.energy_category),
                "converged": bool(trace.converged),
                "iteration": int(trace.iteration),
                "returncode": int(trace.returncode),
                "timestamp": float(trace.timestamp),
            }

            self._chroma_collection.upsert(
                ids=[trace.trace_id],
                embeddings=[trace.hidden_state],
                documents=[trace.code],
                metadatas=[metadata],
            )
        except Exception as e:
            logger.warning("Failed to upsert trace %s to ChromaDB: %s", trace.trace_id, e)

    def query_similar(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve nearest interaction traces by hidden state similarity.
        """
        if self._chroma_collection is None:
            return []

        try:
            results = self._chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
            )
            hits = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    hits.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i] if results.get("documents") else "",
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0.0,
                    })
            return hits
        except Exception as e:
            logger.warning("ChromaDB query failed: %s", e)
            return []

    def get_trace_count(self) -> int:
        """Count the total number of lines in the JSONL interactions log."""
        if not self.log_path.exists():
            return 0
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for _ in f:
                count += 1
        return count

    def load_traces(self, limit: int = 100) -> list[LoopTrace]:
        """Load the most recent traces from the JSONL log."""
        if not self.log_path.exists():
            return []
        traces = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        traces.append(LoopTrace(**data))
                    except Exception as e:
                        logger.warning("Failed to parse trace line: %s", e)
        return traces
