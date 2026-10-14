#!/usr/bin/env python3
"""Overnight long-term-memory ingest under the shared T4 lease (2026-10-07 night).

1. Conversations: every Claude Code transcript folder of this project (main checkout and its
   worktrees) -> Redis (whole turns, scrubbed, retrieval-only) + Chroma `claude_code_sessions`.
2. Repo documents: papers/, docs/, vendor/, results/*.pdf -> Chroma `own_papers` / `literature`.
3. The openai/math corpus (preprint PDFs, CONTENTS.md, lean/docs scope notes, reasoning traces)
   -> Chroma `openai_math_preprints`, resumable by content hash, with a hard deadline so the
   GPU is free for the 05:05 retrain.
4. Retrieval checks (a known query per collection must return the expected source).
5. A second transcript pass for this session's folder shortly before the deadline, so the
   rest of tonight's conversation is stored too.

Writes results/ltm_ingest/night_<date>.json. Fails loudly per step; one failed step does not
stop the others, and every step's status is recorded.

Run (interpreter with chromadb + redis + the repo's anse package on sys.path):
    /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run/.venv/bin/python \
        scripts/night_ltm_ingest.py --date 2026-10-07 --deadline-utc 04:40 --repass-utc 04:25
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import gpu_lease  # noqa: E402

PROJECTS = Path("/home/callensxavier_gmail_com/.claude/projects")
THIS_SESSION_DIR = PROJECTS / "-home-callensxavier-gmail-com-AutoevolveAI--claude-worktrees-openai-math-discovery"
CLONE = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math")
CHROMA_ROOT = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/chroma/ltm")
HOLDER = "ltm-ingest-night"

log = logging.getLogger("night_ltm_ingest")


def at_utc(hhmm: str, now: datetime) -> datetime:
    h, m = (int(x) for x in hhmm.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    return target if target > now else target + timedelta(days=1)


def ollama_placement() -> list[dict[str, Any]]:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/ps", timeout=10) as r:
            models = json.load(r).get("models", [])
        return [{"name": m.get("name"), "size": m.get("size"), "size_vram": m.get("size_vram")} for m in models]
    except Exception as exc:  # recorded, not hidden
        return [{"error": str(exc)}]


def run_step(report: dict[str, Any], name: str, fn: Callable[[], Any]) -> None:
    t0 = time.time()
    log.info("step %s: start", name)
    try:
        report["steps"][name] = {"status": "OK", "result": fn()}
    except Exception as exc:
        report["steps"][name] = {"status": "FAILED", "error": str(exc), "trace": traceback.format_exc()[-2000:]}
        log.error("step %s FAILED: %s", name, exc)
    report["steps"][name]["elapsed_s"] = round(time.time() - t0, 1)
    log.info("step %s: %s in %.0fs", name, report["steps"][name]["status"], report["steps"][name]["elapsed_s"])


def transcripts(dirs: list[Path]) -> dict[str, Any]:
    from ingest_memory import ingest_transcripts  # type: ignore[import-not-found]

    out: dict[str, Any] = {}
    for d in dirs:
        rep = ingest_transcripts(CHROMA_ROOT, None, None, transcript_root=d)
        out[d.name] = {k: rep.get(k) for k in ("turns_stored", "files_read", "sessions")} | {
            "secrets_scrubbed": rep.get("scrub", {}).get("total_replacements")
        }
    return out


def repo_documents() -> dict[str, Any]:
    from ingest_memory import ingest_pdfs  # type: ignore[import-not-found]

    reps = ingest_pdfs(CHROMA_ROOT)
    return {k: {"files_indexed": v.get("files_indexed"), "chunks_written": v.get("chunks_written"),
                "skipped": len(v.get("skipped", []))} for k, v in reps.items()}


def openai_math_corpus(deadline: datetime) -> dict[str, Any]:
    from anse.memory.document_store import DocumentStore

    store = DocumentStore(CHROMA_ROOT / "documents", "openai_math_preprints")
    files: list[Path] = [CLONE / "CONTENTS.md", CLONE / "README.md"]
    files += sorted((CLONE / "lean" / "docs").glob("*.md"))
    files += sorted((CLONE / "reasoning_traces").glob("*.pdf"))
    for folder in sorted(p for p in (CLONE / "preprints").iterdir() if p.is_dir()):
        files += sorted(folder.glob("*.pdf"))
    done = chunks = skipped = 0
    failures: list[dict[str, str]] = []
    stopped_at_deadline = False
    meta = {"corpus": "openai_math", "upstream": "github.com/openai/math@adc7f124", "status_note": "claims by another model, not results"}
    for path in files:
        if datetime.now(timezone.utc) >= deadline:
            stopped_at_deadline = True
            break
        try:
            if path.suffix.lower() == ".pdf":
                written = store.ingest_pdf(path, extra_metadata=meta)
            else:
                written = store.ingest_text_file(path, extra_metadata=meta)
        except Exception as exc:
            failures.append({"path": str(path), "error": str(exc)[:300]})
            continue
        if written:
            done += 1
            chunks += written
        else:
            skipped += 1
    return {"files_total": len(files), "files_indexed_now": done, "already_indexed": skipped,
            "chunks_written": chunks, "failures": failures[:50], "n_failures": len(failures),
            "stopped_at_deadline": stopped_at_deadline, "collection_count": store.count()}


def retrieval_checks() -> dict[str, Any]:
    import chromadb

    from anse.memory.document_store import DocumentStore
    from anse.memory.ollama_embeddings import OllamaEmbeddingFunction

    checks: dict[str, Any] = {}
    store = DocumentStore(CHROMA_ROOT / "documents", "openai_math_preprints")
    hits = store.query("zero-free half-plane seven eighths quasi-Riemann hypothesis", n_results=3)
    checks["openai_math_preprints"] = {
        "top_sources": [h["metadata"].get("source_path", "")[-90:] for h in hits],
        "pass": any("Quasi-Riemann" in h["metadata"].get("source_path", "") for h in hits),
    }
    client = chromadb.PersistentClient(path=str(CHROMA_ROOT / "transcripts"))
    names = [c.name for c in client.list_collections()]
    checks["transcript_collections"] = names
    if "claude_code_sessions" in names:
        col = client.get_collection("claude_code_sessions", embedding_function=OllamaEmbeddingFunction())
        res = col.query(query_texts=["dyadic triangular Hilbert constant exact witness 5/2"], n_results=3)
        docs = res.get("documents", [[]])[0]
        checks["claude_code_sessions"] = {"count": col.count(), "top_snippets": [d[:120] for d in docs],
                                          "pass": any("5/2" in d or "dyadic" in d for d in docs)}
    return checks


def main() -> int:
    p = argparse.ArgumentParser(description="overnight LTM ingest under the T4 lease")
    p.add_argument("--date", required=True)
    p.add_argument("--deadline-utc", default="04:40")
    p.add_argument("--repass-utc", default="04:25")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    now = datetime.now(timezone.utc)
    deadline = at_utc(args.deadline_utc, now)
    repass = at_utc(args.repass_utc, now)
    report: dict[str, Any] = {"date": args.date, "started_utc": now.isoformat(), "deadline_utc": deadline.isoformat(),
                              "chroma_root": str(CHROMA_ROOT), "steps": {}}
    out = REPO / "results" / "ltm_ingest" / f"night_{args.date}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dirs = sorted(d for d in PROJECTS.glob("-home-callensxavier-gmail-com-AutoevolveAI*") if d.is_dir())
    ttl = int((deadline - now).total_seconds()) + 900
    with gpu_lease(HOLDER, "night LTM ingest: transcripts + documents + openai/math corpus", ttl_s=ttl, timeout_s=3600):
        run_step(report, "transcripts_all_project_dirs", lambda: transcripts(dirs))
        report["ollama_after_first_embed"] = ollama_placement()
        run_step(report, "repo_documents", repo_documents)
        run_step(report, "openai_math_corpus", lambda: openai_math_corpus(min(deadline, repass)))
        wait = (repass - datetime.now(timezone.utc)).total_seconds()
        if 0 < wait < 8 * 3600:
            out.write_text(json.dumps(report, indent=2, default=str) + "\n")
            log.info("sleeping %.0f s until the transcript re-pass", wait)
            time.sleep(wait)
        run_step(report, "transcripts_repass_this_session", lambda: transcripts([THIS_SESSION_DIR]))
        if datetime.now(timezone.utc) < deadline:
            run_step(report, "openai_math_corpus_resume", lambda: openai_math_corpus(deadline))
        run_step(report, "retrieval_checks", retrieval_checks)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["all_ok"] = all(s["status"] == "OK" for s in report["steps"].values())
    out.write_text(json.dumps(report, indent=2, default=str) + "\n")
    log.info("wrote %s (all_ok=%s)", out, report["all_ok"])
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
