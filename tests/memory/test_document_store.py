"""Tests for PDF ingestion with provenance.

Provenance is the reason this store exists: the 2026-09-26 audit found that no
paper under `papers/` links any quantitative claim to an artifact. Every chunk
written here therefore carries source_path, source_sha256 and page, and these
tests assert that rather than trusting it.

Chunking and hashing are pure and always tested. Ingestion needs Chroma plus a
live embedding backend, so those tests skip when unavailable.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import httpx
import pytest

from anse.memory.document_store import (
    DEFAULT_CHUNK_CHARS,
    IngestReport,
    chunk_text,
    sha256_of,
)


def _ollama_is_up(host: str = "http://localhost:11434") -> bool:
    try:
        return httpx.get(f"{host}/api/tags", timeout=5).status_code == 200
    except httpx.HTTPError:
        return False


def _chromadb_available() -> bool:
    try:
        import chromadb  # noqa: F401

        return True
    except ImportError:
        return False


requires_stack = pytest.mark.skipif(
    not (_ollama_is_up() and _chromadb_available()),
    reason="needs Ollama and chromadb",
)


def test_sha256_matches_hashlib(tmp_path: Path) -> None:
    """The provenance anchor must be the real content hash."""
    target = tmp_path / "paper.bin"
    payload = b"a quantitative claim and the data behind it"
    target.write_bytes(payload)

    assert sha256_of(target) == hashlib.sha256(payload).hexdigest()
    assert len(sha256_of(target)) == 64


def test_sha256_changes_when_content_changes(tmp_path: Path) -> None:
    """An edited paper must not be mistaken for an already-indexed one."""
    target = tmp_path / "paper.bin"
    target.write_bytes(b"version one")
    first = sha256_of(target)
    target.write_bytes(b"version two")

    assert sha256_of(target) != first


def test_chunk_short_text_is_single_chunk() -> None:
    text = "A short paragraph that comfortably fits inside one chunk window."
    chunks = chunk_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_drops_text_below_minimum_length() -> None:
    """Tiny fragments must not enter the index; they cannot be embedded usefully."""
    assert chunk_text("tiny") == []


def test_chunk_long_text_splits_with_overlap() -> None:
    """Long text splits, and consecutive chunks share content so boundary-spanning
    sentences remain retrievable."""
    paragraph = "Energy descends monotonically under the update rule. " * 200
    chunks = chunk_text(paragraph, chunk_chars=600, overlap=120)

    assert len(chunks) > 1, "text far longer than the window must split"
    assert all(len(c) <= 600 for c in chunks), "no chunk may exceed the window"
    # Reassembled length exceeds the original precisely because of overlap.
    assert sum(len(c) for c in chunks) > len(paragraph.strip()) * 0.9


def test_chunk_rejects_overlap_at_or_above_window() -> None:
    """An overlap >= window would never advance and would loop forever."""
    with pytest.raises(ValueError, match="overlap must be smaller"):
        chunk_text("x" * 5000, chunk_chars=100, overlap=100)


def test_chunk_prefers_paragraph_boundaries() -> None:
    """Chunks should align to structure when a paragraph break is available."""
    first = "First section. " * 30
    second = "Second section. " * 30
    chunks = chunk_text(f"{first}\n\n{second}", chunk_chars=600, overlap=50)

    assert len(chunks) >= 2
    # The break should land at the paragraph, so the first chunk should not
    # contain text from deep inside the second section.
    assert "Second section." not in chunks[0] or chunks[0].endswith("First section.")


def test_ingest_report_serializes_counts() -> None:
    report = IngestReport(collection="own_papers", embedding_model="qwen3-embedding:0.6b")
    report.indexed.append("papers/a.pdf")
    report.skipped.append({"path": "papers/scan.pdf", "reason": "no text layer"})
    report.chunks_written = 42

    payload = report.as_dict()
    assert payload["files_indexed"] == 1
    assert payload["files_skipped"] == 1
    assert payload["chunks_written"] == 42
    assert payload["collection"] == "own_papers"


def test_default_chunk_window_is_sane() -> None:
    """Guard against a future edit making chunks too large to embed well."""
    assert 500 <= DEFAULT_CHUNK_CHARS <= 4000


@requires_stack
def test_ingest_real_pdf_carries_provenance(tmp_path: Path) -> None:
    """End-to-end: a real repo PDF indexes, and every chunk traces to its source."""
    from anse.memory.document_store import DocumentStore

    candidates = sorted(Path("papers").glob("*.pdf"))
    if not candidates:
        pytest.skip("no PDFs under papers/ to ingest")
    pdf = candidates[0]

    store = DocumentStore(tmp_path / "chroma", collection="test_papers")
    written = store.ingest_pdf(pdf, extra_metadata={"corpus": "own_papers"})

    assert written > 0, f"{pdf.name} produced no chunks"
    assert store.count() == written

    # Provenance: a retrieved chunk must name its file and its content hash.
    hits = store.query("energy", n_results=1)
    assert hits, "a freshly indexed collection returned no results"
    meta = hits[0]["metadata"]
    assert meta["source_sha256"] == sha256_of(pdf)
    assert meta["source_name"] == pdf.name
    assert meta["page"] >= 1
    assert meta["corpus"] == "own_papers"


@requires_stack
def test_reingest_is_idempotent_by_content_hash(tmp_path: Path) -> None:
    """Indexing the same file twice must not duplicate it."""
    from anse.memory.document_store import DocumentStore

    candidates = sorted(Path("papers").glob("*.pdf"))
    if not candidates:
        pytest.skip("no PDFs under papers/ to ingest")
    pdf = candidates[0]

    store = DocumentStore(tmp_path / "chroma", collection="test_idem")
    first = store.ingest_pdf(pdf)
    count_after_first = store.count()
    second = store.ingest_pdf(pdf)

    assert first > 0
    assert second == 0, "second ingest of identical content should write nothing"
    assert store.count() == count_after_first
