"""
Phase 2 evolution validation: five use cases for the JEPA world model ("intuition"),
measured on the verified traces harvested by run_phase1_evolution.py. CPU only, no LLM calls.

    python run_phase2_evolution.py --seeds 1 2 3 4 5

UC1 intuition beats a constant   held-out-task first-attempt MAE vs predict-the-train-mean, Spearman
UC2 pass/fail discrimination     first-attempt ROC-AUC, verified fail vs pass (+ leaky all-states, iteration baseline)
UC3 predictive pairs ablation    self-pairs (old) vs transition pairs (new) vs identity baseline
UC4 intuition-guided selection   pick the lowest predicted energy among candidates, vs random / oracle
UC5 robustness                   no collapse, loud dimension errors, NaN/empty skipped, bounded output, raw == normalised input

UC1/UC2 (and gates G1/G2) are scored on FIRST ATTEMPTS only: one state per task run. A retry only
exists because the previous attempt failed, its response usually says so ("the previous code fails
because..."), and in the harvested data no retry ever changed the verified energy. The embedding of a
retry therefore leaks its own label and repeats its task's label ~3x. Scoring those states measured
"is this a retry?", not intuition about code: the bare iteration number out-scored the model. The
all-states numbers and the iteration-number baseline are still reported, labelled as leaky, so the
leak stays visible. Byte-identical replayed traces are dropped by JEPADataset and counted.

Every prediction that is scored is OUT-OF-FOLD: tasks are partitioned into k folds, a model is
trained on k-1 folds of tasks and only predicts the attempts of the tasks it never saw. No epoch,
checkpoint or hyper-parameter is selected on the held-out fold. Gate thresholds were written before
the first run on real data and have not moved. Hyper-parameters are fixed CLI defaults; they were
revised once, after the first real run (35 traces): the TRAINING energy loss showed 80 optimiser
steps barely beat the label variance, so lr/epochs/batch became 3e-3 / 100 / full batch, and the
failed collapse check led to VICReg also being applied to the context latents the energy head reads.
After an independent review the SCORING changed (first attempts only, first-attempt train mean as the
constant baseline, duplicates dropped, inputs normalised inside the model); hyper-parameters and gate
thresholds did not.

Results are checkpointed to <out>/results.json after every use case.
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
import yaml
from torch.utils.data import Subset

from anse.jepa.dataset import HiddenDimMismatchError, JEPADataset, task_kfold
from anse.jepa.metrics import (
    latent_std,
    mean_absolute_error,
    ridge_fit_predict,
    roc_auc,
    spearman,
)
from anse.jepa.trainer import JEPATrainer
from anse.jepa.world_model import JEPAWorldModel

ROOT = Path(__file__).parent
DEFAULT_TRACES = [
    ROOT / "results" / "phase1_evolution" / "traces_uc2_verified.jsonl",
    ROOT / "results" / "phase1_evolution" / "traces_uc4_memory.jsonl",
]
ARMS = ("mixed", "self", "transition")
MIN_TRANSITIONS = 10  # below this UC3 refuses to draw a conclusion
DEAD_DIM_STD = 0.01  # sqrt of the 1e-4 epsilon inside VICReg's std: invisible to the loss below it
MIN_MEAN_STD = 0.1  # 10% of the VICReg variance margin (gamma = 1.0)

UC_META = {
    "uc1": ("Intuition beats a constant", "On tasks never seen in training, is predicted energy closer to the verified energy than always predicting the training mean?"),
    "uc2": ("Pass/fail discrimination", "Does predicted energy rank verified failures above verified passes on held-out tasks?"),
    "uc3": ("Predictive pairs ablation", "Does training on real attempt t -> t+1 pairs predict the next latent better than self-pairs and than assuming nothing changes?"),
    "uc4": ("Intuition-guided selection", "If the agent runs only the candidate with the lowest predicted energy, does it pass more often than a random pick?"),
    "uc5": ("Robustness", "Does the world model avoid collapse, refuse wrong dimensions, skip NaN/empty states, keep predictions in [0, 100] and treat raw embeddings like its training input?"),
}


class InsufficientDataError(RuntimeError):
    """Not enough verified traces to say anything."""


@dataclass
class FoldRun:
    """Everything measured for one (seed, fold, arm) model on its held-out tasks."""

    seed: int
    fold: int
    arm: str
    val_states: list[int]
    predictions: list[float]
    ridge_predictions: list[float]
    train_mean: float
    train_median: float
    train_first_mean: float  # the same constants over first-attempt training states only
    train_first_median: float
    ctx_std_mean: float
    ctx_std_min: float
    ctx_dead_fraction: float
    pred_std_mean: float
    transition_errors: list[tuple[bool, float, float]] = field(default_factory=list)  # (code changed, predictor, identity)
    cpu_seconds: float = 0.0


def r4(value: float | None) -> float | None:
    return None if value is None else round(float(value), 4)


def mean_or_none(values: list[float]) -> float | None:
    return r4(statistics.fmean(values)) if values else None


class Bench:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.out = Path(args.out)
        self.trace_files = [Path(p) for p in args.traces]
        self.ds = JEPADataset(self.trace_files, hidden_dim=None, pair_mode="mixed", verified_only=True)
        n_states = len(self.ds.states)
        tasks = sorted({s.task for s in self.ds.states})
        if n_states < args.min_traces or len(tasks) < args.folds:
            existing = [str(p) for p in self.trace_files if p.exists()]
            raise InsufficientDataError(
                f"only {n_states} usable verified traces over {len(tasks)} tasks (need >= {args.min_traces} "
                f"traces and >= {args.folds} tasks). Usable = metadata.tests_total > 0, a finite, non-empty "
                f"hidden_state, and not an exact duplicate of a trace already loaded. Files found: {existing or 'none'}; skipped: {self.ds.skipped}. "
                f"Let run_phase1_evolution.py (UC2/UC4) finish, then re-run."
            )
        if len(self.ds.first_attempt_indices()) < args.folds:
            raise InsufficientDataError(
                f"only {len(self.ds.first_attempt_indices())} first-attempt states (iteration <= 1 opening a run) among "
                f"{n_states} traces; UC1/UC2 are scored on first attempts and need >= {args.folds}."
            )
        self.out.mkdir(parents=True, exist_ok=True)

        suite = yaml.safe_load((ROOT / "tasks" / "phase1_evolution.yaml").read_text())["tasks"]
        names = {t["task"]: t["name"] for t in suite}
        self.short = {task: names.get(task, task[:40]) for task in tasks}
        self.hidden = torch.stack([s.hidden for s in self.ds.states])
        self.energy = [s.energy for s in self.ds.states]
        self.first = self.ds.first_attempt_indices()
        self.first_set = set(self.first)
        n_first_fail = sum(self.energy[i] > 0 for i in self.first)
        self.runs: list[FoldRun] = []
        self.last_model: JEPAWorldModel | None = None
        n_fail = sum(e > 0 for e in self.energy)
        self.results: dict[str, Any] = {
            "phase": 2,
            "backend": f"torch-cpu JEPA {self.ds.hidden_dim}->{args.d_hidden}->{args.d_latent}, task-level {args.folds}-fold CV",
            "seeds": args.seeds,
            "trace_files": [p.name for p in self.trace_files if p.exists()],
            "n_states": n_states,
            "n_duplicate_traces_dropped": self.ds.skipped["duplicate"],
            "n_distinct_embeddings": self.ds.distinct_embedding_count(),
            "n_tasks": len(tasks),
            "n_first_attempt_states": len(self.first),
            "n_first_attempt_fail": n_first_fail,
            "n_first_attempt_pass": len(self.first) - n_first_fail,
            "n_transitions": len(self.ds.transitions),
            "n_verified_fail": n_fail,
            "n_verified_pass": n_states - n_fail,
            "sample_size_note": "n_states counts distinct (task, iteration, embedding) traces; retries repeat their task's label, so the independent sample for UC1/UC2 is n_first_attempt_states (one per task run).",
            "hidden_dim": self.ds.hidden_dim,
            "skipped_traces": dict(self.ds.skipped),
            "hyperparameters": {
                "d_hidden": args.d_hidden, "d_latent": args.d_latent, "dropout": args.dropout,
                "weight_decay": args.weight_decay, "lr": args.lr, "epochs": args.epochs,
                "batch_size": args.batch_size, "energy_weight": args.energy_weight, "ridge_alpha": args.ridge_alpha,
            },
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def checkpoint(self) -> None:
        self.results["cpu_seconds"] = round(time.process_time(), 1)
        for key, (title, question) in UC_META.items():
            if key in self.results:
                self.results[key] = {"title": title, "question": question, **self.results[key]}
        (self.out / "results.json").write_text(json.dumps(self.results, indent=2))

    # ── Training (shared by all use cases) ───────────────────────────────────
    def new_model(self, seed: int) -> JEPAWorldModel:
        torch.manual_seed(seed)
        return JEPAWorldModel(
            d_input=self.ds.hidden_dim, d_hidden=self.args.d_hidden, d_latent=self.args.d_latent,
            dropout=self.args.dropout, energy_weight=self.args.energy_weight,
        )

    def train_one(self, seed: int, fold: int, arm: str, val_tasks: set[str]) -> FoldRun | None:
        a = self.args
        started = time.process_time()
        all_tasks = {s.task for s in self.ds.states}
        self.ds.set_pair_mode(arm)
        train_idx = self.ds.indices_for_tasks(all_tasks - val_tasks)
        val_idx = self.ds.indices_for_tasks(val_tasks)
        if len(train_idx) < 2:
            return None  # e.g. the transition arm when the training tasks have < 2 transitions
        model = self.new_model(1000 * seed + fold)
        trainer = JEPATrainer(model, lr=a.lr, weight_decay=a.weight_decay, checkpoint_dir=self.out / "checkpoints")
        trainer.fit(Subset(self.ds, train_idx), Subset(self.ds, val_idx or train_idx[:1]), epochs=a.epochs,
                    batch_size=a.batch_size, seed=seed, select_best_on_val=False, validate_every=a.epochs)
        model.eval()

        val_states = [i for i, s in enumerate(self.ds.states) if s.task in val_tasks]
        train_states = [i for i, s in enumerate(self.ds.states) if s.task not in val_tasks]
        h_val = self.hidden[val_states]
        y_train = torch.tensor([self.energy[i] for i in train_states])
        first_train = [self.energy[i] for i in train_states if i in self.first_set]
        y_first = torch.tensor(first_train) if first_train else y_train
        with torch.no_grad():
            z_ctx = model.encode_context(h_val)
            z_pred = model.predictor(z_ctx, z_ctx)  # type: ignore[misc]
            ctx_std = latent_std(z_ctx)
            errors = []
            for ctx, tgt in self.ds.transitions:
                if self.ds.states[tgt].task in val_tasks:
                    h_t, h_next = self.hidden[ctx : ctx + 1], self.hidden[tgt : tgt + 1]
                    z_next = model.tgt_encoder(model.prepare_input(h_next))  # type: ignore[misc]
                    z_t = model.encode_context(h_t)
                    predicted = model.predictor(z_t, z_t)  # type: ignore[misc]
                    errors.append((
                        self.ds.states[ctx].code.strip() != self.ds.states[tgt].code.strip(),
                        float((predicted - z_next).pow(2).sum()),
                        float((model.tgt_encoder(model.prepare_input(h_t)) - z_next).pow(2).sum()),  # type: ignore[misc]
                    ))
        ridge = ridge_fit_predict(self.hidden[train_states], y_train, h_val, alpha=a.ridge_alpha).clamp(0.0, 100.0)
        self.last_model = model
        return FoldRun(
            seed=seed, fold=fold, arm=arm, val_states=val_states,
            predictions=model.predict_energy_batch(h_val).tolist(),
            ridge_predictions=ridge.tolist(),
            train_mean=float(y_train.mean()), train_median=float(y_train.median()),
            train_first_mean=float(y_first.mean()), train_first_median=float(y_first.median()),
            ctx_std_mean=float(ctx_std.mean()), ctx_std_min=float(ctx_std.min()),
            ctx_dead_fraction=float((ctx_std < DEAD_DIM_STD).float().mean()),
            pred_std_mean=float(latent_std(z_pred).mean()),
            transition_errors=errors, cpu_seconds=time.process_time() - started,
        )

    def train_all(self) -> None:
        tasks = [s.task for s in self.ds.states]
        for seed in self.args.seeds:
            folds = task_kfold(tasks, self.args.folds, seed)
            for fold, val_tasks in enumerate(folds):
                for arm in ARMS:
                    run = self.train_one(seed, fold, arm, val_tasks)
                    if run is not None:
                        self.runs.append(run)
            done = [r for r in self.runs if r.seed == seed]
            print(f"  trained seed={seed}: {len(done)} models, {sum(r.cpu_seconds for r in done):.1f}s CPU", flush=True)
        self.ds.set_pair_mode("mixed")

    def oof(self, seed: int, arm: str = "mixed") -> dict[int, dict[str, float]]:
        """state index → out-of-fold predictions and the constants known at training time."""
        table: dict[int, dict[str, float]] = {}
        for run in self.runs:
            if run.seed == seed and run.arm == arm:
                for i, p, rp in zip(run.val_states, run.predictions, run.ridge_predictions):
                    table[i] = {"jepa": p, "ridge": rp, "mean": run.train_mean, "median": run.train_median,
                                "first_mean": run.train_first_mean, "first_median": run.train_first_median,
                                "iteration": float(self.ds.states[i].iteration)}
        return table

    # ── UC1 ──────────────────────────────────────────────────────────────────
    def uc1_beats_constant(self) -> None:
        rows = []
        for seed in self.args.seeds:
            table = self.oof(seed)
            every = sorted(table)
            idx = [i for i in every if i in self.first_set]
            actual = [self.energy[i] for i in idx]
            row: dict[str, Any] = {"seed": seed, "first_attempt_states": len(idx),
                                   "independent_tasks": len({self.ds.states[i].task for i in idx})}
            for key in ("jepa", "first_mean", "first_median", "mean", "ridge"):
                row[f"mae_{key}"] = r4(mean_absolute_error([table[i][key] for i in idx], actual))
            row["spearman_jepa"] = r4(spearman([table[i]["jepa"] for i in idx], actual))
            row["spearman_ridge"] = r4(spearman([table[i]["ridge"] for i in idx], actual))
            row["beats_mean_baseline"] = row["mae_jepa"] < row["mae_first_mean"]
            row["all_states_leaky"] = len(every)
            row["mae_jepa_all_states_leaky"] = r4(mean_absolute_error([table[i]["jepa"] for i in every], [self.energy[i] for i in every]))
            row["mae_mean_all_states_leaky"] = r4(mean_absolute_error([table[i]["mean"] for i in every], [self.energy[i] for i in every]))
            rows.append(row)
            print(f"  UC1 seed={seed} first-attempt MAE jepa={row['mae_jepa']} first_mean={row['mae_first_mean']} "
                  f"first_median={row['mae_first_median']} ridge={row['mae_ridge']} spearman={row['spearman_jepa']} "
                  f"| all states (leaky) jepa={row['mae_jepa_all_states_leaky']} mean={row['mae_mean_all_states_leaky']}", flush=True)
        defined = [r["spearman_jepa"] for r in rows if r["spearman_jepa"] is not None]
        self.results["uc1"] = {
            "seeds": len(rows),
            "scored_on": "first attempts only (one state per task run)",
            "first_attempt_states": rows[0]["first_attempt_states"],
            "independent_tasks": rows[0]["independent_tasks"],
            "mae_jepa": mean_or_none([r["mae_jepa"] for r in rows]),
            "mae_mean_baseline": mean_or_none([r["mae_first_mean"] for r in rows]),
            "mae_median_baseline": mean_or_none([r["mae_first_median"] for r in rows]),
            "mae_all_states_train_mean": mean_or_none([r["mae_mean"] for r in rows]),
            "mae_ridge_on_raw_embedding": mean_or_none([r["mae_ridge"] for r in rows]),
            "spearman_jepa": mean_or_none(defined),
            "spearman_ridge": mean_or_none([r["spearman_ridge"] for r in rows if r["spearman_ridge"] is not None]),
            "seeds_beating_mean_baseline": sum(r["beats_mean_baseline"] for r in rows),
            "mae_jepa_all_states_leaky": mean_or_none([r["mae_jepa_all_states_leaky"] for r in rows]),
            "mae_mean_all_states_leaky": mean_or_none([r["mae_mean_all_states_leaky"] for r in rows]),
            "note": "The mean baseline is the mean energy of the first-attempt TRAINING states, the strongest mean constant for this "
                    "evaluation set (the all-states training mean is inflated by retries of failing tasks). MSE-trained regressors target "
                    "the mean; with many zero energies the median constant can have a lower MAE and is reported for honesty. "
                    "*_all_states_leaky include retries, whose embeddings leak their label; they are not evidence of intuition.",
            "rows": rows,
        }
        self.checkpoint()

    # ── UC2 ──────────────────────────────────────────────────────────────────
    def uc2_discrimination(self) -> None:
        rows = []
        for seed in self.args.seeds:
            table = self.oof(seed)
            every = sorted(table)
            idx = [i for i in every if i in self.first_set]
            failed = [self.energy[i] > 0 for i in idx]
            failed_all = [self.energy[i] > 0 for i in every]
            rows.append({
                "seed": seed, "first_attempt_fail": sum(failed), "first_attempt_pass": len(failed) - sum(failed),
                "auc_jepa": r4(roc_auc([table[i]["jepa"] for i in idx], failed)),
                "auc_ridge": r4(roc_auc([table[i]["ridge"] for i in idx], failed)),
                "all_states_fail": sum(failed_all), "all_states_pass": len(failed_all) - sum(failed_all),
                "auc_jepa_all_states_leaky": r4(roc_auc([table[i]["jepa"] for i in every], failed_all)),
                "auc_iteration_number_all_states": r4(roc_auc([table[i]["iteration"] for i in every], failed_all)),
            })
            print(f"  UC2 seed={seed} first-attempt AUC jepa={rows[-1]['auc_jepa']} ridge={rows[-1]['auc_ridge']} | all states (leaky) "
                  f"jepa={rows[-1]['auc_jepa_all_states_leaky']} iteration-number={rows[-1]['auc_iteration_number_all_states']}", flush=True)
        aucs = [r["auc_jepa"] for r in rows if r["auc_jepa"] is not None]
        leaky = mean_or_none([r["auc_jepa_all_states_leaky"] for r in rows if r["auc_jepa_all_states_leaky"] is not None])
        iteration = mean_or_none([r["auc_iteration_number_all_states"] for r in rows if r["auc_iteration_number_all_states"] is not None])
        self.results["uc2"] = {
            "seeds": len(rows),
            "scored_on": "first attempts only (one state per task run)",
            "independent_tasks": len({self.ds.states[i].task for i in self.first}),
            "verified_fail": rows[0]["first_attempt_fail"],
            "verified_pass": rows[0]["first_attempt_pass"],
            "auc_mean": mean_or_none(aucs),
            "auc_min": r4(min(aucs)) if aucs else None,
            "auc_ridge_mean": mean_or_none([r["auc_ridge"] for r in rows if r["auc_ridge"] is not None]),
            "chance_level": 0.5,
            "all_states_fail": rows[0]["all_states_fail"],
            "all_states_pass": rows[0]["all_states_pass"],
            "auc_jepa_all_states_leaky": leaky,
            "auc_iteration_number_all_states": iteration,
            "note": "A retry exists only because the previous attempt failed, so on all states the iteration number alone is a "
                    "pass/fail classifier needing no model (auc_iteration_number_all_states). Any all-states AUC at or below it "
                    "shows no intuition; only the first-attempt AUC, where that cue is absent, is gated.",
            "rows": rows,
        }
        self.checkpoint()

    # ── UC3 ──────────────────────────────────────────────────────────────────
    def uc3_pairs_ablation(self) -> None:
        n_transitions = len(self.ds.transitions)
        unchanged = sum(self.ds.states[a].code.strip() == self.ds.states[b].code.strip() for a, b in self.ds.transitions)
        rows = []
        for seed in self.args.seeds:
            for arm in ARMS:
                errors = [e for run in self.runs if run.seed == seed and run.arm == arm for e in run.transition_errors]
                if not errors:
                    continue
                predictor = statistics.fmean(e[1] for e in errors)
                identity = statistics.fmean(e[2] for e in errors)
                changed = [e for e in errors if e[0]]
                changed_identity = statistics.fmean(e[2] for e in changed) if changed else 0.0
                rows.append({
                    "seed": seed, "arm": arm, "held_out_transitions": len(errors),
                    "predictor_error": r4(predictor), "identity_error": r4(identity),
                    "relative_error": r4(predictor / identity) if identity > 0 else None,
                    "changed_code_transitions": len(changed),
                    "relative_error_changed_code": r4(statistics.fmean(e[1] for e in changed) / changed_identity) if changed_identity > 0 else None,
                })

        def arm_stats(arm: str) -> dict[str, float]:
            sel = [r for r in rows if r["arm"] == arm and r["relative_error"] is not None]
            if not sel:
                return {"seeds": 0}
            rel = [r["relative_error"] for r in sel]
            changed = [r["relative_error_changed_code"] for r in sel if r["relative_error_changed_code"] is not None]
            return {"seeds": len(sel), "relative_error_mean": r4(statistics.fmean(rel)),  # type: ignore[dict-item]
                    "relative_error_max": r4(max(rel)), "seeds_beating_identity": sum(x < 1.0 for x in rel),  # type: ignore[dict-item]
                    "relative_error_changed_code_mean": mean_or_none(changed)}  # type: ignore[dict-item]

        enough = n_transitions >= MIN_TRANSITIONS
        stats = {arm: arm_stats(arm) for arm in ARMS}
        if not enough:
            conclusion = (f"INSUFFICIENT DATA: only {n_transitions} transition pairs exist (need >= {MIN_TRANSITIONS}); "
                          "the numbers below are reported but no conclusion is drawn.")
        else:
            mixed, old = stats["mixed"].get("relative_error_mean"), stats["self"].get("relative_error_mean")
            conclusion = (f"{n_transitions} transitions, {unchanged} of them with byte-identical code (identity error is exactly 0 there, "
                          f"so 'nothing changes' is unbeatable on them). Relative error (predictor / identity, < 1 beats 'nothing changes'): "
                          f"self-pairs {old}, mixed {mixed}, transition-only {stats['transition'].get('relative_error_mean')}.")
        self.results["uc3"] = {
            "transition_pairs": n_transitions,
            "transitions_with_unchanged_code": unchanged,
            "min_transitions_for_conclusion": MIN_TRANSITIONS,
            "enough_data": enough,
            "self_pairs_old": stats["self"],
            "mixed_new_default": stats["mixed"],
            "transition_only": stats["transition"],
            "conclusion": conclusion,
            "note": "relative_error = mean ||pred(z_t) - z_{t+1}||^2 / mean ||z_t - z_{t+1}||^2 inside each model's own latent space, on transitions of held-out tasks.",
            "rows": rows,
        }
        print(f"  UC3 {conclusion}", flush=True)
        self.checkpoint()

    # ── UC4 ──────────────────────────────────────────────────────────────────
    def uc4_selection(self) -> None:
        candidates: dict[str, list[int]] = {}
        for task in sorted({s.task for s in self.ds.states}):
            seen: set[str] = set()
            for i, s in enumerate(self.ds.states):
                if s.task == task and s.code.strip() and s.code.strip() not in seen:
                    seen.add(s.code.strip())
                    candidates.setdefault(task, []).append(i)
        eligible = {t: c for t, c in candidates.items() if len(c) >= 2}
        rows = []
        for seed in self.args.seeds:
            table = self.oof(seed)
            for task, cand in eligible.items():
                passes = [self.energy[i] == 0.0 for i in cand]
                order = sorted(range(len(cand)), key=lambda j: (table[cand[j]]["jepa"], j))
                ridge_order = sorted(range(len(cand)), key=lambda j: (table[cand[j]]["ridge"], j))
                rows.append({
                    "seed": seed, "task": self.short[task], "candidates": len(cand), "passing": sum(passes),
                    "decidable": 0 < sum(passes) < len(cand),
                    "picked_pass": passes[order[0]], "ridge_picked_pass": passes[ridge_order[0]],
                    "random_expected_pass": r4(sum(passes) / len(passes)), "oracle_pass": any(passes),
                    "picked_predicted_energy": r4(table[cand[order[0]]]["jepa"]),
                    "picked_verified_energy": self.energy[cand[order[0]]],
                })

        def rates(sel: list[dict[str, Any]]) -> dict[str, float]:
            if not sel:
                return {"picks": 0}
            n = len(sel)
            return {"picks": n, "intuition_pass_rate": r4(sum(r["picked_pass"] for r in sel) / n),  # type: ignore[dict-item]
                    "random_pass_rate": r4(sum(r["random_expected_pass"] for r in sel) / n),  # type: ignore[dict-item]
                    "oracle_pass_rate": r4(sum(r["oracle_pass"] for r in sel) / n),  # type: ignore[dict-item]
                    "ridge_pass_rate": r4(sum(r["ridge_picked_pass"] for r in sel) / n)}  # type: ignore[dict-item]

        decidable = [r for r in rows if r["decidable"]]
        if not rows:
            conclusion = "NO DATA: no task has two distinct candidate attempts."
        elif not decidable:
            conclusion = (f"NOT DECIDABLE: {len(eligible)} tasks have >= 2 distinct candidates, but in every one of them all candidates "
                          "pass or all fail, so no selector can beat or lose to random. More seeds per task are needed.")
        else:
            conclusion = f"{len({r['task'] for r in decidable})} decidable tasks, {len(decidable)} picks over {len(self.args.seeds)} model seeds."
        self.results["uc4"] = {
            "tasks_with_2plus_distinct_candidates": len(eligible),
            "decidable_tasks": len({r["task"] for r in decidable}),
            "all_eligible": rates(rows),
            "decidable_only": rates(decidable),
            "conclusion": conclusion,
            "sandbox_runs_saved_per_pick": r4(statistics.fmean(r["candidates"] - 1 for r in rows)) if rows else None,
            "note": "decidable = the candidates of the task include both a verified pass and a verified fail; only there can any selector differ from random. "
                    "Candidates from retries carry the 'previous attempt failed' cue in their embedding, so a future decidable result must be read next to UC2's iteration-number baseline.",
            "rows": rows,
        }
        print(f"  UC4 all={self.results['uc4']['all_eligible']} decidable={self.results['uc4']['decidable_only']}", flush=True)
        self.checkpoint()

    # ── UC5 ──────────────────────────────────────────────────────────────────
    def real_raw_traces(self, n: int) -> list[dict[str, Any]]:
        """The first *n* real verified traces, as raw dicts, to build corrupted copies from."""
        found: list[dict[str, Any]] = []
        for path in self.trace_files:
            if not path.exists():
                continue
            for line in path.read_text().splitlines():
                if len(found) == n:
                    return found
                try:
                    trace = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if len(trace.get("hidden_state") or []) == self.ds.hidden_dim and (trace.get("metadata") or {}).get("tests_total"):
                    found.append(trace)
        if len(found) < n:
            raise InsufficientDataError(f"UC5 needs {n} real traces to corrupt, found {len(found)}")
        return found

    def uc5_robustness(self) -> None:
        rows: list[dict[str, Any]] = []
        mixed = [r for r in self.runs if r.arm == "mixed"]
        worst_mean = min(r.ctx_std_mean for r in mixed)
        worst_dead = max(r.ctx_dead_fraction for r in mixed)
        rows.append({"check": "no_representation_collapse", "passed": worst_mean >= MIN_MEAN_STD and worst_dead == 0.0,
                     "models": len(mixed), "worst_mean_latent_std": r4(worst_mean), "worst_min_latent_std": r4(min(r.ctx_std_min for r in mixed)),
                     "worst_dead_dim_fraction": r4(worst_dead), "threshold_mean_std": MIN_MEAN_STD, "threshold_dead_std": DEAD_DIM_STD})

        real_dim = self.ds.hidden_dim
        raw = self.real_raw_traces(3)
        truncated = dict(raw[0], hidden_state=raw[0]["hidden_state"][: real_dim // 2])
        path = self.out / "uc5_dimension_mismatch.jsonl"
        path.write_text(json.dumps(raw[1]) + "\n" + json.dumps(truncated) + "\n")
        message = ""
        try:
            JEPADataset(path, hidden_dim=real_dim)
        except HiddenDimMismatchError as exc:
            message = str(exc)
        legacy_message = ""
        try:
            JEPADataset(path, hidden_dim=4096)  # the old default silently zero-padded 1536 → 4096
        except HiddenDimMismatchError as exc:
            legacy_message = str(exc)
        model_message = ""
        model = self.last_model
        if model is None:
            raise RuntimeError("UC5 needs the models trained by train_all()")
        try:
            model.predict_energy_scalar(torch.zeros(real_dim + 1))
        except HiddenDimMismatchError as exc:
            model_message = str(exc)
        rows.append({"check": "dimension_mismatch_raises", "passed": bool(message and legacy_message and model_message),
                     "dataset_error": message[:120], "legacy_4096_error": legacy_message[:120], "model_error": model_message[:120]})

        nan_state = list(raw[0]["hidden_state"])
        nan_state[7] = float("nan")
        path = self.out / "uc5_nan_empty.jsonl"
        path.write_text("\n".join([json.dumps(raw[0]), json.dumps(dict(raw[1], hidden_state=nan_state)),
                                   json.dumps(dict(raw[1], hidden_state=[])), "{not json", json.dumps(raw[2])]) + "\n")
        dirty = JEPADataset(path, hidden_dim=real_dim)
        finite = all(bool(torch.isfinite(s.hidden).all()) for s in dirty.states)
        rows.append({"check": "nan_and_empty_states_skipped",
                     "passed": len(dirty.states) == 2 and finite and dirty.skipped["non_finite"] == 1
                     and dirty.skipped["empty_hidden_state"] == 1 and dirty.skipped["malformed_json"] == 1,
                     "lines_written": 5, "states_kept": len(dirty.states), "skipped_non_finite": dirty.skipped["non_finite"],
                     "skipped_empty": dirty.skipped["empty_hidden_state"], "skipped_malformed": dirty.skipped["malformed_json"]})

        oof_preds = [p for r in self.runs for p in r.predictions]
        h = self.hidden[:8]
        stress = torch.cat([h * 1e6, -h * 1e6, torch.zeros(1, real_dim)])
        stress_preds = model.predict_energy_batch(stress).tolist()
        nan_rejected = False
        try:
            model.predict_energy_scalar(torch.full((real_dim,), float("nan")))
        except ValueError:
            nan_rejected = True
        try:  # float32 overflow inside the network: either a bounded number or a loud error, never NaN
            stress_preds.append(model.predict_energy_scalar(torch.full((real_dim,), 3.0e38)))
            overflow = "bounded"
        except ValueError:
            overflow = "rejected"
        every = oof_preds + stress_preds
        rows.append({"check": "predictions_within_0_100", "passed": all(0.0 <= p <= 100.0 for p in every) and nan_rejected,
                     "held_out_predictions": len(oof_preds), "stress_inputs": len(stress_preds), "min_prediction": r4(min(every)),
                     "max_prediction": r4(max(every)), "nan_input_rejected": nan_rejected, "float32_overflow_input": overflow})

        raw_h = torch.tensor([t["hidden_state"] for t in raw], dtype=torch.float32)
        unit_h = raw_h / raw_h.norm(dim=-1, keepdim=True)
        raw_preds, unit_preds = model.predict_energy_batch(raw_h), model.predict_energy_batch(unit_h)
        gap = float((raw_preds - unit_preds).abs().max())
        rows.append({"check": "raw_embedding_predicts_like_training_input", "passed": gap < 1e-3, "real_raw_embeddings": len(raw),
                     "raw_norm_min": r4(float(raw_h.norm(dim=-1).min())), "raw_norm_max": r4(float(raw_h.norm(dim=-1).max())),
                     "max_prediction_gap": r4(gap), "tolerance": 1e-3})

        for row in rows:
            print(f"  UC5 {row['check']:<44} passed={row['passed']}", flush=True)
        self.results["uc5"] = {
            "checks": len(rows),
            "failures": sum(not r["passed"] for r in rows),
            "collapse_threshold": f"mean per-dim std of held-out latents >= {MIN_MEAN_STD} (10% of the VICReg variance margin 1.0) and no dimension below {DEAD_DIM_STD} (the sqrt(1e-4) floor under which VICReg's own std term cannot see a dimension)",
            "rows": rows,
        }
        self.checkpoint()

    # ── Gate ─────────────────────────────────────────────────────────────────
    def gate(self) -> bool:
        r = self.results
        checks: dict[str, bool] = {}
        if "uc1" in r:
            checks["G1 held-out first-attempt MAE below the train-mean baseline (mean over seeds)"] = r["uc1"]["mae_jepa"] < r["uc1"]["mae_mean_baseline"]
        if "uc2" in r:
            u = r["uc2"]
            checks["G2 held-out first-attempt ROC-AUC mean >= 0.60 and worst seed above chance"] = (
                u["auc_mean"] is not None and u["auc_mean"] >= 0.60 and u["auc_min"] > 0.5)
        if "uc3" in r:
            u = r["uc3"]
            new, old = u["mixed_new_default"].get("relative_error_mean"), u["self_pairs_old"].get("relative_error_mean")
            checks[f"G3 with >= {MIN_TRANSITIONS} transitions, transition-aware training beats identity and self-pairs"] = bool(
                u["enough_data"] and new is not None and old is not None and new < 1.0 and new < old)
        if "uc4" in r:
            d = r["uc4"]["decidable_only"]
            checks["G4 intuition pick passes more often than random on decidable tasks"] = bool(
                d["picks"] > 0 and d["intuition_pass_rate"] > d["random_pass_rate"])
        if "uc5" in r:
            checks["G5 all robustness checks pass"] = r["uc5"]["failures"] == 0
        r["gate"] = checks
        r["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.checkpoint()
        print("\nGATE")
        for name, ok in checks.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        return all(checks.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traces", nargs="+", default=[str(p) for p in DEFAULT_TRACES])
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--min-traces", type=int, default=30)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=256, help="full batch: spectral-norm overhead dominates a step, and VICReg statistics want the whole set")
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--weight-decay", type=float, default=0.05)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--d-hidden", type=int, default=64)
    parser.add_argument("--d-latent", type=int, default=16)
    parser.add_argument("--energy-weight", type=float, default=10.0)
    parser.add_argument("--ridge-alpha", type=float, default=1.0)
    parser.add_argument("--threads", type=int, default=1, help="torch CPU threads (1 is fastest for this tiny model on a shared machine)")
    parser.add_argument("--uc", nargs="+", default=["1", "2", "3", "4", "5"], help="Use cases to run, in order")
    parser.add_argument("--out", default=str(ROOT / "results" / "phase2_evolution"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    torch.set_num_threads(args.threads)
    try:
        bench = Bench(args)
    except InsufficientDataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Phase 2 evolution: {bench.results['n_states']} verified states, {bench.results['n_tasks']} tasks, "
          f"{bench.results['n_transitions']} transitions, fail/pass={bench.results['n_verified_fail']}/{bench.results['n_verified_pass']}, "
          f"{bench.results['n_duplicate_traces_dropped']} duplicate traces dropped, first attempts={bench.results['n_first_attempt_states']} "
          f"(fail/pass={bench.results['n_first_attempt_fail']}/{bench.results['n_first_attempt_pass']}), "
          f"d={bench.ds.hidden_dim}", flush=True)
    bench.train_all()
    steps = {"1": bench.uc1_beats_constant, "2": bench.uc2_discrimination, "3": bench.uc3_pairs_ablation,
             "4": bench.uc4_selection, "5": bench.uc5_robustness}
    for key in args.uc:
        steps[key]()
    return 0 if bench.gate() else 1


if __name__ == "__main__":
    sys.exit(main())
