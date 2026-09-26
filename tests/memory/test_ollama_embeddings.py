"""Tests for the real (non-md5) embedding function.

The point of `OllamaEmbeddingFunction` is that it is semantic and that it fails
closed. Both properties are tested here, plus the dimension-drift guard that
protects a Chroma collection from being silently corrupted.

Network-dependent tests are marked and skipped when Ollama is unreachable, so
the suite stays green on a box without it -- but they are real integration
tests when it is up, not mocks of the thing under test.
"""

from __future__ import annotations

import httpx
import pytest

from anse.memory.ollama_embeddings import (
    EmbeddingUnavailableError,
    OllamaEmbeddingFunction,
)


def _ollama_is_up(host: str = "http://localhost:11434") -> bool:
    try:
        return httpx.get(f"{host}/api/tags", timeout=5).status_code == 200
    except httpx.HTTPError:
        return False


requires_ollama = pytest.mark.skipif(
    not _ollama_is_up(), reason="Ollama not reachable on localhost:11434"
)


def test_rejects_bare_string_input() -> None:
    """Chroma passes a sequence; a bare str would silently embed per-character."""
    fn = OllamaEmbeddingFunction()
    with pytest.raises(TypeError, match="sequence of strings"):
        fn("not a list")


def test_rejects_empty_text() -> None:
    """An empty chunk must raise, not yield a zero vector that pollutes the index."""
    fn = OllamaEmbeddingFunction()
    with pytest.raises(ValueError, match="empty or whitespace-only"):
        fn(["valid text", "   "])


def test_name_includes_model_so_collections_cannot_mix() -> None:
    """Two models must not share a collection; identity carries the model name."""
    a = OllamaEmbeddingFunction(model="model-a")
    b = OllamaEmbeddingFunction(model="model-b")
    assert a.name() == "ollama:model-a"
    assert a.name() != b.name()


def test_fails_closed_when_backend_unreachable() -> None:
    """Unreachable backend raises rather than returning a placeholder vector.

    This is the behaviour that distinguishes this module from
    `anse/memory/redis_memory.py`, which logs a warning and returns False, and
    from `chroma_rag.FastDeterministicEmbeddingFunction`, which always succeeds
    with a non-semantic md5 vector.
    """
    fn = OllamaEmbeddingFunction(
        host="http://127.0.0.1:9", max_retries=1, timeout_s=2.0
    )
    with pytest.raises(EmbeddingUnavailableError, match="could not embed"):
        fn(["anything"])


def test_dimension_is_unknown_before_first_call() -> None:
    fn = OllamaEmbeddingFunction()
    assert fn.dimension is None


def test_satisfies_chroma_embedding_function_protocol() -> None:
    """Chroma calls `__call__` on upsert but `embed_query` on query.

    Because this class is duck-typed against Chroma's Protocol rather than
    subclassing it, `embed_query` does not come for free. Its absence produced
    a split failure in practice: ingestion of 315 chunks succeeded while every
    query raised AttributeError.
    """
    fn = OllamaEmbeddingFunction()
    for method in ("__call__", "embed_query", "name"):
        assert callable(getattr(fn, method, None)), f"missing {method}"


@requires_ollama
def test_embeds_and_fixes_dimension() -> None:
    """A live embed returns a real vector and pins the dimension."""
    fn = OllamaEmbeddingFunction()
    vectors = fn(["the harvester writes verified episodes"])

    assert len(vectors) == 1
    assert len(vectors[0]) > 100, "an embedding of ~100+ dims is expected, got a stub"
    assert fn.dimension == len(vectors[0])
    assert all(isinstance(x, float) for x in vectors[0])
    # A real embedding is not all-zero and not constant.
    assert len(set(vectors[0])) > 10, "vector looks degenerate, not a real embedding"


@requires_ollama
def test_embeddings_are_semantic_not_lexical() -> None:
    """The whole reason this module exists.

    Two sentences with different words but the same meaning must be closer than
    two sentences sharing many characters but unrelated in meaning. An md5
    n-gram embedding fails this; a real model passes it.
    """

    def cosine(u: list[float], v: list[float]) -> float:
        dot = sum(a * b for a, b in zip(u, v))
        nu = sum(a * a for a in u) ** 0.5
        nv = sum(b * b for b in v) ** 0.5
        return dot / (nu * nv)

    fn = OllamaEmbeddingFunction()
    related_a, related_b, unrelated = fn(
        [
            "the dog ran quickly across the field",
            "a canine sprinted rapidly over the meadow",
            "quarterly amortisation of deferred tax liabilities",
        ]
    )

    similar = cosine(related_a, related_b)
    different = cosine(related_a, unrelated)
    assert similar > different, (
        f"paraphrase similarity {similar:.3f} should exceed unrelated {different:.3f}; "
        "this embedding does not carry semantic signal"
    )


@requires_ollama
def test_probe_reports_live_backend() -> None:
    fn = OllamaEmbeddingFunction()
    info = fn.probe()
    assert info["available"] is True
    assert info["dimension"] > 100
    assert info["model"] == fn.model
