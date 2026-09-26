#!/usr/bin/env python3
"""Populate long-term memory: Claude Code transcripts + the PDF corpora.

Two independent ingests, reported separately:

  * **Transcripts** -> Redis (durable recall) + Chroma (semantic retrieval).
    Every turn is scrubbed before storage and marked `trainable=False`. See
    `anse/memory/transcript_ltm.py` for why that flag is not negotiable.

  * **PDFs** -> Chroma, in two collections: `own_papers` (this repo's generated
    papers) and `literature` (background reading). Every chunk carries
    `source_path`, `source_sha256` and `page`, so a claim surfaced by retrieval
    can be traced to the exact bytes it came from.

Both use real 1024-d embeddings from a local Ollama model, not the md5 n-gram
pseudo-vectors of `chroma_rag.FastDeterministicEmbeddingFunction`.

Usage:
    .venv/bin/python scripts/ingest_memory.py --all
    .venv/bin/python scripts/ingest_memory.py --transcripts --limit-files 5
    .venv/bin/python scripts/ingest_memory.py --pdfs
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DISK2 = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI")

# Chroma lives on disk 2: it grows with the corpus and disk 2 has the room.
DEFAULT_CHROMA_ROOT = DISK2 / "datalake" / "chroma" / "ltm"

logger = logging.getLogger("ingest_memory")


def ingest_transcripts(
    chroma_root: Path,
    limit_files: int | None,
    redis_url: str | None,
    transcript_root: Path | None = None,
) -> dict[str, Any]:
    from anse.memory.transcript_ltm import DEFAULT_TRANSCRIPT_ROOT, import_all

    root = transcript_root or DEFAULT_TRANSCRIPT_ROOT
    report = import_all(
        root=root,
        redis_url=redis_url,
        chroma_directory=chroma_root / "transcripts",
        limit_files=limit_files,
    )
    report["transcript_root"] = str(root)
    scrubbed = report["scrub"]["total_replacements"]
    if report["turns_stored"] and scrubbed == 0:
        # Not an error, but worth surfacing: a corpus of real development
        # transcripts that contains zero paths, e-mails or tokens is unusual
        # enough to be worth a human glance at the scrub patterns.
        logger.warning(
            "stored %d turns but scrubbed nothing -- verify the scrub patterns",
            report["turns_stored"],
        )
    return report


def ingest_pdfs(chroma_root: Path) -> dict[str, Any]:
    from anse.memory.document_store import ingest_project_corpora

    return ingest_project_corpora(
        persist_directory=chroma_root / "documents",
        papers_dir=REPO_ROOT / "papers",
        literature_dirs=[REPO_ROOT / "docs"],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="transcripts and PDFs")
    parser.add_argument("--transcripts", action="store_true")
    parser.add_argument("--pdfs", action="store_true")
    parser.add_argument("--limit-files", type=int, default=None)
    parser.add_argument(
        "--transcript-root",
        type=Path,
        default=None,
        help="Directory of session JSONL to import. The default is ~/.claude/projects, "
        "which is EVERY project on this machine -- measured here at 1,601 files / "
        "80,537 turns / roughly 5.6 h of embedding. Scope it to one project unless "
        "you mean the whole corpus, and note that other projects' transcripts are "
        "other projects' data.",
    )
    parser.add_argument("--chroma-root", type=Path, default=DEFAULT_CHROMA_ROOT)
    parser.add_argument("--redis-url", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not (args.all or args.transcripts or args.pdfs):
        parser.error("choose --all, --transcripts and/or --pdfs")

    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
    )
    args.chroma_root.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {"chroma_root": str(args.chroma_root)}
    failed = False

    if args.all or args.transcripts:
        logger.info("ingesting Claude Code transcripts -> Redis + Chroma")
        try:
            results["transcripts"] = ingest_transcripts(
                args.chroma_root,
                args.limit_files,
                args.redis_url,
                transcript_root=args.transcript_root,
            )
            t = results["transcripts"]
            logger.info(
                "  %d turns from %d files across %d sessions; %d secrets scrubbed",
                t["turns_stored"],
                t["files_read"],
                t["sessions"],
                t["scrub"]["total_replacements"],
            )
        except Exception as exc:
            logger.error("  transcript ingest FAILED: %s", exc)
            results["transcripts"] = {"error": str(exc)}
            failed = True

    if args.all or args.pdfs:
        logger.info("ingesting PDF corpora -> Chroma")
        try:
            results["pdfs"] = ingest_pdfs(args.chroma_root)
            for name, report in results["pdfs"].items():
                logger.info(
                    "  %s: %d files, %d chunks, %d skipped (%d-d embeddings)",
                    name,
                    report["files_indexed"],
                    report["chunks_written"],
                    report["files_skipped"],
                    report["embedding_dimension"] or 0,
                )
        except Exception as exc:
            logger.error("  PDF ingest FAILED: %s", exc)
            results["pdfs"] = {"error": str(exc)}
            failed = True

    if args.json:
        print(json.dumps(results, indent=2, default=str))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
