"""Real semantic embeddings via a local Ollama model.

This exists to replace `chroma_rag.FastDeterministicEmbeddingFunction`, which
builds vectors from `hashlib.md5` over character n-grams. That function is
deterministic and fast, and it is a legitimate *cache key*, but it carries no
semantic signal: nearest neighbours in md5 space are hash collisions, not
related meanings. Anything presented to a user as "RAG" or "semantic search"
must not be backed by it.

Design constraint, learned from this repo's own audit history: **fail closed**.
`anse/memory/redis_memory.py` and `antigravity-harness/storage/redis_bus.py`
both swap in a volatile in-memory substitute when their backend is unreachable
and return success, so callers cannot tell a durable write from a discarded
one. This module raises `EmbeddingUnavailableError` instead. A caller that
wants a degraded mode must choose it explicitly.

Dimensionality is a property of the model, not a constant here: this host's
`qwen3-embedding:0.6b` returns 1024 floats (verified by live call). The first
successful response fixes `dimension` for the instance, and every later
response is checked against it -- a silent dimension change between batches
would corrupt a Chroma collection, and `anse/jepa/dataset.py` raises
`HiddenDimMismatchError` on exactly that class of drift downstream.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Sequence

import httpx

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:0.6b"


class EmbeddingUnavailableError(RuntimeError):
    """The embedding backend could not produce a vector.

    Raised rather than returning a placeholder, so that no caller can persist
    a non-semantic vector into a collection that claims to be semantic.
    """


class OllamaEmbeddingFunction:
    """Chroma-compatible embedding function backed by a local Ollama model.

    Implements the `chromadb.EmbeddingFunction` call protocol
    (`__call__(input) -> list[list[float]]`) without importing chromadb, so
    this module stays usable for plain embedding work and in environments
    where chromadb is not installed.
    """

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
        timeout_s: float = 120.0,
        max_retries: int = 3,
    ) -> None:
        self.model = model or os.environ.get(
            "ANSE_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        )
        self.host = (host or os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)).rstrip(
            "/"
        )
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self._dimension: int | None = None

    @property
    def dimension(self) -> int | None:
        """Vector width, known only after the first successful embed."""
        return self._dimension

    def name(self) -> str:
        """Chroma >=0.5 asks an embedding function to identify itself.

        The model is part of the identity: vectors from two different models
        must never land in one collection.
        """
        return f"ollama:{self.model}"

    def _embed_one(self, text: str) -> list[float]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = httpx.post(
                    f"{self.host}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=self.timeout_s,
                )
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "embedding request failed (attempt %d/%d): %s",
                    attempt,
                    self.max_retries,
                    exc,
                )
                continue

            if response.status_code != 200:
                last_error = EmbeddingUnavailableError(
                    f"Ollama returned {response.status_code}: {response.text[:200]}"
                )
                logger.warning(
                    "embedding HTTP %d (attempt %d/%d)",
                    response.status_code,
                    attempt,
                    self.max_retries,
                )
                continue

            vector = response.json().get("embedding")
            if not vector:
                last_error = EmbeddingUnavailableError(
                    f"Ollama response for model {self.model!r} contained no embedding"
                )
                continue
            return [float(x) for x in vector]

        raise EmbeddingUnavailableError(
            f"could not embed with {self.model!r} at {self.host} after "
            f"{self.max_retries} attempts: {last_error}"
        ) from last_error

    def __call__(self, input: Sequence[str]) -> list[list[float]]:  # noqa: A002
        """Embed a batch. The parameter is named `input` to match Chroma's protocol."""
        if isinstance(input, str):
            raise TypeError(
                "OllamaEmbeddingFunction expects a sequence of strings, not a bare str"
            )

        # Validate the whole batch before spending a single network call. Ollama's
        # /api/embeddings rejects an empty prompt, and a caller that chunked badly
        # should hear about it immediately rather than after N-1 successful embeds.
        for position, text in enumerate(input):
            if not text or not text.strip():
                raise ValueError(
                    f"cannot embed an empty or whitespace-only string at index "
                    f"{position}; filter empty chunks before embedding"
                )

        vectors: list[list[float]] = []
        for text in input:
            vector = self._embed_one(text)

            if self._dimension is None:
                self._dimension = len(vector)
                logger.info(
                    "embedding dimension fixed at %d for model %s",
                    self._dimension,
                    self.model,
                )
            elif len(vector) != self._dimension:
                raise EmbeddingUnavailableError(
                    f"dimension drift from {self.model!r}: expected "
                    f"{self._dimension}, got {len(vector)}"
                )
            vectors.append(vector)
        return vectors

    def probe(self) -> dict[str, Any]:
        """Verify the backend is live and report what it is.

        Used by deployment validation so a broken embedding backend surfaces
        as a failed check rather than as a silently degraded index.
        """
        vector = self._embed_one("probe")
        if self._dimension is None:
            self._dimension = len(vector)
        return {
            "model": self.model,
            "host": self.host,
            "dimension": len(vector),
            "available": True,
        }
