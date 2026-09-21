"""
Redis Bus: High-throughput event streaming, JSON state persistence, and Vector Store.
Supports Redis Streams (subtasks, attestation receipts), Hash/JSON documents (traces),
and Vector Embeddings for similarity lookup across lessons and failing patterns.
Includes an in-memory fallback engine for isolated testing without an external Redis daemon.
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TraceRecord:
    """Execution trace record for DPO / RL pipeline."""

    trace_id: str
    subtask_id: str
    prompt: str
    completion: str
    verdict: str  # "PASSED" | "FAILED"
    energy: float
    reasons: list[str] = field(default_factory=list)
    human_patch: str | None = None
    embedding: list[float] | None = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraceRecord:
        return cls(**data)


class InMemoryBusBackend:
    """Mock in-memory Redis implementation for CI and standalone local development."""

    def __init__(self) -> None:
        self.streams: dict[str, list[tuple[str, dict[str, str]]]] = {}
        self.hashes: dict[str, dict[str, str]] = {}
        self.keys: dict[str, str] = {}
        self.vectors: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def xadd(self, stream: str, payload: dict[str, Any]) -> str:
        if stream not in self.streams:
            self.streams[stream] = []
        msg_id = f"{int(time.time() * 1000)}-{len(self.streams[stream])}"
        # Stringify payload fields
        str_payload = {k: str(v) if not isinstance(v, str) else v for k, v in payload.items()}
        self.streams[stream].append((msg_id, str_payload))
        return msg_id

    def xread(
        self, stream: str, last_id: str = "0", count: int = 10
    ) -> list[tuple[str, dict[str, str]]]:
        if stream not in self.streams:
            return []
        items = self.streams[stream]
        # Return items after last_id
        filtered = []
        for mid, data in items:
            if mid > last_id:
                filtered.append((mid, data))
                if len(filtered) >= count:
                    break
        return filtered

    def hset(self, key: str, mapping: dict[str, Any]) -> int:
        if key not in self.hashes:
            self.hashes[key] = {}
        for k, v in mapping.items():
            self.hashes[key][k] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
        return len(mapping)

    def hgetall(self, key: str) -> dict[str, str]:
        return dict(self.hashes.get(key, {}))

    def set(self, key: str, value: str) -> bool:
        self.keys[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self.keys.get(key)


class RedisBus:
    """
    Unified communication and storage hub.
    Connects to live Redis instance when available, or seamlessly falls back to InMemoryBusBackend.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        db: int = 0,
        use_mock: bool = False,
    ) -> None:
        self.host = str(host or os.getenv("REDIS_HOST") or "localhost")
        self.port = int(port or os.getenv("REDIS_PORT") or 6379)
        self.db = db
        self.is_mock = use_mock
        self._client: Any = None
        self._vectors: dict[str, tuple[list[float], dict[str, Any]]] = {}

        if self.is_mock:
            self._client = InMemoryBusBackend()
        else:
            self._connect()

    def _connect(self) -> None:
        try:
            import redis

            client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=1.0,
            )
            client.ping()
            self._client = client
            self.is_mock = False
        except Exception:
            # Fallback to in-memory backend
            self._client = InMemoryBusBackend()
            self.is_mock = True

    # ─── Event Streams ─────────────────────────────────────────────────────────

    def publish_event(self, stream: str, payload: dict[str, Any]) -> str:
        """Publish an event to a Redis Stream."""
        if self.is_mock:
            return self._client.xadd(stream, payload)

        stringified = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in payload.items()
        }
        return self._client.xadd(stream, stringified)

    def consume_events(
        self, stream: str, last_id: str = "0", count: int = 10
    ) -> list[tuple[str, dict[str, Any]]]:
        """Read pending events from a Redis Stream."""
        if self.is_mock:
            return self._client.xread(stream, last_id=last_id, count=count)

        try:
            res = self._client.xread({stream: last_id}, count=count)
            if not res:
                return []
            events = []
            for _sname, msg_list in res:
                for mid, fields in msg_list:
                    parsed_fields = {}
                    for k, v in fields.items():
                        try:
                            parsed_fields[k] = json.loads(v)
                        except (json.JSONDecodeError, TypeError):
                            parsed_fields[k] = v
                    events.append((mid, parsed_fields))
            return events
        except Exception:
            return []

    # ─── JSON & Trace Document Storage ────────────────────────────────────────

    def record_trace(self, trace: TraceRecord) -> str:
        """Persist a complete execution trace."""
        trace_data = trace.to_dict()
        key = f"antigravity:trace:{trace.trace_id}"

        if self.is_mock:
            self._client.set(key, json.dumps(trace_data))
        else:
            self._client.set(key, json.dumps(trace_data))
            # Also register to subtask index
            self._client.rpush(f"antigravity:subtask:{trace.subtask_id}:traces", trace.trace_id)

        if trace.embedding is not None:
            self.store_vector(trace.trace_id, trace.embedding, metadata=trace_data)

        return trace.trace_id

    def get_trace(self, trace_id: str) -> TraceRecord | None:
        """Fetch an execution trace by ID."""
        key = f"antigravity:trace:{trace_id}"
        raw = self._client.get(key)
        if not raw:
            return None
        data = json.loads(raw)
        return TraceRecord.from_dict(data)

    def list_all_traces(self) -> list[TraceRecord]:
        """Extract all traces from storage."""
        traces: list[TraceRecord] = []
        if self.is_mock:
            for k, val in self._client.keys.items():
                if k.startswith("antigravity:trace:"):
                    traces.append(TraceRecord.from_dict(json.loads(val)))
            return traces

        keys = self._client.keys("antigravity:trace:*")
        for k in keys:
            raw = self._client.get(k)
            if raw:
                traces.append(TraceRecord.from_dict(json.loads(raw)))
        return traces

    # ─── Vector Store & Cosine Similarity ─────────────────────────────────────

    def store_vector(self, key: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Stores a vector with associated metadata."""
        self._vectors[key] = (vector, metadata)

    def search_vectors(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Cosine similarity search over stored vectors."""
        if not self._vectors or not query_vector:
            return []

        def cosine_sim(v1: list[float], v2: list[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            if norm1 == 0.0 or norm2 == 0.0:
                return 0.0
            return dot / (norm1 * norm2)

        scored: list[tuple[str, float, dict[str, Any]]] = []
        for key, (vec, meta) in self._vectors.items():
            if len(vec) == len(query_vector):
                score = cosine_sim(query_vector, vec)
                scored.append((key, score, meta))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def batch_search_vectors(
        self, queries: list[list[float]], top_k: int = 5
    ) -> list[list[tuple[str, float, dict[str, Any]]]]:
        """Executes vector searches for multiple query vectors in batch."""
        return [self.search_vectors(q, top_k=top_k) for q in queries]

    def trim_stream(self, stream: str, max_len: int = 1000) -> int:
        """Trims a stream to at most max_len entries to prevent memory flooding."""
        if self.is_mock:
            if stream in self._client.streams:
                original_len = len(self._client.streams[stream])
                if original_len > max_len:
                    self._client.streams[stream] = self._client.streams[stream][-max_len:]
                    return original_len - max_len
            return 0

        try:
            return int(self._client.xtrim(stream, maxlen=max_len))
        except Exception:
            return 0

    def set_with_ttl(self, key: str, value: str, ttl_seconds: int = 3600) -> bool:
        """Stores a key with time-to-live expiration."""
        if self.is_mock:
            self._client.set(key, value)
            return True

        try:
            return bool(self._client.setex(key, ttl_seconds, value))
        except Exception:
            return False
