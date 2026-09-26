"""Ingest PDFs (literature review + this project's own generated papers) into Chroma.

Two corpora, deliberately kept in separate collections:

  * `literature`  -- external papers read as background. Retrieval over these
    supports a literature-grounding claim.
  * `own_papers`  -- PDFs this repo generated under `papers/`. These are
    indexed so a reviewer (human or model) can ask what this project has
    already asserted, and where.

**Provenance is the point, not a nicety.** The 2026-09-26 audit found that no
paper in `papers/` embeds a hash, run id, or path linking any quantitative
claim to an artifact under `results/`, while several figure generators
synthesise their curves outright. Every chunk stored here therefore carries
`source_path`, `source_sha256`, and `page`, so a claim found by retrieval can
always be traced back to the exact bytes it came from. A future claims-audit
can then ask "which file, which page, which hash" and get an answer.

Text extraction is `pypdf`. PDFs that are pure scans yield no text layer;
those are reported as skipped with a reason rather than indexed as empty, so
the collection count never overstates coverage.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from anse.memory.ollama_embeddings import OllamaEmbeddingFunction

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_CHARS = 1800
DEFAULT_CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 40


@dataclass
class IngestReport:
    """What actually happened, per file. A skip is a result, not a failure."""

    indexed: list[str] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    chunks_written: int = 0
    collection: str = ""
    embedding_model: str = ""
    embedding_dimension: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "collection": self.collection,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "files_indexed": len(self.indexed),
            "files_skipped": len(self.skipped),
            "chunks_written": self.chunks_written,
            "indexed": self.indexed,
            "skipped": self.skipped,
        }


def sha256_of(path: Path) -> str:
    """Content hash, used as the provenance anchor for every chunk of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_pdf_pages(path: Path) -> list[tuple[int, str]]:
    """Return (page_number, text) for pages that carry an extractable text layer."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # a single malformed page must not lose the file
            logger.warning("%s page %d: extraction failed: %s", path.name, index, exc)
            continue
        if text.strip():
            pages.append((index, text))
    return pages


def chunk_text(
    text: str,
    chunk_chars: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split on a character window with overlap, preferring paragraph breaks.

    Overlap exists so a sentence spanning a boundary is still retrievable from
    at least one chunk.
    """
    if overlap >= chunk_chars:
        raise ValueError("overlap must be smaller than chunk_chars")

    normalized = text.replace("\r\n", "\n").strip()
    if len(normalized) <= chunk_chars:
        return [normalized] if len(normalized) >= MIN_CHUNK_CHARS else []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_chars, len(normalized))
        window = normalized[start:end]

        # Prefer to break at a paragraph boundary inside the last 30% of the
        # window, so chunks align to structure rather than to arbitrary offsets.
        if end < len(normalized):
            pivot = window.rfind("\n\n", int(chunk_chars * 0.7))
            if pivot != -1:
                end = start + pivot
                window = normalized[start:end]

        candidate = window.strip()
        if len(candidate) >= MIN_CHUNK_CHARS:
            chunks.append(candidate)

        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


class DocumentStore:
    """Chroma-backed store for PDF corpora, embedded with a real model."""

    def __init__(
        self,
        persist_directory: Path | str,
        collection: str,
        embedding_function: OllamaEmbeddingFunction | None = None,
    ) -> None:
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection
        self.embedding_function = embedding_function or OllamaEmbeddingFunction()
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        import chromadb

        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self._collection.count()

    def already_indexed(self, source_sha256: str) -> bool:
        """True if any chunk from this exact file content is present.

        Keyed on content hash, not path, so a moved or renamed file is not
        re-indexed and an edited file is.
        """
        existing = self._collection.get(
            where={"source_sha256": source_sha256}, limit=1
        )
        return bool(existing.get("ids"))

    def ingest_pdf(self, path: Path, extra_metadata: dict[str, Any] | None = None) -> int:
        """Index one PDF. Returns the number of chunks written."""
        digest = sha256_of(path)
        if self.already_indexed(digest):
            logger.info("%s already indexed (sha256=%s)", path.name, digest[:12])
            return 0

        pages = extract_pdf_pages(path)
        if not pages:
            raise ValueError(
                f"{path.name}: no extractable text layer (likely a scanned image)"
            )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for page_number, page_text in pages:
            for chunk_index, chunk in enumerate(chunk_text(page_text)):
                ids.append(f"{digest[:16]}:p{page_number}:c{chunk_index}")
                documents.append(chunk)
                metadata: dict[str, Any] = {
                    "source_path": str(path),
                    "source_name": path.name,
                    "source_sha256": digest,
                    "page": page_number,
                    "chunk_index": chunk_index,
                }
                if extra_metadata:
                    metadata.update(extra_metadata)
                metadatas.append(metadata)

        if not documents:
            raise ValueError(f"{path.name}: text layer present but no chunk met the minimum length")

        # Batch the upsert; Chroma embeds via our function, which raises rather
        # than substituting a placeholder if Ollama is unreachable.
        BATCH = 32
        for start in range(0, len(documents), BATCH):
            self._collection.upsert(
                ids=ids[start : start + BATCH],
                documents=documents[start : start + BATCH],
                metadatas=metadatas[start : start + BATCH],
            )
        return len(documents)

    def ingest_text_file(
        self, path: Path, extra_metadata: dict[str, Any] | None = None
    ) -> int:
        """Index a plain-text or Markdown document.

        The literature this project actually cites lives in Markdown, not PDF
        (`docs/LITERATURE_REVIEW_RAG.md`, `docs/EBM_JEPA_Foundations.md`,
        `docs/LeCun2006_EBM_Summary.md`). Restricting ingestion to PDFs reported an
        empty `literature` collection while the material sat on disk unindexed,
        which reads as "no literature" rather than "wrong file extension".

        Provenance is identical to the PDF path: content hash plus a page number,
        which for a flat text file is always 1.
        """
        digest = sha256_of(path)
        if self.already_indexed(digest):
            logger.info("%s already indexed (sha256=%s)", path.name, digest[:12])
            return 0

        text = path.read_text(encoding="utf-8", errors="replace")
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError(f"{path.name}: no chunk met the minimum length")

        ids, documents, metadatas = [], [], []
        for index, chunk in enumerate(chunks):
            ids.append(f"{digest[:16]}:t{index}")
            documents.append(chunk)
            metadata: dict[str, Any] = {
                "source_path": str(path),
                "source_name": path.name,
                "source_sha256": digest,
                "page": 1,
                "chunk_index": index,
            }
            if extra_metadata:
                metadata.update(extra_metadata)
            metadatas.append(metadata)

        BATCH = 32
        for start in range(0, len(documents), BATCH):
            self._collection.upsert(
                ids=ids[start : start + BATCH],
                documents=documents[start : start + BATCH],
                metadatas=metadatas[start : start + BATCH],
            )
        return len(documents)

    def ingest_directory(
        self,
        directory: Path | str,
        pattern: str = "*.pdf",
        extra_metadata: dict[str, Any] | None = None,
    ) -> IngestReport:
        """Index every matching file under `directory`, reporting skips honestly.

        Dispatches on extension: `.pdf` goes through the PDF text extractor, and
        `.md`/`.txt`/`.rst` through the plain-text path.
        """
        directory = Path(directory)
        report = IngestReport(
            collection=self.collection_name,
            embedding_model=self.embedding_function.model,
        )

        TEXT_SUFFIXES = {".md", ".txt", ".rst"}
        for path in sorted(directory.rglob(pattern)):
            try:
                if path.suffix.lower() in TEXT_SUFFIXES:
                    written = self.ingest_text_file(path, extra_metadata=extra_metadata)
                else:
                    written = self.ingest_pdf(path, extra_metadata=extra_metadata)
            except Exception as exc:
                report.skipped.append({"path": str(path), "reason": str(exc)})
                logger.warning("skipped %s: %s", path.name, exc)
                continue
            if written:
                report.indexed.append(str(path))
                report.chunks_written += written
            else:
                report.skipped.append(
                    {"path": str(path), "reason": "already indexed (same sha256)"}
                )

        report.embedding_dimension = self.embedding_function.dimension
        return report

    def query(
        self, question: str, n_results: int = 5, where: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Semantic search. Every hit carries its provenance metadata."""
        results = self._collection.query(
            query_texts=[question], n_results=n_results, where=where
        )
        hits: list[dict[str, Any]] = []
        ids = results.get("ids") or [[]]
        if not ids[0]:
            return hits
        for i in range(len(ids[0])):
            hits.append(
                {
                    "id": ids[0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )
        return hits


def ingest_project_corpora(
    persist_directory: Path | str,
    papers_dir: Path | str = "papers",
    literature_dirs: Iterable[Path | str] = ("docs",),
) -> dict[str, dict[str, Any]]:
    """Ingest this project's own papers and its literature into separate collections."""
    reports: dict[str, dict[str, Any]] = {}

    own = DocumentStore(persist_directory, "own_papers")
    reports["own_papers"] = own.ingest_directory(
        papers_dir, extra_metadata={"corpus": "own_papers"}
    ).as_dict()

    lit = DocumentStore(persist_directory, "literature")
    combined = IngestReport(
        collection="literature", embedding_model=lit.embedding_function.model
    )
    for directory in literature_dirs:
        partial = lit.ingest_directory(directory, extra_metadata={"corpus": "literature"})
        combined.indexed.extend(partial.indexed)
        combined.skipped.extend(partial.skipped)
        combined.chunks_written += partial.chunks_written
    combined.embedding_dimension = lit.embedding_function.dimension
    reports["literature"] = combined.as_dict()

    return reports
