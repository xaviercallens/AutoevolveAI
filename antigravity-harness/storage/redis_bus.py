"""
Redis Bus: High-throughput event streaming, JSON state persistence, and Vector Store.
Supports Redis Streams (subtasks, attestation receipts), Hash/JSON documents (traces),
and Vector Embeddings for similarity lookup across lessons and failing patterns.
Includes an in-memory fallback engine for isolated testing without an external Redis daemon.

Note: Persistence is guaranteed only when connected to a live Redis instance. When Redis is
unavailable, writes silently fall back to volatile in-memory storage (is_mock=True). Callers
must inspect the is_mock flag in write method return values to distinguish durable from
volatile writes.
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from dataclasses import MISSING as dataclass_MISSING, asdict, dataclass, field, fields
from typing import Any

logger = logging.getLogger(__name__)


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
    def from_dict(cls, data: dict[str, Any]) -> "TraceRecord":
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        # Check required fields are present
        required = {f.name for f in fields(cls) if f.default is f.default_factory is type}  # type: ignore[comparison-overlap]
        missing = {f.name for f in fields(cls)
                   if f.default is dataclass_MISSING
                   and f.default_factory is dataclass_MISSING} - set(filtered)
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return cls(**filtered)


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
        except (
            ConnectionError,
            ImportError,
            TimeoutError,
            OSError,
        ) as e:
            logger.error(
                "Failed to connect to Redis at %s:%d, falling back to volatile in-memory storage: %s",
                self.host,
                self.port,
                e,
            )
            self._client = InMemoryBusBackend()
            self.is_mock = True
        except Exception as e:
            logger.error(
                "Unexpected error connecting to Redis at %s:%d, falling back to volatile in-memory storage: %s",
                self.host,
                self.port,
                e,
            )
            self._client = InMemoryBusBackend()
            self.is_mock = True

    # ─── Event Streams ─────────────────────────────────────────────────────────

    def publish_event(self, stream: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Publish an event to a Redis Stream.

        Returns a dict with keys:
        - 'value': the message ID (str)
        - 'is_mock': True if write is volatile in-memory, False if persisted to Redis
        """
        if self.is_mock:
            return {"value": self._client.xadd(stream, payload), "is_mock": True}

        stringified = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in payload.items()
        }
        return {"value": self._client.xadd(stream, stringified), "is_mock": False}

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

    def record_trace(self, trace: TraceRecord) -> dict[str, Any]:
        """
        Persist a complete execution trace.

        Returns a dict with keys:
        - 'value': the trace ID (str)
        - 'is_mock': True if write is volatile in-memory, False if persisted to Redis
        """
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

        return {"value": trace.trace_id, "is_mock": self.is_mock}

    def get_trace(self, trace_id: str) -> TraceRecord | None:
        """Fetch an execution trace by ID."""
        key = f"antigravity:trace:{trace_id}"
        raw = self._client.get(key)
        if not raw:
            return None
        data = json.loads(raw)
        return TraceRecord.from_dict(data)

    def list_all_traces(self) -> list[TraceRecord]:
        """Extract all traces from storage.

        Records that cannot be deserialized (e.g. stale data from other pipelines
        sharing the same Redis) are silently skipped.
        """
        traces: list[TraceRecord] = []
        if self.is_mock:
            for k, val in self._client.keys.items():
                if k.startswith("antigravity:trace:"):
                    try:
                        traces.append(TraceRecord.from_dict(json.loads(val)))
                    except (ValueError, TypeError):
                        pass
            return traces

        keys = self._client.keys("antigravity:trace:*")
        for k in keys:
            raw = self._client.get(k)
            if raw:
                try:
                    traces.append(TraceRecord.from_dict(json.loads(raw)))
                except (ValueError, TypeError):
                    pass
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

    def trim_stream(self, stream: str, max_len: int = 1000) -> dict[str, Any]:
        """
        Trims a stream to at most max_len entries to prevent memory flooding.

        Returns a dict with keys:
        - 'value': number of entries trimmed (int)
        - 'is_mock': True if operation was on volatile in-memory storage, False if on Redis
        """
        if self.is_mock:
            trimmed = 0
            if stream in self._client.streams:
                original_len = len(self._client.streams[stream])
                if original_len > max_len:
                    self._client.streams[stream] = self._client.streams[stream][-max_len:]
                    trimmed = original_len - max_len
            return {"value": trimmed, "is_mock": True}

        try:
            trimmed = int(self._client.xtrim(stream, maxlen=max_len))
            return {"value": trimmed, "is_mock": False}
        except Exception as e:
            logger.error("Failed to trim stream %s: %s", stream, e)
            return {"value": 0, "is_mock": False}

    def set_with_ttl(self, key: str, value: str, ttl_seconds: int = 3600) -> dict[str, Any]:
        """
        Stores a key with time-to-live expiration.

        Returns a dict with keys:
        - 'value': True if write succeeded, False otherwise (bool)
        - 'is_mock': True if write is volatile in-memory, False if persisted to Redis
        """
        if self.is_mock:
            self._client.set(key, value)
            return {"value": True, "is_mock": True}

        try:
            success = bool(self._client.setex(key, ttl_seconds, value))
            return {"value": success, "is_mock": False}
        except Exception as e:
            logger.error("Failed to set key %s with TTL: %s", key, e)
            return {"value": False, "is_mock": False}
