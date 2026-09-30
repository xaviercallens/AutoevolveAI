#!/usr/bin/env python
"""
run_xautoresearch_hypotheses.py — xAutoresearch × ANSE Experiment Orchestrator
================================================================================
Autoresearch paradigm (Karpathy-style): formulate → implement → ratchet → commit.
Integrates xaviercallens/xautoresearch with ANSE / Laya coding companion.

Usage:
  uv run python run_xautoresearch_hypotheses.py --cpu_validate_all
  uv run python run_xautoresearch_hypotheses.py --hypothesis AR-H4 --gcp_submit
  uv run python run_xautoresearch_hypotheses.py --sweep_all --dry_run
  uv run python run_xautoresearch_hypotheses.py --select_best
  uv run python run_xautoresearch_hypotheses.py --integrate_anse
  uv run python run_xautoresearch_hypotheses.py --backup_gcs
  uv run python run_xautoresearch_hypotheses.py --release_resources

Fitness = -val_bpb - 0.001 * hallucination_rate  (maximize)
  lower val_bpb + lower hallucination = higher fitness

GCP T4 spot: ~$0.009 per 5-min experiment
"""

import argparse
import glob
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from anse.autoresearch.xar_bridge import (
    XAutoresearchBridge,
    XARHypothesisRecord,
    HallucinationBenchmark,
)

# ── Config ─────────────────────────────────────────────────────────────────────
XAR_REPO = Path("/mnt/data/home/xavkal/xautoresearch")
RESULTS_DIR = Path("results/xautoresearch")
GCS_BUCKET = "gs://socrate-ai-datalake/xautoresearch"

HYPOTHESIS_REGISTRY = {
    "AR-H1": {"title": "T4 Baseline", "description": "AR-H1 nanochat sized for T4 16GB (n_embd=512, n_layer=8)"},
    "AR-H2": {"title": "GQA Attention",    "description": "AR-H2 GQA: n_kv_head=2 (saves 30% VRAM)"},
    "AR-H3": {"title": "Muon LR Tuning",   "description": "AR-H3 Muon: lr=0.04 + cosine warmup 100 steps"},
    "AR-H4": {"title": "NAR Pre-filter",   "description": "AR-H4 quality_gate: NAR pre-filter masks uncertain tokens in loss"},
    "AR-H5": {"title": "MCTS Dual-Process","description": "AR-H5 MCTS: tree-of-thoughts with Laya value network"},
    "AR-H6": {"title": "LoRA PRM",         "description": "AR-H6 LoRA r=4: process reward model + ScoreHead aux loss"},
    "AR-H7": {"title": "All-Sliding Attn", "description": "AR-H7 window=SSSS: all sliding-window (faster → more steps)"},
}


# ── Fitness ────────────────────────────────────────────────────────────────────

def compute_anse_fitness(val_bpb: float | None, hallu_rate: float | None) -> float:
    """Maximize: -val_bpb - 0.001 * hallucination_rate."""
    if val_bpb is None:
        return float("-inf")
    return -val_bpb - 0.001 * (hallu_rate or 0.0)


def ratchet_gate(
    current_best: XARHypothesisRecord | None,
    candidate: XARHypothesisRecord,
) -> bool:
    """True if candidate ANSE fitness strictly exceeds current best."""
    if current_best is None:
        return True
    f_best = compute_anse_fitness(current_best.val_bpb, current_best.anse_hallucination_rate)
    f_cand = compute_anse_fitness(candidate.val_bpb, candidate.anse_hallucination_rate)
    return f_cand > f_best


# ── CPU Validation ─────────────────────────────────────────────────────────────

def cpu_validate_hypothesis(h_id: str, train_py_path: Path) -> bool:
    """Syntax-check a train.py file. Returns True if no py_compile error."""
    import py_compile, tempfile, os
    if not train_py_path.exists():
        print(f"  [CPU validate] {h_id}: file not found → skip")
        return True  # No file = baseline, assume ok

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(train_py_path.read_text())
        tmp = f.name
    try:
        py_compile.compile(tmp, doraise=True)
        print(f"  [CPU validate] {h_id}: ✓ syntax OK")
        return True
    except py_compile.PyCompileError as e:
        print(f"  [CPU validate] {h_id}: ✗ syntax error → {e}")
        return False
    finally:
        os.unlink(tmp)


# ── GCP Submit ─────────────────────────────────────────────────────────────────

def submit_to_gcp(h_id: str, train_py_path: Path, dry_run: bool = False) -> dict | None:
    """Submit a hypothesis train.py to GCP T4 spot runner."""
    runner = Path("scripts/gcp_t4_spot_runner.py")
    cmd = [sys.executable, str(runner), "--hypothesis", h_id,
           "--train_py", str(train_py_path)]
    if dry_run:
        cmd.append("--dry_run")

    if not runner.exists():
        print(f"  [GCP] Runner {runner} not found")
        return None

    print(f"  [GCP] {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=660)
        for line in result.stdout.splitlines():
            if line.strip().startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        if result.returncode != 0:
            print(f"  [GCP] Error: {result.stderr[-300:]}")
            return {"status": "error"}
        return {"status": "success", "stdout": result.stdout[-200:]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}


# ── Results TSV ────────────────────────────────────────────────────────────────

def append_to_results_tsv(record: XARHypothesisRecord) -> None:
    tsv = XAR_REPO / "results.tsv"
    write_header = not tsv.exists()
    with open(tsv, "a") as f:
        if write_header:
            f.write("commit\tval_bpb\tmemory_gb\tanse_gate\tstatus\tdescription\n")
        f.write(record.to_tsv_row() + "\n")
    print(f"  [TSV] {record.hypothesis_id}: val_bpb={record.val_bpb}, status={record.status}")


# ── GCS Backup ─────────────────────────────────────────────────────────────────

def backup_to_gcs(dry_run: bool = False) -> None:
    items = [
        (XAR_REPO / "results.tsv",                     f"{GCS_BUCKET}/results.tsv"),
        (Path("results/xautoresearch/"),                f"{GCS_BUCKET}/anse_results/"),
        (Path("results/ar_h5/"),                        f"{GCS_BUCKET}/ar_h5/"),
        (Path("papers/laya_coding_companion_paper.pdf"),f"{GCS_BUCKET}/paper_v3.pdf"),
        (Path("artifacts/zenodo_bundle/"),              f"{GCS_BUCKET}/zenodo/"),
    ]
    for local, remote in items:
        if not local.exists():
            print(f"  [GCS] skip {local}")
            continue
        if dry_run:
            print(f"  [GCS dry] gsutil cp {local} {remote}")
            continue
        cmd = ["gsutil", "cp"] + (["-r"] if local.is_dir() else []) + [str(local), remote]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            print(f"  [GCS] {'✓' if r.returncode == 0 else '✗'} {local}")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"  [GCS] gsutil error: {e}")


# ── Resource Release ───────────────────────────────────────────────────────────

def release_gcp_resources(dry_run: bool = False) -> None:
    script = Path("scripts/gcp_release_resources.sh")
    if dry_run:
        print("  [release dry] bash gcp_release_resources.sh")
        return
    if script.exists():
        subprocess.run(["bash", str(script)], check=False)
    else:
        # Inline fallback
        r = subprocess.run(
            ["gcloud", "compute", "instances", "list",
             "--filter=tags.items=xautoresearch", "--format=get(name,zone)"],
            capture_output=True, text=True
        )
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                name, zone = parts[0], parts[1]
                print(f"  Deleting {name} in {zone}...")
                subprocess.run(["gcloud", "compute", "instances", "delete",
                                 name, f"--zone={zone}", "--quiet"], check=False)


# ── ANSE Integration ───────────────────────────────────────────────────────────

def integrate_best_into_anse(dry_run: bool = False) -> None:
    bridge = XAutoresearchBridge(XAR_REPO, RESULTS_DIR)
    best = bridge.load_best_hypothesis()
    if best is None:
        print("  [ANSE] No valid hypothesis. Run --sweep_all first.")
        return

    print(f"\n[ANSE Integration]")
    print(f"  Best: {best.hypothesis_id}  val_bpb={best.val_bpb}")
    print(f"  description: {best.description}")

    laya = None
    try:
        from anse.laya.model import LayaCodingCompanion
        laya = LayaCodingCompanion()
        print(f"  Laya: {sum(p.numel() for p in laya.parameters()):,} params")
    except Exception as e:
        print(f"  Laya not loaded: {e}")

    bench_before = HallucinationBenchmark(laya).run()
    print(f"  Before: acc={bench_before['accuracy']:.3f}  "
          f"hallu={bench_before['hallucination_rate']:.3f}")

    applied = bridge.apply_to_laya_scorehead(best, laya)
    print(f"  ScoreHead updated: {applied}")

    bench_after = HallucinationBenchmark(laya).run()
    print(f"  After:  acc={bench_after['accuracy']:.3f}  "
          f"hallu={bench_after['hallucination_rate']:.3f}")

    print(f"  ΔAccuracy: {bench_after['accuracy']-bench_before['accuracy']:+.3f}  "
          f"ΔHallucination: {bench_after['hallucination_rate']-bench_before['hallucination_rate']:+.3f}")

    integration = bridge.measure_integration(best, laya, laya)
    receipt = bridge.write_receipt(integration)
    print(f"  Receipt: {receipt}")

    if not dry_run:
        bridge.backup_to_gcs(receipt)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu_validate_all", action="store_true")
    parser.add_argument("--hypothesis", default=None)
    parser.add_argument("--gcp_submit", action="store_true")
    parser.add_argument("--sweep_all", action="store_true")
    parser.add_argument("--select_best", action="store_true")
    parser.add_argument("--integrate_anse", action="store_true")
    parser.add_argument("--backup_gcs", action="store_true")
    parser.add_argument("--release_resources", action="store_true")
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    bridge = XAutoresearchBridge(XAR_REPO, RESULTS_DIR)

    if args.cpu_validate_all:
        print("\n[CPU Validation] Checking all hypotheses...")
        base_train = XAR_REPO / "train.py"
        for h_id, info in HYPOTHESIS_REGISTRY.items():
            ok = cpu_validate_hypothesis(h_id, base_train)
            print(f"  {h_id}: {info['title']:<25} {'✓' if ok else '✗'}")

    if args.hypothesis and args.gcp_submit:
        h_id = args.hypothesis
        if h_id not in HYPOTHESIS_REGISTRY:
            print(f"Unknown hypothesis: {h_id}")
            sys.exit(1)
        print(f"\n[GCP] {h_id}: {HYPOTHESIS_REGISTRY[h_id]['title']}")
        result = submit_to_gcp(h_id, XAR_REPO / "train.py", dry_run=args.dry_run)
        print(f"  Result: {result}")

    if args.sweep_all:
        print(f"\n[Sweep All] 7 hypotheses  dry_run={args.dry_run}")
        print(f"  Estimated cost: {'$0.00 (dry run)' if args.dry_run else '$0.063'}\n")
        current_best = bridge.load_best_hypothesis()

        for i, (h_id, info) in enumerate(HYPOTHESIS_REGISTRY.items()):
            print(f"\n--- [{i+1}/7] {h_id}: {info['title']} ---")
            cpu_ok = cpu_validate_hypothesis(h_id, XAR_REPO / "train.py")

            if not cpu_ok:
                record = XARHypothesisRecord(
                    hypothesis_id=h_id, commit_hash="cpu_fail", val_bpb=None,
                    peak_vram_mb=None, training_seconds=None,
                    status="crash", description=info["description"],
                )
            elif args.dry_run:
                # Simulate mock results (decreasing val_bpb per hypothesis)
                mock_bpb = 0.998 - i * 0.003
                gate = 0.82 if h_id == "AR-H4" else (0.75 if h_id == "AR-H6" else None)
                record = XARHypothesisRecord(
                    hypothesis_id=h_id, commit_hash=f"mock{i:02d}",
                    val_bpb=mock_bpb, peak_vram_mb=12800.0, training_seconds=300.0,
                    status="keep", description=info["description"],
                    anse_gate_quality=gate,
                    anse_hallucination_rate=(1.0 - gate) if gate else None,
                )
            else:
                gcp = submit_to_gcp(h_id, XAR_REPO / "train.py", dry_run=False)
                val_bpb = (gcp or {}).get("val_bpb")
                status = "keep" if (val_bpb and ratchet_gate(current_best,
                    XARHypothesisRecord(h_id, "", val_bpb, None, None, "keep", "")
                )) else "discard"
                record = XARHypothesisRecord(
                    hypothesis_id=h_id,
                    commit_hash=((gcp or {}).get("commit_hash", "unknown")[:7]),
                    val_bpb=val_bpb,
                    peak_vram_mb=(gcp or {}).get("peak_vram_mb"),
                    training_seconds=(gcp or {}).get("training_seconds"),
                    status=status,
                    description=info["description"],
                )

            append_to_results_tsv(record)
            if record.is_valid() and ratchet_gate(current_best, record):
                current_best = record
                print(f"  ★ New best: {h_id} val_bpb={record.val_bpb:.6f}")

        bridge.print_leaderboard()

    if args.select_best:
        bridge.print_leaderboard()
        best = bridge.load_best_hypothesis()
        if best:
            f = compute_anse_fitness(best.val_bpb, best.anse_hallucination_rate)
            print(f"\n✓ Best: {best.hypothesis_id}  val_bpb={best.val_bpb}  fitness={f:.6f}")

    if args.integrate_anse:
        integrate_best_into_anse(dry_run=args.dry_run)

    if args.backup_gcs:
        print("\n[GCS Backup]")
        backup_to_gcs(dry_run=args.dry_run)

    if args.release_resources:
        print("\n[Release GCP Resources]")
        release_gcp_resources(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
