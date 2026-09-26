"""Import Claude Code session transcripts into long-term memory.

Claude Code already persists every session as JSONL under
`~/.claude/projects/<slug>/<session-id>.jsonl`: user prompts, assistant
replies, tool calls and tool results. `docs/ROADMAP_V1_V2_COMPANION.md` §4.1
observes that a nightly importer over those files is sufficient to build
long-term memory with no live plumbing, and that is what this module is.

Two hard constraints, both taken from that roadmap's §4.5, both enforced here
rather than documented and hoped for:

1. **Scrubbing is a gate, not a pass.** Transcripts contain tokens, keys,
   absolute home paths and e-mail addresses. `scrub()` runs before anything is
   persisted, and `ScrubReport` records what it removed so a run that scrubbed
   nothing from a corpus full of secrets is visibly suspicious rather than
   silently clean.

2. **These records are retrieval-only.** Provider terms restrict using
   assistant outputs as training targets. Every record is therefore written
   with `trainable: False` and `usage: "retrieval_only"`, and
   `iter_training_candidates()` deliberately does not exist in this module.
   The defensible design the roadmap describes trains on *this project's own*
   artifacts -- diffs, test outcomes, verifier results, and the local model's
   own samples -- and uses assistant transcripts for retrieval and episode
   segmentation only. Changing that is a policy decision for the repository
   owner, not a code change to make casually.

Storage is dual, mirroring `anse/memory/harvester.py`: Redis for durable
key-addressed recall, Chroma for semantic retrieval. Redis being unreachable
raises; it does not silently degrade to a dict (the defect
`anse/memory/redis_memory.py` was found to have).
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)

DEFAULT_TRANSCRIPT_ROOT = Path.home() / ".claude" / "projects"
REDIS_KEY_PREFIX = "anse:ltm:transcript"
CHROMA_COLLECTION = "claude_code_sessions"

# Ordered most-specific-first: a GitHub token would also match the generic
# high-entropy rule, and the specific label is more useful in the report.
_SCRUB_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b")),
    ("home_path", re.compile(r"/home/[A-Za-z0-9_.\-]+")),
)


@dataclass
class ScrubReport:
    """Counts per pattern. Visible so an implausibly clean run is noticeable."""

    replacements: dict[str, int] = field(default_factory=dict)

    def record(self, label: str, count: int) -> None:
        if count:
            self.replacements[label] = self.replacements.get(label, 0) + count

    @property
    def total(self) -> int:
        return sum(self.replacements.values())


def scrub(text: str, report: ScrubReport | None = None) -> str:
    """Remove credentials, e-mail addresses and absolute home paths."""
    cleaned = text
    for label, pattern in _SCRUB_PATTERNS:
        cleaned, count = pattern.subn(f"[REDACTED:{label}]", cleaned)
        if report is not None:
            report.record(label, count)
    return cleaned


@dataclass
class TranscriptTurn:
    """One turn of a session, already scrubbed."""

    session_id: str
    project_slug: str
    turn_index: int
    role: str
    text: str
    tool_names: list[str] = field(default_factory=list)
    timestamp: str | None = None
    # See module docstring: provider terms. Not a suggestion.
    trainable: bool = False
    usage: str = "retrieval_only"

    @property
    def record_id(self) -> str:
        return f"{self.session_id}:{self.turn_index}"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text_from_content(content: Any) -> tuple[str, list[str]]:
    """Flatten Claude Code's content field to text plus any tool names seen."""
    if isinstance(content, str):
        return content, []

    parts: list[str] = []
    tools: list[str] = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text" and block.get("text"):
                parts.append(str(block["text"]))
            elif block_type == "thinking" and block.get("thinking"):
                parts.append(str(block["thinking"]))
            elif block_type == "tool_use":
                name = str(block.get("name", "unknown"))
                tools.append(name)
                parts.append(f"[tool_use:{name}] {json.dumps(block.get('input', {}))[:2000]}")
            elif block_type == "tool_result":
                raw = block.get("content")
                rendered = raw if isinstance(raw, str) else json.dumps(raw)[:2000]
                parts.append(f"[tool_result] {rendered}")
    return "\n".join(parts), tools


def parse_transcript(path: Path, scrub_report: ScrubReport | None = None) -> list[TranscriptTurn]:
    """Read one session JSONL into scrubbed turns.

    Malformed lines are skipped with a warning rather than aborting the file --
    transcripts are append-only logs and a truncated final line is normal.
    """
    session_id = path.stem
    project_slug = path.parent.name
    turns: list[TranscriptTurn] = []

    with path.open(encoding="utf-8") as handle:
        for turn_index, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning("%s line %d: %s", path.name, turn_index, exc)
                continue

            message = event.get("message")
            if not isinstance(message, dict):
                continue
            role = message.get("role")
            if role not in ("user", "assistant"):
                continue

            text, tools = _text_from_content(message.get("content"))
            if not text.strip():
                continue

            turns.append(
                TranscriptTurn(
                    session_id=session_id,
                    project_slug=project_slug,
                    turn_index=turn_index,
                    role=str(role),
                    text=scrub(text, scrub_report),
                    tool_names=tools,
                    timestamp=event.get("timestamp"),
                )
            )
    return turns


# Well under the 4096-token runtime window Ollama gives the embedding model
# (~4 chars/token, so ~6000 chars is ~1500 tokens). Overlap keeps a sentence that
# straddles a boundary retrievable from at least one window.
EMBED_CHUNK_CHARS = 6000
EMBED_CHUNK_OVERLAP = 400


def _chunk_for_embedding(
    text: str,
    chunk_chars: int = EMBED_CHUNK_CHARS,
    overlap: int = EMBED_CHUNK_OVERLAP,
) -> list[str]:
    """Split a turn into windows that fit the embedding model's runtime context.

    Always returns at least one non-empty chunk, because the caller has already
    established the turn has text and the embedding function rejects empty input.
    """
    stripped = text.strip()
    if len(stripped) <= chunk_chars:
        return [stripped]

    chunks: list[str] = []
    start = 0
    while start < len(stripped):
        end = min(start + chunk_chars, len(stripped))
        window = stripped[start:end].strip()
        if window:
            chunks.append(window)
        if end >= len(stripped):
            break
        start = max(end - overlap, start + 1)
    return chunks or [stripped[:chunk_chars]]


def iter_transcripts(root: Path | str = DEFAULT_TRANSCRIPT_ROOT) -> Iterator[Path]:
    """Yield every session JSONL under the Claude Code projects root."""
    root = Path(root)
    if not root.exists():
        return
    yield from sorted(root.rglob("*.jsonl"))


class TranscriptLTM:
    """Dual-write long-term memory: Redis for recall, Chroma for retrieval."""

    def __init__(
        self,
        redis_url: str | None = None,
        chroma_directory: Path | str | None = None,
        collection: str = CHROMA_COLLECTION,
        enable_chroma: bool = True,
    ) -> None:
        import redis

        self.redis_url = redis_url or os.environ.get(
            "ANSE_REDIS_URL", "redis://localhost:6379/0"
        )
        # from_url does not connect; ping() is what proves the backend is there.
        self._redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
        self._redis.ping()

        self._collection = None
        if enable_chroma and chroma_directory is not None:
            from anse.memory.ollama_embeddings import OllamaEmbeddingFunction
            import chromadb

            directory = Path(chroma_directory)
            directory.mkdir(parents=True, exist_ok=True)
            self._embedding_function = OllamaEmbeddingFunction()
            client = chromadb.PersistentClient(path=str(directory))
            self._collection = client.get_or_create_collection(
                name=collection,
                embedding_function=self._embedding_function,
                metadata={"hnsw:space": "cosine"},
            )

    def store_turn(self, turn: TranscriptTurn) -> None:
        """Write one turn to Redis, and to Chroma when enabled."""
        key = f"{REDIS_KEY_PREFIX}:{turn.record_id}"
        self._redis.hset(
            key,
            mapping={
                "session_id": turn.session_id,
                "project_slug": turn.project_slug,
                "turn_index": str(turn.turn_index),
                "role": turn.role,
                "text": turn.text,
                "tool_names": json.dumps(turn.tool_names),
                "timestamp": turn.timestamp or "",
                "trainable": "0",
                "usage": turn.usage,
            },
        )
        self._redis.sadd(f"{REDIS_KEY_PREFIX}:sessions", turn.session_id)

        if self._collection is not None:
            # Redis holds the turn whole; Chroma gets it in windows.
            #
            # Ollama's RUNTIME context for the embedding model is 4096 tokens even
            # though the model advertises 32768, and transcript turns are heavy-tailed:
            # measured median 298 chars but p99 10,461 and max 111,045. Embedding a
            # long turn whole returns HTTP 500 "the input length exceeds the context
            # length" and, because the embedding function fails closed, aborts the
            # whole import. Chunking keeps the durable record complete while making
            # every embedded document fit.
            chunks = _chunk_for_embedding(turn.text)
            base = {
                "session_id": turn.session_id,
                "project_slug": turn.project_slug,
                "role": turn.role,
                "turn_index": turn.turn_index,
                "tool_names": ",".join(turn.tool_names),
                "trainable": False,
                "usage": turn.usage,
                "chunks": len(chunks),
            }
            self._collection.upsert(
                ids=[f"{turn.record_id}:{i}" for i in range(len(chunks))],
                documents=chunks,
                metadatas=[{**base, "chunk_index": i} for i in range(len(chunks))],
            )

    def turn_count(self) -> int:
        """Number of turn records currently in Redis."""
        return len(list(self._redis.scan_iter(match=f"{REDIS_KEY_PREFIX}:*:*", count=1000)))

    def session_ids(self) -> set[str]:
        return set(self._redis.smembers(f"{REDIS_KEY_PREFIX}:sessions"))

    def search(self, question: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Semantic search over stored turns."""
        if self._collection is None:
            raise RuntimeError("Chroma is not enabled on this TranscriptLTM instance")
        results = self._collection.query(query_texts=[question], n_results=n_results)
        ids = results.get("ids") or [[]]
        if not ids[0]:
            return []
        return [
            {
                "id": ids[0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
            for i in range(len(ids[0]))
        ]


def import_all(
    root: Path | str = DEFAULT_TRANSCRIPT_ROOT,
    redis_url: str | None = None,
    chroma_directory: Path | str | None = None,
    limit_files: int | None = None,
) -> dict[str, Any]:
    """Import every available transcript. Returns a report of what was stored."""
    scrub_report = ScrubReport()
    ltm = TranscriptLTM(
        redis_url=redis_url,
        chroma_directory=chroma_directory,
        enable_chroma=chroma_directory is not None,
    )

    files_read = 0
    turns_stored = 0
    for path in iter_transcripts(root):
        if limit_files is not None and files_read >= limit_files:
            break
        turns = parse_transcript(path, scrub_report)
        for turn in turns:
            ltm.store_turn(turn)
            turns_stored += 1
        files_read += 1

    return {
        "files_read": files_read,
        "turns_stored": turns_stored,
        "sessions": len(ltm.session_ids()),
        "scrub": {"total_replacements": scrub_report.total, "by_pattern": scrub_report.replacements},
        "usage_policy": "retrieval_only -- not training targets (see module docstring)",
    }
