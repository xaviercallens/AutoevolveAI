#!/usr/bin/env python3
"""Put run two into long-term memory, then check it can be retrieved.

  1. Redis `anse:ltm:llm_calls`: backfill the run's prover calls (the runners
     call Ollama directly, so APIExtractor never pushed them), same schema
     (the raw JSONL line), de-duplicated against the list.
  2. Chroma `llm_calls`: scripts/ingest_llm_calls.py over every call log.
  3. Chroma `literature`: the paper, LL.md, the retrain summary.
  4. Conversation LTM: this project's transcripts only (scoped root).
  5. Retrieval positive control: a query about the #exit gate hole must return
     an LL.md chunk.
Embeddings run on the T4 via Ollama, so the whole job holds the GPU lease.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import gpu_lease  # noqa: E402

from anse.memory.document_store import DocumentStore  # noqa: E402

PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
CALL_LOG = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/call_logs/master_math_run2.jsonl")
DOCS = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/chroma/ltm/documents")
TRANSCRIPTS = Path.home() / ".claude/projects/-home-callensxavier-gmail-com-AutoevolveAI"
OUT = REPO / "results" / "master_math_run2" / "ltm_ingest.json"


def redis_backfill() -> dict:
    import redis

    r = redis.Redis.from_url("redis://localhost:6379/0", socket_timeout=10)
    have = set(r.lrange("anse:ltm:llm_calls", 0, -1))
    lines = [ln for ln in CALL_LOG.read_text().splitlines() if ln.strip()]
    new = [ln for ln in lines if ln.encode() not in have]
    for ln in new:
        r.lpush("anse:ltm:llm_calls", ln)
    return {"call_log_lines": len(lines), "pushed": len(new), "list_len": r.llen("anse:ltm:llm_calls")}


def main() -> int:
    literature_only = "--literature-only" in sys.argv
    report: dict = {}
    if OUT.exists() and literature_only:
        report = json.loads(OUT.read_text())
    with gpu_lease("autoevolveai-ltm", "LTM ingest master-math run two", ttl_s=3600, timeout_s=3 * 3600):
        if not literature_only:
            report["redis"] = redis_backfill()
            print(json.dumps(report), flush=True)
            rc = subprocess.run([PY, str(REPO / "scripts" / "ingest_llm_calls.py")], cwd=str(REPO)).returncode
            report["chroma_llm_calls_rc"] = rc
        store = DocumentStore(DOCS, "literature")
        before = store.count()
        chunks, superseded = {}, {}
        for p in [REPO / "papers/master_math_run2/master_math_run2.tex", REPO / "LL.md",
                  REPO / "results/night_retrain_20260927/summary.json"]:
            # a corrected document must not leave its retracted version retrievable
            superseded[p.name] = store.supersede(p)
            chunks[p.name] = store.ingest_text_file(p, extra_metadata={"topic": "master_math_run2"})
        report["literature"] = {"before": before, "after": store.count(), "chunks": chunks,
                                "superseded": superseded}
        print(json.dumps(report), flush=True)
        if not literature_only:
            rc = subprocess.run([PY, str(REPO / "scripts" / "ingest_memory.py"), "--transcripts",
                                 "--transcript-root", str(TRANSCRIPTS)], cwd=str(REPO)).returncode
            report["transcripts_rc"] = rc
        hits = store.query("proof ending in #exit suppressed the axiom report and scored clean", n_results=3)
        report["retrieval_control"] = [{"distance": round(h["distance"], 3),
                                        "source": str(h.get("metadata", {}).get("source", ""))[-60:],
                                        "text": h["document"][:120]} for h in hits]
        report["retrieval_control_ok"] = any("#exit" in h["document"] for h in hits)
    OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0 if report["retrieval_control_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
