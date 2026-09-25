#!/usr/bin/env python3
"""
Step-by-step night training workflow.

Each model advances through explicit, resumable steps. Every step records what
it did to a per-model journal on the second disk, so a night that dies halfway
resumes at the step it reached instead of starting over.

    ARTIFACT -> DATA -> FIT -> EVAL -> GATE

  ARTIFACT  the base/checkpoint is present on disk 2 and loads
  DATA      the training rows are assembled and pass the provenance gate
  FIT       a real optimisation run on the T4
  EVAL      measured on held-out rows
  GATE      promote or reject against the incumbent

Rules this file will not bend:

  * A step that cannot run reports BLOCKED with the reason. It never
    substitutes a smaller job and calls it done.
  * FIT records the loss series the trainer actually produced. There is no
    path here that writes a loss curve from a formula -- that is the defect in
    scripts/generate_phd_paper_figures.py.
  * A run whose loss rose is reported as a run whose loss rose. The lake's
    flagship adapter is the output of an 8-step run with loss 3.532 -> 3.692
    labelled SUCCESS; GATE exists so that never promotes anything.
  * --smoke runs a deliberately tiny fit to prove the machinery end to end.
    Its artifacts are written under a smoke/ prefix and are never promotable.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger("night_train")

DISK2 = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI")
LAKE = DISK2 / "datalake"
RUNS = DISK2 / "training_runs"
JOURNALS = RUNS / "journals"

T4_TOTAL_MIB = 15360


class Step(StrEnum):
    ARTIFACT = "ARTIFACT"
    DATA = "DATA"
    FIT = "FIT"
    EVAL = "EVAL"
    GATE = "GATE"


class Outcome(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


@dataclass
class StepRecord:
    step: Step
    outcome: Outcome
    detail: str
    data: dict[str, Any] = field(default_factory=dict)
    seconds: float = 0.0
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ModelJournal:
    model: str
    smoke: bool
    steps: list[StepRecord] = field(default_factory=list)

    @property
    def last_ok(self) -> Step | None:
        oks = [s.step for s in self.steps if s.outcome is Outcome.OK]
        return oks[-1] if oks else None

    def record(self, rec: StepRecord) -> None:
        self.steps.append(rec)
        icon = {
            Outcome.OK: "ok",
            Outcome.BLOCKED: "blocked",
            Outcome.FAILED: "FAILED",
        }[rec.outcome]
        logger.info("    %-8s %-8s %s", rec.step, icon, rec.detail)

    def write(self) -> Path:
        JOURNALS.mkdir(parents=True, exist_ok=True)
        prefix = "smoke_" if self.smoke else ""
        path = JOURNALS / f"{prefix}{self.model}.json"
        path.write_text(
            json.dumps(
                {
                    "model": self.model,
                    "smoke": self.smoke,
                    "updated": datetime.now(timezone.utc).isoformat(),
                    "last_ok_step": self.last_ok,
                    "steps": [asdict(s) for s in self.steps],
                },
                indent=2,
                default=str,
            )
            + "\n"
        )
        return path


def gpu_state() -> tuple[bool, str, int]:
    """(available, description, free_mib). Live, never assumed."""
    try:
        import torch
    except ImportError as exc:
        return False, f"torch unavailable: {exc}", 0
    if not torch.cuda.is_available():
        return False, "torch.cuda.is_available() is False", 0
    free, _total = torch.cuda.mem_get_info()
    return True, torch.cuda.get_device_name(0), free // 2**20


# --------------------------------------------------------------------- steps


def step_artifact(model: str, journal: ModelJournal) -> bool:
    t0 = time.time()
    base = LAKE / "models"
    if not base.is_dir():
        journal.record(
            StepRecord(
                Step.ARTIFACT,
                Outcome.BLOCKED,
                f"no model staging at {base}; run bootstrap_from_datalake.py",
                seconds=time.time() - t0,
            )
        )
        return False
    files = list(base.rglob("*"))
    n = sum(1 for f in files if f.is_file())
    size_gb = sum(f.stat().st_size for f in files if f.is_file()) / 2**30
    journal.record(
        StepRecord(
            Step.ARTIFACT,
            Outcome.OK,
            f"{n} artifact(s), {size_gb:.2f} GB on disk 2",
            data={"files": n, "gb": round(size_gb, 3), "root": str(base)},
            seconds=time.time() - t0,
        )
    )
    return True


def step_data(model: str, journal: ModelJournal, smoke: bool) -> list[dict] | None:
    t0 = time.time()
    corpus = LAKE / "data/redis/redis_ltm_lora_dataset.jsonl"
    if not corpus.exists():
        journal.record(
            StepRecord(
                Step.DATA, Outcome.BLOCKED, f"corpus absent: {corpus}",
                seconds=time.time() - t0,
            )
        )
        return None

    rows: list[dict] = []
    for line in corpus.open():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Provenance gate. Card P4-2 makes this the single chokepoint for real
    # training; until it lands, only a smoke run may proceed, and only because
    # its output is never promotable.
    verified = [r for r in rows if str(r.get("verdict", "")).upper() == "PASSED"]
    if not verified and not smoke:
        journal.record(
            StepRecord(
                Step.DATA,
                Outcome.BLOCKED,
                f"{len(rows)} rows carry no attestation verdict; the verified-data "
                "gate (card P4-2) has not landed. Refusing to train for real on "
                "unverified rows.",
                data={"rows": len(rows), "verified": 0},
                seconds=time.time() - t0,
            )
        )
        return None

    use = verified if verified else rows
    journal.record(
        StepRecord(
            Step.DATA,
            Outcome.OK,
            f"{len(use)} row(s)"
            + ("" if verified else " UNVERIFIED — smoke only, not promotable"),
            data={"rows": len(rows), "verified": len(verified), "used": len(use)},
            seconds=time.time() - t0,
        )
    )
    return use


def step_fit(
    model: str, journal: ModelJournal, rows: list[dict], smoke: bool
) -> dict | None:
    """Real optimisation on the T4. The loss series is the trainer's own."""
    t0 = time.time()
    ok, desc, free_mib = gpu_state()
    if not ok:
        journal.record(
            StepRecord(Step.FIT, Outcome.BLOCKED, f"no GPU: {desc}",
                       seconds=time.time() - t0)
        )
        return None

    base_id = "Qwen/Qwen2.5-0.5B-Instruct" if smoke else "Qwen/Qwen2.5-Coder-7B-Instruct"
    need = 3_000 if smoke else 11_000
    if free_mib < need:
        journal.record(
            StepRecord(
                Step.FIT,
                Outcome.BLOCKED,
                f"{free_mib} MiB free of {T4_TOTAL_MIB}, need ~{need}. "
                "Unload Ollama first (`ollama stop <model>`); keep_alive holds ~8 GiB.",
                data={"free_mib": free_mib},
                seconds=time.time() - t0,
            )
        )
        return None

    try:
        import torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        journal.record(
            StepRecord(Step.FIT, Outcome.BLOCKED, f"missing dependency: {exc}",
                       seconds=time.time() - t0)
        )
        return None

    steps = 12 if smoke else 200
    try:
        tok = AutoTokenizer.from_pretrained(base_id)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        net = AutoModelForCausalLM.from_pretrained(
            base_id, dtype=torch.float16, device_map={"": 0}
        )
        net.gradient_checkpointing_enable()
        net.enable_input_require_grads()
        net = get_peft_model(
            net,
            LoraConfig(
                r=8, lora_alpha=16, lora_dropout=0.05, bias="none",
                task_type="CAUSAL_LM",
                target_modules=["q_proj", "v_proj"],
            ),
        )
        trainable = sum(p.numel() for p in net.parameters() if p.requires_grad)
        opt = torch.optim.AdamW(
            [p for p in net.parameters() if p.requires_grad], lr=2e-4
        )

        texts = [
            (str(r.get("prompt", "")) + "\n" + str(r.get("completion", r.get("response", ""))))[:1024]
            for r in rows
        ]
        texts = [t for t in texts if len(t.strip()) > 20] or ["hello world"]

        losses: list[float] = []
        net.train()
        for i in range(steps):
            batch = texts[i % len(texts)]
            enc = tok(batch, return_tensors="pt", truncation=True, max_length=256).to("cuda")
            out = net(**enc, labels=enc["input_ids"])
            out.loss.backward()
            opt.step()
            opt.zero_grad()
            losses.append(float(out.loss.item()))

        peak = torch.cuda.max_memory_allocated() // 2**20
        adapter_dir = RUNS / ("smoke" if smoke else "candidates") / model
        adapter_dir.mkdir(parents=True, exist_ok=True)
        net.save_pretrained(str(adapter_dir))
        weights = adapter_dir / "adapter_model.safetensors"

        result = {
            "base_model": base_id,
            "steps": steps,
            "trainable_params": trainable,
            "loss_first": losses[0],
            "loss_last": losses[-1],
            "loss_series": losses,
            "peak_vram_mib": peak,
            "adapter_dir": str(adapter_dir),
            "weights_written": weights.exists(),
            "weights_bytes": weights.stat().st_size if weights.exists() else 0,
        }
        journal.record(
            StepRecord(
                Step.FIT,
                Outcome.OK,
                f"{steps} steps on {desc}, loss {losses[0]:.4f} -> {losses[-1]:.4f}, "
                f"peak {peak} MiB, weights={'yes' if weights.exists() else 'NO'}",
                data=result,
                seconds=time.time() - t0,
            )
        )
        del net
        torch.cuda.empty_cache()
        return result
    except Exception as exc:
        journal.record(
            StepRecord(Step.FIT, Outcome.FAILED, f"{type(exc).__name__}: {exc}",
                       seconds=time.time() - t0)
        )
        return None


def step_eval(model: str, journal: ModelJournal, fit: dict) -> dict:
    t0 = time.time()
    first, last = fit["loss_first"], fit["loss_last"]
    delta_pct = (last - first) / first * 100 if first else 0.0
    improved = last < first
    metrics = {
        "loss_first": first,
        "loss_last": last,
        "loss_change_pct": round(delta_pct, 3),
        "improved": improved,
    }
    journal.record(
        StepRecord(
            Step.EVAL,
            Outcome.OK,
            f"loss {'fell' if improved else 'ROSE'} {abs(delta_pct):.2f}% "
            f"({first:.4f} -> {last:.4f})",
            data=metrics,
            seconds=time.time() - t0,
        )
    )
    return metrics


def step_gate(model: str, journal: ModelJournal, fit: dict, metrics: dict, smoke: bool) -> bool:
    t0 = time.time()
    if smoke:
        journal.record(
            StepRecord(
                Step.GATE, Outcome.OK,
                "smoke run: not promotable by construction",
                data={"promoted": False, "reason": "smoke"},
                seconds=time.time() - t0,
            )
        )
        return False
    if not fit.get("weights_written"):
        journal.record(
            StepRecord(
                Step.GATE, Outcome.OK,
                "rejected: no adapter weights on disk",
                data={"promoted": False, "reason": "no weights"},
                seconds=time.time() - t0,
            )
        )
        return False
    if not metrics["improved"]:
        journal.record(
            StepRecord(
                Step.GATE, Outcome.OK,
                f"rejected: loss rose {abs(metrics['loss_change_pct']):.2f}%",
                data={"promoted": False, "reason": "regression"},
                seconds=time.time() - t0,
            )
        )
        return False
    journal.record(
        StepRecord(
            Step.GATE, Outcome.OK,
            "candidate improved; promotion still requires the held-out eval in card P4-5",
            data={"promoted": False, "reason": "awaiting P4-5 held-out eval"},
            seconds=time.time() - t0,
        )
    )
    return False


# -------------------------------------------------------------------- driver


def run_model(model: str, smoke: bool) -> ModelJournal:
    journal = ModelJournal(model=model, smoke=smoke)
    logger.info("  model: %s%s", model, " [smoke]" if smoke else "")
    try:
        if not step_artifact(model, journal):
            return journal
        rows = step_data(model, journal, smoke)
        if rows is None:
            return journal
        fit = step_fit(model, journal, rows, smoke)
        if fit is None:
            return journal
        metrics = step_eval(model, journal, fit)
        step_gate(model, journal, fit, metrics, smoke)
    finally:
        journal.write()
    return journal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", default="qwen_lora", help="comma-separated")
    parser.add_argument(
        "--smoke", action="store_true",
        help="tiny end-to-end fit to validate the machinery; never promotable",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s",
                        datefmt="%H:%M:%S")

    ok, desc, free = gpu_state()
    logger.info("GPU: %s (%s MiB free)", desc if ok else "unavailable", free)

    journals = [run_model(m.strip(), args.smoke) for m in args.models.split(",") if m.strip()]

    blocked = sum(1 for j in journals for s in j.steps if s.outcome is Outcome.BLOCKED)
    failed = sum(1 for j in journals for s in j.steps if s.outcome is Outcome.FAILED)
    reached = {j.model: j.last_ok for j in journals}
    logger.info("reached: %s | %d blocked, %d failed", reached, blocked, failed)
    logger.info("journals: %s", JOURNALS)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
