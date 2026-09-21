#!/usr/bin/env python3
"""Phase 2 use case on real hardware: does a learned latent predict execution energy?

Stage A harvests traces by sampling the local Qwen3-8B across a temperature sweep, so the
dataset contains genuine successes *and* genuine failures. Stage B trains the JEPA world
model on those latents and asks the only question that matters: on held-out traces, does
the predicted energy beat a mean-predictor baseline?

Important claim boundary: the latent comes from ``qwen3-embedding:0.6b`` encoding the
emitted code, not from the generator's own residual stream (Ollama does not expose hidden
states). The supported claim is "a learned code representation predicts execution energy",
not "the generator introspects its own energy".

Usage::

    python run_llm_phase2.py --samples-per-task 3 --epochs 120
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from anse.config import JEPAConfig, MemoryConfig
from anse.core.ollama_extractor import OllamaConfig, OllamaExtractor
from anse.jepa.dataset import JEPADataset
from anse.jepa.trainer import JEPATrainer
from anse.jepa.world_model import JEPAWorldModel
from anse.memory.harvester import Harvester, LoopTrace
from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.parser import extract_code
from anse.symbolic.sandbox import SandboxExecutor
from main import load_tasks

HIDDEN_DIM = 1024

SYSTEM = (
    "You are an expert Python programmer. Write complete, self-contained code solving the "
    "task, with asserts at the bottom. Return a single ```python block, nothing else."
)


def harvest(args: argparse.Namespace, out_dir: Path) -> Path:
    """Sample the LLM across temperatures and record real (latent, energy) pairs."""
    extractor = OllamaExtractor(OllamaConfig(gen_model=args.model))
    sandbox = SandboxExecutor()
    evaluator = EnergyEvaluator()
    harvester = Harvester(
        config=MemoryConfig(
            persist_directory=out_dir / "chroma",
            interactions_log=out_dir / "interactions.jsonl",
        ),
        enable_chroma=False,
    )

    tasks = load_tasks(Path(args.tasks))
    temps = [0.0, 0.5, 0.9, 1.3]
    rng = random.Random(0)
    n = 0
    started = time.time()

    for t_i, task in enumerate(tasks, 1):
        for s in range(args.samples_per_task):
            temp = temps[s % len(temps)]
            prompt = f"TASK:\n{task['task']}"
            if temp > 0.8:
                # Nudge toward terser answers: produces genuine failures, not synthetic ones.
                prompt += "\nBe extremely concise."
            raw, record = extractor.extract(
                prompt, system_prompt=SYSTEM, temperature=temp,
            )
            code = extract_code(raw).code
            exec_res = sandbox.execute(code)
            energy = evaluator.evaluate(
                result=exec_res, code=code, expected_output=task.get("expected_output"),
            )
            harvester.record(LoopTrace(
                task=task["task"],
                prompt=prompt,
                code=code,
                raw_response=raw,
                energy=energy.score,
                energy_category=energy.category.value,
                converged=energy.score <= 5.0,
                iteration=s + 1,
                duration_ms=exec_res.duration_ms,
                returncode=exec_res.returncode,
                execution_stdout=exec_res.stdout,
                execution_stderr=exec_res.stderr,
                hidden_state=record.to_embedding(),
                metadata={"temperature": temp, "tier": task.get("tier", "?"), **record.metadata},
            ))
            n += 1
            print(f"  [{t_i:2d}/{len(tasks)} s{s+1}] T={temp} E={energy.score:>8.1f} "
                  f"{energy.category.value}", flush=True)
        rng.random()

    print(f"[phase2-llm] harvested {n} traces in {time.time() - started:.0f}s "
          f"-> {harvester.log_path}", flush=True)
    return harvester.log_path


def pearson(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation; 0.0 when either series is constant."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return 0.0 if dx == 0 or dy == 0 else num / (dx * dy)


def evaluate_predictions(model: JEPAWorldModel, loader: DataLoader) -> dict:
    """Compare JEPA energy predictions against a mean-predictor baseline on held-out data."""
    model.eval()
    preds: list[float] = []
    actuals: list[float] = []
    with torch.no_grad():
        for h_ctx, _h_tgt, energy in loader:
            for i in range(h_ctx.shape[0]):
                preds.append(model.predict_energy_scalar(h_ctx[i]))
                actuals.append(float(energy[i]))

    if not actuals:
        return {"n": 0}

    # predict_energy_scalar returns a 0-100 energy; dataset energies are normalised to [0,1].
    scaled = [p / 100.0 for p in preds]
    baseline = sum(actuals) / len(actuals)
    mae = sum(abs(p - a) for p, a in zip(scaled, actuals)) / len(actuals)
    mae_baseline = sum(abs(baseline - a) for a in actuals) / len(actuals)
    return {
        "n": len(actuals),
        "pearson_r": round(pearson(scaled, actuals), 4),
        "mae": round(mae, 4),
        "mae_mean_baseline": round(mae_baseline, 4),
        "beats_baseline": mae < mae_baseline,
        "skill_score_vs_baseline_pct": round(100.0 * (1 - mae / max(mae_baseline, 1e-9)), 1),
        "pred_std": round(float(torch.tensor(scaled).std()), 4),
        "actual_std": round(float(torch.tensor(actuals).std()), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", default="tasks/phase1_benchmark.yaml")
    parser.add_argument("--out", default=".scratchpad/llm_phase2")
    parser.add_argument("--samples-per-task", type=int, default=3)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--skip-harvest", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "interactions.jsonl"

    if not args.skip_harvest:
        print(f"[phase2-llm] harvesting: {args.samples_per_task} samples/task", flush=True)
        jsonl = harvest(args, out_dir)

    rows = [json.loads(line) for line in jsonl.open(encoding="utf-8") if line.strip()]
    dims = {len(r["hidden_state"]) for r in rows}
    assert dims == {HIDDEN_DIM}, f"latent dim mismatch {dims}; JEPA would train on padding"
    energies = [r["energy"] for r in rows]
    print(f"[phase2-llm] {len(rows)} traces, energy min={min(energies)} max={max(energies)} "
          f"distinct={len(set(energies))}", flush=True)

    dataset = JEPADataset(jsonl, hidden_dim=HIDDEN_DIM)
    print(f"[phase2-llm] dataset pairs: {len(dataset)}", flush=True)

    jepa_cfg = JEPAConfig(latent_dim=128, hidden_dim=256)
    model = JEPAWorldModel(
        d_input=HIDDEN_DIM,
        d_hidden=jepa_cfg.hidden_dim,
        d_latent=jepa_cfg.latent_dim,
    )
    trainer = JEPATrainer(
        model=model, config=jepa_cfg, checkpoint_dir=out_dir / "checkpoints", device="cpu",
    )
    started = time.time()
    summary = trainer.train(
        dataset, epochs=args.epochs, batch_size=16, val_fraction=0.25, seed=42,
    )
    train_s = time.time() - started

    generator = torch.Generator().manual_seed(42)
    n_val = max(1, int(0.25 * len(dataset)))
    _, val_ds = torch.utils.data.random_split(
        dataset, [len(dataset) - n_val, n_val], generator=generator,
    )
    metrics = evaluate_predictions(model, DataLoader(val_ds, batch_size=8))

    report = {
        "model": args.model,
        "embedding_model": "qwen3-embedding:0.6b",
        "latent_dim_note": "latent is a separate encoder's code representation, "
                           "not the generator's own hidden state",
        "traces": len(rows),
        "dataset_pairs": len(dataset),
        "energy_distinct_values": len(set(energies)),
        "epochs": args.epochs,
        "train_seconds": round(train_s, 1),
        "final_train_loss": round(float(summary.final_train_loss), 5),
        "final_val_loss": round(float(summary.final_val_loss), 5),
        "held_out": metrics,
    }
    (out_dir / "phase2_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== PHASE 2 (real LLM latents) ===")
    print(f"traces={len(rows)} pairs={len(dataset)} epochs={args.epochs} ({train_s:.0f}s)")
    print(f"train_loss={report['final_train_loss']} val_loss={report['final_val_loss']}")
    print(f"held-out n={metrics['n']} pearson_r={metrics.get('pearson_r')} "
          f"MAE={metrics.get('mae')} vs baseline {metrics.get('mae_mean_baseline')}")
    print(f"beats mean-predictor: {metrics.get('beats_baseline')} "
          f"(skill {metrics.get('skill_score_vs_baseline_pct')}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
