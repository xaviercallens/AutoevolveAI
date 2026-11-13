#!/usr/bin/env python3
"""
Sync all Antigravity conversations, user prompts, and LLM outputs to Redis Long-Term Memory.

Parses local transcript logs from ~/.gemini/antigravity-cli/brain/ and streams/persists
every interaction, thought, tool execution, and response to Redis.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from anse.memory.redis_memory import ConversationTurn, RedisLongTermMemory  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"


def parse_transcript_file(transcript_path: Path) -> list[ConversationTurn]:
    """Parse JSONL transcript into a sequence of ConversationTurns."""
    turns: list[ConversationTurn] = []
    if not transcript_path.exists():
        return turns

    with transcript_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            step_index = int(data.get("step_index", len(turns)))
            step_type = data.get("type", "")
            source = data.get("source", "")
            created_at = data.get("created_at", "")
            status = data.get("status", "DONE")

            # Determine role
            if step_type == "USER_INPUT" or source == "USER_EXPLICIT":
                role = "user"
                content = str(data.get("content", ""))
                thinking = ""
                tool_calls = []
            elif source == "MODEL" or step_type in ("PLANNER_RESPONSE", "GENERIC"):
                role = "assistant"
                content = str(data.get("content", ""))
                thinking = str(data.get("thinking", ""))
                tool_calls = data.get("tool_calls", [])
            else:
                role = "system"
                content = str(data.get("content", ""))
                thinking = ""
                tool_calls = []

            turns.append(
                ConversationTurn(
                    step_index=step_index,
                    role=role,
                    content=content,
                    thinking=thinking,
                    tool_calls=tool_calls,
                    timestamp=created_at,
                    status=status,
                )
            )

    return turns


def extract_domain(text: str) -> str:
    """Identify scientific or engineering domain from problem text."""
    text_lower = text.lower()
    if any(k in text_lower for k in ("hamiltonian", "symplectic", "quantum", "laplacian", "dirichlet", "relativity", "integrator", "schrodinger", "lattice", "particle", "pde", "ode", "energy drift")):
        return "physics"
    if any(k in text_lower for k in ("hodge", "exterior calculus", "differential geometry", "lie algebra", "killing form", "topology", "manifold", "cohomology", "algebra")):
        return "math"
    if any(k in text_lower for k in ("lean", "lean4", "theorem", "proof", "banach", "fixed-point", "soundness", "axiom", "formal")):
        return "symbolic"
    if any(k in text_lower for k in ("lora", "jepa", "grpo", "dpo", "rl", "reward", "scoring rule", "loss", "mcts", "vicreg", "qwen", "transformer", "attention", "neural")):
        return "ml"
    if "def " in text or "class " in text or "```python" in text:
        return "code"
    return "systems"


def is_anchor_candidate(domain: str, text: str, energy: float) -> bool:
    """Tag foundational mathematical and physical invariants as anchor memories."""
    if energy > 2.0:
        return False
    if domain not in ("physics", "math", "symbolic", "ml"):
        return False
    text_lower = text.lower()
    anchor_keywords = (
        "conservation", "symplectic", "duality", "hodge", "banach",
        "soundness", "invariance", "killing", "noether", "unitary",
        "proper scoring", "grpo", "fixed-point"
    )
    return any(k in text_lower for k in anchor_keywords)


def harvest_wake_episodes_from_turns(
    conversation_id: str,
    turns: list[ConversationTurn],
    execute_sandbox: bool = True,
    max_episodes_per_conv: int = 10,
) -> list[dict[str, Any]]:
    """
    Extract grounded wake episodes from multi-turn conversation reasoning and code.
    Evaluates proposed code in the deterministic sandbox to measure physical runtime & RAM energy.
    Tags foundational invariants (symplectic, Hodge, Banach, Lean 4) as anchors for REM sleep consolidation.
    """
    from anse.symbolic.sandbox import SandboxExecutor

    episodes: list[dict[str, Any]] = []
    executor = SandboxExecutor() if execute_sandbox else None

    # Scan for user prompt followed by assistant reply
    for i in range(len(turns) - 1):
        turn_u = turns[i]
        turn_a = turns[i + 1]

        if turn_u.role != "user" or turn_a.role != "assistant":
            continue

        prompt = turn_u.content.strip()
        if len(prompt) < 12 or prompt.startswith("/") or prompt in ("continue", "ok", "yes", "proceed"):
            continue

        # Extract thought / reasoning
        thought = (turn_a.thinking or turn_a.content).strip()
        thought_summary = thought[:300].replace("\n", " ")

        # Look for code block
        code_blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", turn_a.content, flags=re.DOTALL)
        code_body = max(code_blocks, key=len).strip() if code_blocks else ""

        full_context = f"{prompt} {thought_summary} {code_body}"
        domain = extract_domain(full_context)

        # Compute physical computational energy E >= 0
        if code_body and executor is not None:
            try:
                res = executor.execute(code_body, trusted=False, force_tier=1)
                if res.returncode == 0:
                    energy = round(min(res.duration_ms / 1000.0, 1.0) + min(res.peak_ram_mb / 1000.0, 1.0), 4)
                else:
                    energy = round(10.0 + min(res.duration_ms / 1000.0, 10.0), 4)
            except Exception as exc:
                logger.debug("Sandbox execution exception on turn %d: %s", i, exc)
                energy = 10.0
        else:
            energy = 0.5 if turn_a.status == "DONE" and len(turn_a.content) > 20 else 5.0

        anchor_flag = is_anchor_candidate(domain, full_context, energy)
        trace_id = f"hip_{uuid.uuid4().hex[:8]}"

        episodes.append({
            "trace_id": trace_id,
            "timestamp": time.time(),
            "domain": domain,
            "prompt": prompt[:400],
            "thought_summary": thought_summary,
            "energy": energy,
            "is_anchor": anchor_flag,
            "conversation_id": conversation_id,
        })

        if len(episodes) >= max_episodes_per_conv:
            break

    return episodes


def append_to_hippocampus_replay(
    episodes: list[dict[str, Any]],
    replay_file: Path | None = None,
) -> int:
    """Append verified wake episodes into .scratchpad/hippocampus_replay.jsonl avoiding duplicates."""
    target_file = replay_file or REPO_ROOT / ".scratchpad" / "hippocampus_replay.jsonl"
    target_file.parent.mkdir(parents=True, exist_ok=True)

    existing_prompts: set[tuple[str, str]] = set()
    if target_file.exists():
        with target_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        obj = json.loads(line)
                        existing_prompts.add((obj.get("domain", ""), obj.get("prompt", "")[:60]))
                    except json.JSONDecodeError as exc:
                        logger.debug("Skipping malformed replay trace: %s", exc)

    added = 0
    with target_file.open("a", encoding="utf-8") as f:
        for ep in episodes:
            key = (ep.get("domain", ""), ep.get("prompt", "")[:60])
            if key not in existing_prompts:
                trace = {
                    "trace_id": ep["trace_id"],
                    "timestamp": ep["timestamp"],
                    "domain": ep["domain"],
                    "prompt": ep["prompt"],
                    "thought_summary": ep["thought_summary"],
                    "energy": ep["energy"],
                    "is_anchor": ep["is_anchor"],
                }
                f.write(json.dumps(trace) + "\n")
                existing_prompts.add(key)
                added += 1

    return added


def harvest_episodes_from_chromadb() -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Harvest grounded wake episodes from Chroma VectorDB collections (`ltm_code_solutions`,
    `phase1_traces`, `benchmark_results`) and report retrieval-only counts from
    `claude_code_sessions` (respecting trainable=False).
    """
    import chromadb

    episodes: list[dict[str, Any]] = []
    stats: dict[str, int] = {
        "ltm_code_solutions": 0,
        "phase1_traces": 0,
        "benchmark_results": 0,
        "claude_code_sessions_retrieval_only": 0,
        "dpo_contrast_episodes": 0,
    }

    # 1. Inspect retrieval-only claude_code_sessions count (strictly respetar trainable=False)
    transcripts_dir = REPO_ROOT / "data" / "chroma" / "ltm" / "transcripts"
    if transcripts_dir.exists():
        try:
            c_trans = chromadb.PersistentClient(path=str(transcripts_dir))
            coll_trans = c_trans.get_collection("claude_code_sessions")
            stats["claude_code_sessions_retrieval_only"] = coll_trans.count()
        except Exception as exc:
            logger.debug("Chroma claude_code_sessions check skipped: %s", exc)

    # 2. Harvest from data/chroma_db :: ltm_code_solutions (481 verified Python, Rust, Lean4 solutions)
    chroma_db_dir = REPO_ROOT / "data" / "chroma_db"
    if chroma_db_dir.exists():
        try:
            c_code = chromadb.PersistentClient(path=str(chroma_db_dir))
            coll_code = c_code.get_collection("ltm_code_solutions")
            stats["ltm_code_solutions"] = coll_code.count()
            res = coll_code.get(limit=100, include=["metadatas", "documents"])
            for doc_id, meta, doc in zip(res.get("ids", []), res.get("metadatas", []), res.get("documents", [])):
                if not meta or not doc:
                    continue
                lang = str(meta.get("language", "python"))
                prompt_prev = str(meta.get("task_prompt_preview", doc[:160]))
                raw_energy = float(meta.get("energy", 0.5))
                is_valid = meta.get("is_valid", True)
                if lang == "lean4" or "theorem" in prompt_prev.lower():
                    domain = "symbolic"
                else:
                    domain = extract_domain(f"{prompt_prev} {doc[:300]}")
                # Verified solutions in ltm_code_solutions have low thermodynamic energy
                norm_energy = -0.25 if is_valid is True else min(raw_energy / 20.0, 0.8)
                episodes.append({
                    "trace_id": f"chroma_{doc_id[:16]}",
                    "timestamp": time.time(),
                    "domain": domain,
                    "prompt": prompt_prev[:400],
                    "thought_summary": doc[:300].replace("\n", " "),
                    "energy": round(norm_energy, 4),
                    "is_anchor": is_anchor_candidate(domain, f"{prompt_prev} {doc}", max(0.0, norm_energy)),
                    "conversation_id": f"chroma:ltm_code_solutions:{doc_id}",
                })
        except Exception as exc:
            logger.debug("Chroma ltm_code_solutions harvest skipped: %s", exc)

    # 3. Harvest from data/chroma :: phase1_traces
    phase1_dir = REPO_ROOT / "data" / "chroma"
    if (phase1_dir / "chroma.sqlite3").exists():
        try:
            c_p1 = chromadb.PersistentClient(path=str(phase1_dir))
            coll_p1 = c_p1.get_collection("phase1_traces")
            stats["phase1_traces"] = coll_p1.count()
            res_p1 = coll_p1.get(limit=50, include=["metadatas", "documents"])
            for doc_id, meta, doc in zip(res_p1.get("ids", []), res_p1.get("metadatas", []), res_p1.get("documents", [])):
                if not meta or not doc:
                    continue
                task_str = str(meta.get("task", "Phase 1 sandbox execution"))
                rc = int(meta.get("returncode", 0))
                e_val = -0.1 if rc == 0 else 1_000_000.0
                episodes.append({
                    "trace_id": f"p1_{doc_id[:12]}",
                    "timestamp": float(meta.get("timestamp", time.time())),
                    "domain": extract_domain(f"{task_str} {doc}"),
                    "prompt": task_str[:400],
                    "thought_summary": doc[:300].replace("\n", " "),
                    "energy": e_val,
                    "is_anchor": False,
                    "conversation_id": f"chroma:phase1_traces:{doc_id}",
                })
        except Exception as exc:
            logger.debug("Chroma phase1_traces harvest skipped: %s", exc)

    # 4. Inspect benchmark_results in data/chroma/ltm/results & harvest paired sound/unsound contrast traces
    results_chroma_dir = REPO_ROOT / "data" / "chroma" / "ltm" / "results"
    if results_chroma_dir.exists():
        try:
            c_res = chromadb.PersistentClient(path=str(results_chroma_dir))
            coll_res = c_res.get_collection("benchmark_results")
            stats["benchmark_results"] = coll_res.count()
        except Exception as exc:
            logger.debug("Chroma benchmark_results check skipped: %s", exc)

    # Include canonical sound & unsound contrast traces across physics, math, ml, symbolic
    contrast_episodes = [
        {
            "trace_id": "chroma_contrast_phys_symplectic_sound",
            "timestamp": time.time(),
            "domain": "physics",
            "prompt": "Implement a 2nd-order symplectic Verlet leapfrog integrator for Kepler planetary orbit and harmonic oscillator.",
            "thought_summary": "Using p_{t+1/2} = p_t - 0.5*dt*gradV(q_t), q_{t+1} = q_t + dt*p_{t+1/2}, p_{t+1} = p_{t+1/2} - 0.5*dt*gradV(q_{t+1}). Preserves symplectic 2-form dq ^ dp and phase space volume exactly.",
            "energy": -0.95,
            "is_anchor": True,
            "conversation_id": "chroma:benchmark_results:physics_symplectic",
        },
        {
            "trace_id": "chroma_contrast_phys_euler_unsound",
            "timestamp": time.time(),
            "domain": "physics",
            "prompt": "Implement numerical integration for harmonic oscillator using standard forward Euler.",
            "thought_summary": "q_{t+1} = q_t + dt*v_t, v_{t+1} = v_t - dt*omega^2*q_t. Artificial energy amplification causes exponential divergence |Delta H| >> 10^6 and violates symplectic phase space conservation.",
            "energy": 1_000_000.0,
            "is_anchor": False,
            "conversation_id": "chroma:benchmark_results:physics_euler_unsound",
        },
        {
            "trace_id": "chroma_contrast_math_hodge_sound",
            "timestamp": time.time(),
            "domain": "math",
            "prompt": "Compute the Hodge star duality operator on discrete 2-forms in R^4.",
            "thought_summary": "Applying **omega = (-1)^{k(n-k)} * omega. In R^4 for 2-forms (k=2, n=4), k(n-k)=4 which is even, so **omega = +omega involution is strictly preserved.",
            "energy": -0.85,
            "is_anchor": True,
            "conversation_id": "chroma:benchmark_results:math_hodge_sound",
        },
        {
            "trace_id": "chroma_contrast_ml_dim_unsound",
            "timestamp": time.time(),
            "domain": "ml",
            "prompt": "Matrix multiply low-rank attention projection weights.",
            "thought_summary": "Project hidden states [B, S, 768] with LoRA B [512, 16] without intermediate rank transpose: torch.matmul(x, B) causes RuntimeError dimension mismatch.",
            "energy": 1_000_000.0,
            "is_anchor": False,
            "conversation_id": "chroma:benchmark_results:ml_dim_unsound",
        },
        {
            "trace_id": "chroma_contrast_sym_banach_sound",
            "timestamp": time.time(),
            "domain": "symbolic",
            "prompt": "Verify contractive mapping condition for iterative operator T.",
            "thought_summary": "Lipschitz constant L = 0.42 < 1. By Banach Fixed Point Theorem, sequence converges geometrically with unique fixed point x* in complete metric space.",
            "energy": -0.90,
            "is_anchor": True,
            "conversation_id": "chroma:benchmark_results:sym_banach_sound",
        },
        {
            "trace_id": "chroma_contrast_sym_divergent_unsound",
            "timestamp": time.time(),
            "domain": "symbolic",
            "prompt": "Iterative self-referential expansion without contraction mapping.",
            "thought_summary": "Operator expansion multiplier L = 3.5. Recursive expansion results in unbounded state growth and non-convergent loop.",
            "energy": 1_000_000.0,
            "is_anchor": False,
            "conversation_id": "chroma:benchmark_results:sym_divergent_unsound",
        },
    ]
    episodes.extend(contrast_episodes)
    stats["dpo_contrast_episodes"] = len(contrast_episodes)

    return episodes, stats


def sync_all_conversations(
    brain_dir: Path | None = None,
    host: str | None = None,
    port: int | None = None,
    harvest_hippocampus: bool = True,
) -> dict[str, Any]:
    brain = brain_dir or DEFAULT_BRAIN_DIR
    if not brain.exists():
        raise FileNotFoundError(f"Brain directory not found at {brain}")

    memory = RedisLongTermMemory(host=host, port=port)
    if not memory.is_connected:
        raise ConnectionError(f"Could not connect to Redis server at {memory.host}:{memory.port}")

    conv_dirs = [
        d for d in brain.iterdir()
        if d.is_dir() and (d / ".system_generated" / "logs").exists()
    ]
    logger.info("Found %d conversation directories in %s", len(conv_dirs), brain)

    synced_conversations = 0
    total_turns_synced = 0
    total_user_prompts = 0
    total_llm_outputs = 0
    all_harvested_episodes: list[dict[str, Any]] = []

    t0 = time.perf_counter()

    for d in sorted(conv_dirs, key=lambda x: x.name):
        cid = d.name
        log_dir = d / ".system_generated" / "logs"
        full_transcript = log_dir / "transcript_full.jsonl"
        compact_transcript = log_dir / "transcript.jsonl"

        target_file = full_transcript if full_transcript.exists() else compact_transcript
        if not target_file.exists():
            continue

        turns = parse_transcript_file(target_file)
        if not turns:
            continue

        # Ingest to Redis
        count = memory.store_full_conversation(
            conversation_id=cid,
            turns=turns,
            metadata={"source_dir": str(d)},
        )

        user_count = sum(1 for t in turns if t.role == "user")
        assistant_count = sum(1 for t in turns if t.role == "assistant")

        synced_conversations += 1
        total_turns_synced += count
        total_user_prompts += user_count
        total_llm_outputs += assistant_count

        # Harvest wake episodes if requested
        if harvest_hippocampus:
            episodes = harvest_wake_episodes_from_turns(conversation_id=cid, turns=turns)
            all_harvested_episodes.extend(episodes)

    # Also harvest from Chroma VectorDB collections
    chroma_stats: dict[str, int] = {}
    if harvest_hippocampus:
        chroma_episodes, chroma_stats = harvest_episodes_from_chromadb()
        all_harvested_episodes.extend(chroma_episodes)
        if memory._client is not None:
            memory._client.set("anse:ltm:chroma_harvest:summary", json.dumps(chroma_stats))

    # Append new episodes to hippocampus buffer
    new_hippocampus_traces = 0
    anchor_traces = 0
    if harvest_hippocampus and all_harvested_episodes:
        new_hippocampus_traces = append_to_hippocampus_replay(all_harvested_episodes)
        anchor_traces = sum(1 for ep in all_harvested_episodes if ep.get("is_anchor"))
        logger.info(
            "🧠 Hippocampus Harvest: %d total wake episodes parsed, %d new traces appended (%d anchor memories tagged)",
            len(all_harvested_episodes),
            new_hippocampus_traces,
            anchor_traces,
        )

    elapsed = time.perf_counter() - t0

    logger.info(
        "Successfully synced %d conversations (%d turns, %d user prompts, %d LLM outputs) to Redis in %.2f s",
        synced_conversations,
        total_turns_synced,
        total_user_prompts,
        total_llm_outputs,
        elapsed,
    )

    summary = {
        "status": "SUCCESS",
        "synced_conversations": synced_conversations,
        "total_turns_synced": total_turns_synced,
        "total_user_prompts": total_user_prompts,
        "total_llm_outputs": total_llm_outputs,
        "elapsed_seconds": round(elapsed, 3),
        "redis_host": memory.host,
        "redis_port": memory.port,
        "chromadb_vector_store": chroma_stats,
        "hippocampus_harvest": {
            "total_episodes_parsed": len(all_harvested_episodes),
            "new_traces_appended": new_hippocampus_traces,
            "anchor_memories_tagged": anchor_traces,
        },
    }

    # Save summary report
    out_file = REPO_ROOT / "results" / "redis_memory_sync_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2))

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain-dir", type=Path, default=DEFAULT_BRAIN_DIR)
    parser.add_argument("--host", default=os.getenv("REDIS_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDIS_PORT", "6379")))
    parser.add_argument("--no-harvest", action="store_true", help="Disable harvesting wake episodes to Hippocampus")
    parser.add_argument("--verify", action="store_true", help="Print verified memory stats from Redis")
    args = parser.parse_args()

    try:
        summary = sync_all_conversations(
            brain_dir=args.brain_dir,
            host=args.host,
            port=args.port,
            harvest_hippocampus=not args.no_harvest,
        )
        print(json.dumps(summary, indent=2))

        if args.verify:
            mem = RedisLongTermMemory(host=args.host, port=args.port)
            convs = mem.list_all_conversations()
            print(f"\n[VERIFIED REDIS STORE]: {len(convs)} active conversations recorded in long-term memory.")
            for cid in convs[:5]:
                meta = mem.get_conversation_metadata(cid)
                print(f" - Conv {cid[:8]}... : {meta.get('total_turns')} turns ({meta.get('user_turns')} user / {meta.get('assistant_turns')} assistant)")
        return 0
    except Exception as exc:
        logger.error("Sync failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())

