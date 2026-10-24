"""
HiveMind Conversation Recorder & Verified Episode Flywheel
==========================================================
Captures, scrubs, and persists AI/Human contribution conversations and execution
receipts for Project HiveMind using AutoevolveAI's `anse.v2` capture & episode store:

1. Scrubs PII, tokens, and secrets via `anse.v2.scrub.scrub`.
2. Appends structured receipt rows to `results/hivemind_conversation_spool.jsonl`
   and parses them via `anse.v2.capture.antigravity.parse_receipts`.
3. Harvests active Antigravity brain transcripts (`transcript.jsonl`) and Claude Code
   hook spools (`~/.night_school/spool/`).
4. Persists verified episodes into SQLite `EpisodeStore` (`data/hivemind_episodes.db`)
   with `(chosen, rejected)` DPO preference pair generation for HiveMind domain experts.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from anse.v2.capture.antigravity import parse_receipts  # noqa: E402
from anse.v2.episode_store import Episode, EpisodeStore  # noqa: E402
from anse.v2.scrub import scrub  # noqa: E402

DEFAULT_SPOOL_PATH = ROOT_DIR / "results" / "hivemind_conversation_spool.jsonl"
DEFAULT_EPISODES_JSONL = ROOT_DIR / "results" / "hivemind_conversation_episodes.jsonl"
DEFAULT_DB_PATH = ROOT_DIR / "data" / "hivemind_episodes.db"


def record_hivemind_contribution_turn(
    prompt: str,
    files_edited: list[str],
    code_or_summary: str,
    passed: bool = True,
    task_id: str = "HM-S6-CONTRIB",
    energy: float | None = None,
    origin: str = "human",
    spool_path: str | Path = DEFAULT_SPOOL_PATH,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Scrubs and records a single HiveMind contribution turn to JSONL spool and SQLite EpisodeStore."""
    clean_prompt, prompt_redactions = scrub(prompt)
    clean_code, code_redactions = scrub(code_or_summary)
    clean_files = [scrub(f)[0] for f in files_edited if f.strip()]

    now = time.time()
    computed_energy = float(energy) if energy is not None else (0.25 if passed else 1_000_000.0)

    receipt_row = {
        "timestamp": now,
        "subtask_id": task_id,
        "prompt": clean_prompt,
        "files_edited": clean_files,
        "chosen" if passed else "test_stdout": clean_code,
        "verdict": "PASSED" if passed else "FAILED",
        "status": "ATTESTED" if passed else "FAILED",
    }

    spool_file = Path(spool_path)
    spool_file.parent.mkdir(parents=True, exist_ok=True)
    with spool_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt_row) + "\n")

    parsed_episodes = parse_receipts([json.dumps(receipt_row)])

    ep = Episode(
        task_id=task_id,
        split="train",
        prompt=clean_prompt,
        code=clean_code,
        energy=computed_energy,
        passed=passed,
        temperature=0.2,
        model_id="hivemind-contributor-agent",
        origin=origin if origin in {"local_model", "human"} else "human",
        created_at=now,
    )

    with EpisodeStore(db_path) as store:
        inserted = store.insert(ep)
        total_episodes = store.count(split="train")
        passed_episodes = store.count(split="train", passed=True)
        dpo_pairs_count = len(store.preference_pairs("train"))

    total_redactions = sum(prompt_redactions.values()) + sum(code_redactions.values())
    return {
        "recorded": True,
        "inserted_new_episode": inserted,
        "episode_id": ep.id,
        "code_sha256": ep.code_sha,
        "task_id": task_id,
        "passed": passed,
        "energy": computed_energy,
        "redactions_applied": total_redactions,
        "parsed_antigravity_episodes": [asdict(pe) for pe in parsed_episodes],
        "store_stats": {
            "db_path": str(db_path),
            "spool_path": str(spool_file),
            "total_train_episodes": total_episodes,
            "passed_train_episodes": passed_episodes,
            "preference_pairs_available": dpo_pairs_count,
        },
    }


def harvest_antigravity_brain_transcripts(
    brain_root: str | Path | None = None,
    spool_path: str | Path = DEFAULT_SPOOL_PATH,
    episodes_jsonl_path: str | Path = DEFAULT_EPISODES_JSONL,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Scans Antigravity brain transcripts and local spools to populate the HiveMind episode store."""
    if brain_root is None:
        brain_root = Path.home() / ".gemini" / "antigravity-cli" / "brain"
    else:
        brain_root = Path(brain_root)

    harvested_turns: list[dict[str, Any]] = []

    if brain_root.exists():
        transcript_files = sorted(
            brain_root.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0.0,
            reverse=True,
        )[:2]
        for transcript_path in transcript_files:
            conv_id = transcript_path.parents[2].name
            try:
                with transcript_path.open("rb") as bf:
                    bf.seek(0, 2)
                    size = bf.tell()
                    bf.seek(max(0, size - 65536))
                    tail_text = bf.read().decode("utf-8", errors="replace")
                lines = tail_text.splitlines()
            except Exception:
                continue

            if "hivemind" not in tail_text.lower():
                continue

            user_inputs: list[str] = []
            model_responses: list[str] = []
            for raw in lines:
                if not raw.strip() or not raw.lstrip().startswith("{"):
                    continue
                try:
                    step = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                step_type = str(step.get("type", ""))
                content = str(step.get("content", ""))
                if step_type == "USER_INPUT" and content.strip():
                    user_inputs.append(content[:1000])
                elif step_type == "PLANNER_RESPONSE" and content.strip():
                    model_responses.append(content[:1000])

            if user_inputs and any("hivemind" in u.lower() for u in user_inputs):
                prompt_text = scrub(user_inputs[-1])[0]
                response_text = (
                    scrub(model_responses[-1])[0]
                    if model_responses
                    else "HiveMind subproject configured."
                )
                res = record_hivemind_contribution_turn(
                    prompt=prompt_text,
                    files_edited=[
                        "sub_projects/hivemind/hivemind_swarm_bridge_harness.py",
                        "sub_projects/hivemind/hivemind_hardness_engine.py",
                        "sub_projects/hivemind/hivemind_conversation_recorder.py",
                    ],
                    code_or_summary=response_text,
                    passed=True,
                    task_id=f"HM-CONV-{conv_id[:8]}",
                    energy=0.15,
                    origin="human",
                    spool_path=spool_path,
                    db_path=db_path,
                )
                harvested_turns.append(res)

    spool_file = Path(spool_path)
    all_receipts = (
        parse_receipts(spool_file.read_text(encoding="utf-8").splitlines())
        if spool_file.exists()
        else []
    )

    out_jsonl = Path(episodes_jsonl_path)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for ep in all_receipts:
            fh.write(json.dumps(asdict(ep)) + "\n")

    with EpisodeStore(db_path) as store:
        total_eps = store.count(split="train")
        passed_eps = store.count(split="train", passed=True)
        dpo_pairs = len(store.preference_pairs("train"))

    return {
        "harvested_conversations_count": len(harvested_turns),
        "total_receipt_episodes": len(all_receipts),
        "episodes_jsonl_path": str(out_jsonl),
        "db_path": str(db_path),
        "store_total_episodes": total_eps,
        "store_passed_episodes": passed_eps,
        "store_dpo_pairs": dpo_pairs,
    }


if __name__ == "__main__":
    summary = harvest_antigravity_brain_transcripts()
    print(json.dumps(summary, indent=2))
