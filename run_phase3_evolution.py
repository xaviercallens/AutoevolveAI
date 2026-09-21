"""
Phase 3 evolution validation: five use cases on self-replacement, measured in the real sandbox.

    python run_phase3_evolution.py

UC1 better child promoted   correct faster child clears equivalence + domination and becomes active
UC2 fast but wrong rejected wrong child is stopped by the equivalence gate; the legacy rule is evaluated too
UC3 A/A noise test          identical code vs itself: false promotions, new rule vs legacy single sample
UC4 rollback                promote, roll back: version, hash, behaviour and lineage are restored/recorded
UC5 LLM-proposed evolution  a real model proposes optimisations; every proposal runs the full pipeline

Correctness claims are audited by an oracle the gates never see: each component's held-out `fuzz`
inputs (tasks/phase3_evolution.yaml), run differentially against the v0001 parent. The hypervisor
decides on hidden tests + benchmark output; the oracle judges whether that decision was right.

Every number is measured in this run. Results are checkpointed to <out>/results.json after every use case.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import yaml

from anse.autopoiesis.hypervisor import (
    AutopoiesisHypervisor,
    BaselineMetrics,
    BenchmarkSample,
    DominationRule,
    EvolutionDecision,
    judge_domination,
    legacy_single_sample_rule,
)
from anse.autopoiesis.registry import ComponentRegistry, RegistryError, code_sha256
from anse.config import get_config
from anse.symbolic.parser import NoCodeFoundError, extract_code
from anse.symbolic.sandbox import SandboxExecutor

ROOT = Path(__file__).parent

LLM_SYSTEM_PROMPT = (
    "You are a Python performance engineer. Reply with exactly one ```python code block that contains "
    "only the optimised function: same name, same parameters, same results for every input. "
    "Standard library only. No tests, no example calls, no print statements, no explanation."
)
LLM_PROMPT = (
    "Contract: {description}\n\n"
    "The current implementation is correct but slow:\n```python\n{parent}```\n\n"
    "Rewrite it with a better algorithm so it runs much faster on large inputs while returning "
    "exactly the same results, including for empty and edge-case inputs."
)
LLM_RETRY_SUFFIX = (
    "\n\nYour previous attempt was rejected.\n```python\n{code}\n```\nReason: {reason}\n{failures}"
    "Fix the problem and reply with the corrected, fast function only."
)


def generate_proposal(model: str, seed: int, prompt: str, system_prompt: str) -> tuple[str, int]:
    """
    One real LLM generation through APIExtractor; returns (reply, embedding dimension).

    Runs in a spawned worker process on purpose: APIExtractor imports torch (~270 MB), and the
    sandbox reports ru_maxrss, which a forked child inherits from its launcher. Keeping torch out
    of the measuring process keeps the RAM term of the energy about the component, not the harness.
    """
    from anse.core.api_extractor import APIExtractor

    cfg = get_config()
    cfg.model.api_model_name = model
    reply, record = APIExtractor(config=cfg.model, seed=seed).extract(
        prompt, system_prompt=system_prompt
    )
    return reply, len(record.to_embedding())


def fmt(samples: list[BenchmarkSample]) -> str:
    return " ".join(f"{s.energy:.1f}" for s in samples)


def legacy_would_swap(parent: BenchmarkSample, child: BenchmarkSample) -> bool:
    """Evaluate the pre-evolution condition on one real parent sample and one real child sample."""
    baseline = BaselineMetrics(parent.energy, parent.duration_ms, parent.peak_ram_mb)
    return legacy_single_sample_rule(child.evaluation, baseline)


class Bench:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.out = Path(args.out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.cfg = get_config()
        self.cfg.model.api_model_name = args.model
        self.sandbox = SandboxExecutor(config=self.cfg.sandbox)
        self.rule = DominationRule(samples=args.samples)
        suite = yaml.safe_load((ROOT / "tasks" / "phase3_evolution.yaml").read_text())["components"]
        self.components: list[dict[str, Any]] = suite[: args.limit] if args.limit else suite
        self.registry_root = self.out / "registry" / time.strftime("run-%Y%m%d-%H%M%S")
        self.results: dict[str, Any] = {
            "phase": 3,
            "model": args.model,
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
            "samples_per_side": args.samples,
            "fuzz_seed": args.fuzz_seed,
            "registry_root": str(self.registry_root.relative_to(ROOT))
            if self.registry_root.is_relative_to(ROOT)
            else str(self.registry_root),
        }
        self.generations = 0
        previous = self.out / "results.json"
        if args.resume and previous.exists():
            # Keep use cases already measured by an interrupted run; only the requested ones are redone.
            old = json.loads(previous.read_text())
            kept = {k: v for k, v in old.items() if k.startswith("uc") and k[2:] not in args.uc}
            self.results.update(kept)
            self.results["started"] = old.get("started", self.results["started"])
            self.generations = int(old.get("generations", 0)) if "uc5" in kept else 0

    def hypervisor(self, uc: str) -> AutopoiesisHypervisor:
        """A fresh registry per use case, seeded with every naive parent as v0001."""
        registry = ComponentRegistry(self.registry_root / uc)
        for c in self.components:
            registry.register(c["name"], c["parent"])
        return AutopoiesisHypervisor(
            registry, sandbox=self.sandbox, rule=self.rule, sandbox_config=self.cfg.sandbox
        )

    def oracle(
        self, hv: AutopoiesisHypervisor, component: dict[str, Any], candidate_code: str
    ) -> dict[str, Any]:
        """
        Held-out differential audit of *candidate_code* against the component's v0001 parent.
        The fuzz inputs are generated here, from the suite file, and are never handed to evolve().
        """
        inputs = eval(
            component["fuzz"], {"rng": random.Random(self.args.fuzz_seed)}
        )  # trusted suite expression
        outcome = hv.differential_test(
            component["parent"], candidate_code, component["entry"], inputs
        )
        return {
            "oracle_inputs": outcome.total,
            "oracle_mismatches": outcome.mismatches,
            "oracle_agrees": outcome.agrees,
            "oracle_example": outcome.examples[0] if outcome.examples else "",
        }

    def checkpoint(self) -> None:
        self.results["generations"] = self.generations
        (self.out / "results.json").write_text(json.dumps(self.results, indent=2))

    @staticmethod
    def decision_row(d: EvolutionDecision) -> dict[str, Any]:
        v = d.verdict
        return {
            "component": d.component,
            "promoted": d.promoted,
            "decided_at": d.stage,
            "reason": d.reason,
            "tests_passed": f"{d.equivalence.child_passed}/{d.equivalence.total}",
            "parent_energy": round(v.parent_median, 2) if v else None,
            "child_energy": round(v.child_median, 2) if v else None,
            "median_paired_gain": round(v.gain, 2) if v else None,
            "noise_threshold": round(v.threshold, 2) if v else None,
            "pair_wins": f"{v.pair_wins}/{v.pairs}" if v else None,
            "speedup": round(d.speedup, 2) if d.speedup is not None else None,
            "parent_version": d.parent_version,
            "child_version": d.child_version,
            "parent_energies": fmt(d.parent_samples),
            "child_energies": fmt(d.child_samples),
        }

    # ── UC1 ──────────────────────────────────────────────────────────────────
    def uc1_better_child_promoted(self) -> None:
        hv = self.hypervisor("uc1")
        rows = []
        for c in self.components:
            d = hv.evolve(c["name"], c["child_fast"], c["tests"], c["workload"])
            row = self.decision_row(d)
            row["active_version_after"] = hv.registry.active_version(c["name"])
            row.update(
                self.oracle(hv, c, hv.registry.active_code(c["name"]))
            )  # audit what is live now
            rows.append(row)
            print(
                f"  UC1 {c['name']:<18} promoted={d.promoted} speedup={row['speedup']} "
                f"E {row['parent_energy']} -> {row['child_energy']} oracle_mismatches={row['oracle_mismatches']}/"
                f"{row['oracle_inputs']} ({d.reason})",
                flush=True,
            )
        speedups = [r["speedup"] for r in rows if r["promoted"]]
        self.results["uc1"] = {
            "title": "Better child is promoted",
            "question": "Does a correct, faster child pass the equivalence gate, dominate the parent beyond noise, and become the active version?",
            "components": len(rows),
            "promoted": sum(r["promoted"] for r in rows),
            "active_is_child": sum(r["active_version_after"] == r["child_version"] for r in rows),
            "live_versions_agreeing_with_held_out_oracle": sum(r["oracle_agrees"] for r in rows),
            "median_speedup": round(statistics.median(speedups), 2) if speedups else 0.0,
            "min_speedup": round(min(speedups), 2) if speedups else 0.0,
            "energy_parent_to_child": {
                r["component"]: round(r["child_energy"] / r["parent_energy"], 3)
                for r in rows
                if r["parent_energy"]
            },
            "rows": rows,
        }
        self.checkpoint()

    # ── UC2 ──────────────────────────────────────────────────────────────────
    def uc2_fast_but_wrong_rejected(self) -> None:
        hv = self.hypervisor("uc2")
        rows = []
        for c in self.components:
            d = hv.evolve(c["name"], c["child_wrong"], c["tests"], c["workload"])
            # What the old hypervisor looked at: energy only. Measured here, never assumed.
            parents, children = hv.measure_interleaved(c["parent"], c["child_wrong"], c["workload"])
            measured = len(parents) == len(children) == self.rule.samples and all(
                s.valid for s in parents + children
            )
            verdict = (
                judge_domination(
                    [s.energy for s in parents], [s.energy for s in children], self.rule
                )
                if measured
                else None
            )
            rows.append(
                {
                    "component": c["name"],
                    "new_pipeline_promoted": d.promoted,
                    "rejected_at": d.stage,
                    "tests_passed": f"{d.equivalence.child_passed}/{d.equivalence.total}",
                    "first_failure": d.equivalence.child_failures[0]
                    if d.equivalence.child_failures
                    else "",
                    "parent_energy": round(verdict.parent_median, 2) if verdict else None,
                    "wrong_child_energy": round(verdict.child_median, 2) if verdict else None,
                    "wrong_child_energy_is_lower": bool(
                        verdict and verdict.child_median < verdict.parent_median
                    ),
                    "legacy_rule_would_swap": legacy_would_swap(parents[0], children[0]),
                    "legacy_parent_sample": round(parents[0].energy, 2),
                    "legacy_child_sample": round(children[0].energy, 2),
                    "domination_alone_would_swap": bool(verdict and verdict.dominates),
                    "benchmark_output_matches_parent": {s.output for s in children}
                    == {s.output for s in parents},
                    "active_version_after": hv.registry.active_version(c["name"]),
                    "lineage_decision": hv.registry.lineage(c["name"])[-1]["decision"],
                    **self.oracle(hv, c, c["child_wrong"]),
                }
            )
            r = rows[-1]
            print(
                f"  UC2 {c['name']:<18} new={'PROMOTED' if d.promoted else 'rejected@' + d.stage} "
                f"tests={r['tests_passed']} E {r['parent_energy']} -> {r['wrong_child_energy']} "
                f"legacy_would_swap={r['legacy_rule_would_swap']}",
                flush=True,
            )
        self.results["uc2"] = {
            "title": "Fast but wrong is rejected",
            "question": "Is a child that is faster because it is wrong stopped by the equivalence gate, even though the legacy energy-only rule would have swapped it in?",
            "wrong_children": len(rows),
            "confirmed_wrong_by_held_out_oracle": sum(r["oracle_mismatches"] > 0 for r in rows),
            "rejected_by_new_pipeline": sum(not r["new_pipeline_promoted"] for r in rows),
            "rejected_at_equivalence_gate": sum(
                r["rejected_at"] == "equivalence" and not r["new_pipeline_promoted"] for r in rows
            ),
            "wrong_child_energy_lower": sum(r["wrong_child_energy_is_lower"] for r in rows),
            "accepted_by_legacy_rule": sum(r["legacy_rule_would_swap"] for r in rows),
            "accepted_by_domination_without_gate": sum(
                r["domination_alone_would_swap"] for r in rows
            ),
            "undetectable_from_benchmark_output": sum(
                r["benchmark_output_matches_parent"] for r in rows
            ),
            "parent_still_active": sum(r["active_version_after"] == 1 for r in rows),
            "rows": rows,
        }
        self.checkpoint()

    # ── UC3 ──────────────────────────────────────────────────────────────────
    def uc3_aa_noise(self) -> None:
        hv = self.hypervisor("uc3")
        rows = []
        for repeat in range(1, self.args.aa_repeats + 1):
            for c in self.components:
                parent_code = hv.registry.active_code(c["name"])
                twin = (
                    parent_code
                    + f"\n# A/A twin {repeat}: byte-different, behaviourally identical\n"
                )
                d = hv.evolve(c["name"], twin, c["tests"], c["workload"])
                pairs = list(zip(d.parent_samples, d.child_samples))
                legacy_pairs = [legacy_would_swap(p, ch) for p, ch in pairs]
                row = self.decision_row(d)
                row.update(
                    {
                        "repeat": repeat,
                        "false_promotion_new_rule": d.promoted,
                        "false_promotion_legacy_rule": legacy_pairs[0] if legacy_pairs else False,
                        "legacy_swaps_over_all_pairs": f"{sum(legacy_pairs)}/{len(legacy_pairs)}",
                        "energy_spread_max_over_min": round(
                            max(s.energy for s in d.parent_samples + d.child_samples)
                            / min(s.energy for s in d.parent_samples + d.child_samples),
                            2,
                        )
                        if pairs
                        else None,
                    }
                )
                rows.append(row)
                print(
                    f"  UC3 {c['name']:<18} #{repeat} new_rule_promoted={d.promoted} wins={row['pair_wins']} "
                    f"legacy_first_sample_swap={row['false_promotion_legacy_rule']} legacy_all={row['legacy_swaps_over_all_pairs']}",
                    flush=True,
                )
        n = len(rows)
        legacy_num = sum(int(r["legacy_swaps_over_all_pairs"].split("/")[0]) for r in rows)
        legacy_den = sum(int(r["legacy_swaps_over_all_pairs"].split("/")[1]) for r in rows)
        spreads = [r["energy_spread_max_over_min"] for r in rows if r["energy_spread_max_over_min"]]
        self.results["uc3"] = {
            "title": "A/A noise test",
            "question": "When the child is identical to the parent, how often does each rule wrongly authorise a swap on this noisy machine?",
            "trials": n,
            "false_promotions_new_rule": sum(r["false_promotion_new_rule"] for r in rows),
            "false_promotions_legacy_rule": sum(r["false_promotion_legacy_rule"] for r in rows),
            "false_promotion_rate_new_rule": round(
                sum(r["false_promotion_new_rule"] for r in rows) / n, 3
            )
            if n
            else 0.0,
            "false_promotion_rate_legacy_rule": round(
                sum(r["false_promotion_legacy_rule"] for r in rows) / n, 3
            )
            if n
            else 0.0,
            "legacy_single_sample_comparisons": legacy_den,
            "legacy_single_sample_swaps": legacy_num,
            "median_energy_spread_max_over_min": round(statistics.median(spreads), 2)
            if spreads
            else 0.0,
            "rows": rows,
        }
        self.checkpoint()

    # ── UC4 ──────────────────────────────────────────────────────────────────
    def uc4_rollback(self) -> None:
        hv = self.hypervisor("uc4")
        reg = hv.registry
        rows = []
        for c in self.components:
            name = c["name"]
            parent_sha = code_sha256(c["parent"])
            d = hv.evolve(name, c["child_fast"], c["tests"], c["workload"])
            row: dict[str, Any] = {
                "component": name,
                "promoted": d.promoted,
                "version_after_promote": reg.active_version(name),
            }
            if d.promoted:
                live = reg.load_active(name)
                row["live_file_after_promote"] = Path(str(live.__file__)).name
                row["live_is_child_code"] = reg.active(name).sha256 == code_sha256(c["child_fast"])
                restored = hv.rollback(name, reason="UC4 rollback drill")
                live = reg.load_active(name)
                events = [e["event"] for e in reg.lineage(name)]
                last = reg.lineage(name)[-1]
                row.update(
                    {
                        "version_after_rollback": restored,
                        "active_hash_is_parent": reg.active(name).sha256 == parent_sha,
                        "active_code_is_parent": reg.active_code(name) == c["parent"],
                        "live_file_after_rollback": Path(str(live.__file__)).name,
                        "probe_result_correct": getattr(live, c["entry"])(*c["probe_args"])
                        == c["probe_expected"],
                        "lineage_events": " > ".join(events),
                        "rollback_logged": last["event"] == "rollback"
                        and last["from_version"] == d.child_version
                        and last["to_version"] == 1,
                        "child_version_file_kept": reg.version_path(
                            name, int(d.child_version or 0)
                        ).exists(),
                    }
                )
                try:
                    hv.rollback(name)
                    row["second_rollback_refused"] = False
                except RegistryError:
                    row["second_rollback_refused"] = True
                # Drill: a corrupted pointer must be rebuilt from the lineage, not trusted or fatal.
                reg.pointer_path(name).write_text("{not json", encoding="utf-8")
                row["corrupted_pointer_recovered_to"] = reg.active_version(name)
                row["repair_logged"] = reg.lineage(name)[-1]["event"] == "repair"
                row["restored"] = bool(
                    restored == 1
                    and row["active_hash_is_parent"]
                    and row["active_code_is_parent"]
                    and row["live_file_after_rollback"] == "v0001.py"
                    and row["probe_result_correct"]
                    and row["rollback_logged"]
                    and row["child_version_file_kept"]
                    and row["second_rollback_refused"]
                    and row["corrupted_pointer_recovered_to"] == 1
                    and row["repair_logged"]
                )
            else:
                row.update({"restored": False, "reason": d.reason})
            rows.append(row)
            print(
                f"  UC4 {name:<18} promoted={d.promoted} restored={row['restored']} "
                f"lineage={row.get('lineage_events', '-')}",
                flush=True,
            )
        self.results["uc4"] = {
            "title": "Rollback",
            "question": "After a promotion, does rollback restore exactly the parent's version, hash and behaviour, and is the move recorded in the lineage?",
            "components": len(rows),
            "promoted_then_rolled_back": sum(r["promoted"] for r in rows),
            "fully_restored": sum(r["restored"] for r in rows),
            "second_rollback_refused": sum(bool(r.get("second_rollback_refused")) for r in rows),
            "corrupted_pointer_repaired": sum(bool(r.get("repair_logged")) for r in rows),
            "rows": rows,
        }
        self.checkpoint()

    # ── UC5 ──────────────────────────────────────────────────────────────────
    def uc5_llm_evolution(self) -> None:
        hv = self.hypervisor("uc5")
        llm = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"))
        rows = []
        for c in self.components[: self.args.uc5_components]:
            prompt = LLM_PROMPT.format(description=c["description"], parent=c["parent"])
            retry_suffix = ""
            for proposal in range(1, self.args.uc5_proposals + 1):
                t0 = time.time()
                reply, embedding_dim = llm.submit(
                    generate_proposal,
                    self.args.model,
                    proposal,
                    prompt + retry_suffix,
                    LLM_SYSTEM_PROMPT,
                ).result()
                self.generations += 1
                row: dict[str, Any] = {
                    "component": c["name"],
                    "proposal": proposal,
                    "seed": proposal,
                    "generation_seconds": round(time.time() - t0, 1),
                    "embedding_dim": embedding_dim,
                }
                try:
                    code = extract_code(reply).code + "\n"
                except NoCodeFoundError:
                    row.update(
                        {
                            "code_extracted": False,
                            "gate_says_correct": False,
                            "oracle_agrees": False,
                            "promoted": False,
                            "decided_at": "extraction",
                            "reason": "no code block in the reply",
                            "code": reply[:600],
                        }
                    )
                    rows.append(row)
                    retry_suffix = LLM_RETRY_SUFFIX.format(
                        code="", reason=row["reason"], failures=""
                    )
                    continue
                d = hv.evolve(c["name"], code, c["tests"], c["workload"])
                row.update(self.decision_row(d))
                row.update(
                    {
                        "code_extracted": True,
                        "gate_says_correct": d.equivalence.eligible and d.stage != "benchmark",
                        "first_failure": d.equivalence.child_failures[0]
                        if d.equivalence.child_failures
                        else "",
                        "code": code,
                    }
                )
                # Independent judge: for a promotion, audit the code that is live in the registry now.
                audited = hv.registry.active_code(c["name"]) if d.promoted else code
                row["audited_live_version"] = d.promoted and audited == code
                row.update(self.oracle(hv, c, audited))
                rows.append(row)
                print(
                    f"  UC5 {c['name']:<18} proposal {proposal}: tests={row['tests_passed']} promoted={d.promoted} "
                    f"speedup={row['speedup']} oracle_mismatches={row['oracle_mismatches']}/{row['oracle_inputs']} "
                    f"({d.stage}: {d.reason})",
                    flush=True,
                )
                self.checkpoint_partial("uc5", rows)
                if d.promoted:
                    break
                failures = "".join(f"- {f}\n" for f in d.equivalence.child_failures)
                retry_suffix = LLM_RETRY_SUFFIX.format(
                    code=code, reason=d.reason, failures=failures
                )
        llm.shutdown()
        promoted = [r for r in rows if r["promoted"]]
        self.results["uc5"] = {
            "title": "LLM-proposed evolution",
            "question": "When a real model proposes the optimisation, how many proposals are correct (by the gate, and by a held-out oracle the gate never sees), how many are promoted, and what speed-up is measured?",
            "components": len({r["component"] for r in rows}),
            "proposals": len(rows),
            "code_extracted": sum(r["code_extracted"] for r in rows),
            "correct_by_gate": sum(r["gate_says_correct"] for r in rows),
            "correct_by_held_out_oracle": sum(r["oracle_agrees"] for r in rows),
            "gate_passed_but_oracle_found_wrong": sum(
                r["gate_says_correct"] and not r["oracle_agrees"] for r in rows
            ),
            "gate_rejected_but_oracle_found_correct": sum(
                r["code_extracted"] and not r["gate_says_correct"] and r["oracle_agrees"]
                for r in rows
            ),
            "promoted": len(promoted),
            "incorrect_promoted": sum(
                r["promoted"] and not (r["oracle_agrees"] and r["audited_live_version"])
                for r in rows
            ),
            "components_improved": len({r["component"] for r in promoted}),
            "speedup_by_component": {r["component"]: r["speedup"] for r in promoted},
            "rows": rows,
        }
        self.checkpoint()

    def checkpoint_partial(self, key: str, rows: list[dict[str, Any]]) -> None:
        """LLM calls are slow: keep finished proposals on disk even if the run is interrupted."""
        (self.out / f"{key}_partial_rows.json").write_text(json.dumps(rows, indent=2))

    # ── Gate ─────────────────────────────────────────────────────────────────
    def gate(self) -> bool:
        r = self.results
        checks: dict[str, bool] = {}
        if "uc1" in r:
            u = r["uc1"]
            checks[
                "G1 every correct faster child is promoted, becomes the active version, and agrees with the parent on the held-out oracle"
            ] = (
                u["components"] > 0
                and u["promoted"] == u["active_is_child"] == u["components"]
                and u["live_versions_agreeing_with_held_out_oracle"] == u["components"]
            )
        if "uc2" in r:
            u = r["uc2"]
            checks[
                "G2 every fast-but-wrong child is rejected at the equivalence gate, while the legacy rule would swap at least one in"
            ] = (
                u["wrong_children"] > 0
                and u["rejected_at_equivalence_gate"]
                == u["parent_still_active"]
                == u["wrong_children"]
                and u["accepted_by_legacy_rule"] > 0
            )
        if "uc3" in r:
            u = r["uc3"]
            checks[
                "G3 zero false promotions of identical code over >= 10 A/A trials under the new rule"
            ] = u["trials"] >= 10 and u["false_promotions_new_rule"] == 0
        if "uc4" in r:
            u = r["uc4"]
            checks[
                "G4 rollback restores the parent's version, hash and behaviour and is logged, for every component"
            ] = u["components"] > 0 and u["fully_restored"] == u["components"]
        if "uc5" in r:
            u = r["uc5"]
            checks[
                "G5 the LLM lands at least one promoted improvement, and the held-out differential oracle finds no promoted version that differs from the original parent"
            ] = u["promoted"] >= 1 and u["incorrect_promoted"] == 0
        r["gate"] = checks
        r["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.checkpoint()
        print("\nGATE")
        for name, ok in checks.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        return all(checks.values())


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default="qwen2.5-coder:1.5b")
    parser.add_argument(
        "--samples",
        type=int,
        default=DominationRule().samples,
        help="Interleaved pairs per comparison",
    )
    parser.add_argument("--aa-repeats", type=int, default=3, help="UC3: A/A trials per component")
    parser.add_argument("--uc5-components", type=int, default=3)
    parser.add_argument("--uc5-proposals", type=int, default=2)
    parser.add_argument(
        "--fuzz-seed", type=int, default=20260921, help="Seed of the held-out oracle's inputs"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Only the first N components (smoke run)"
    )
    parser.add_argument(
        "--uc", nargs="+", default=["1", "2", "3", "4", "5"], help="Use cases to run, in order"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Keep finished use cases from an interrupted run's results.json",
    )
    parser.add_argument("--out", default=str(ROOT / "results" / "phase3_evolution"))
    args = parser.parse_args()

    bench = Bench(args)
    steps = {
        "1": bench.uc1_better_child_promoted,
        "2": bench.uc2_fast_but_wrong_rejected,
        "3": bench.uc3_aa_noise,
        "4": bench.uc4_rollback,
        "5": bench.uc5_llm_evolution,
    }
    for uc in args.uc:
        print(f"\n=== UC{uc} ===", flush=True)
        t0 = time.time()
        steps[uc]()
        print(f"=== UC{uc} done in {time.time() - t0:.0f}s ===", flush=True)
    return 0 if bench.gate() else 1


if __name__ == "__main__":
    sys.exit(main())
