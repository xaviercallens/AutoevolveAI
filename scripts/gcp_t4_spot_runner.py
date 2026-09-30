#!/usr/bin/env python
"""
gcp_t4_spot_runner.py — xAutoresearch GCP T4 Spot Orchestrator

Usage:
  uv run python scripts/gcp_t4_spot_runner.py --hypothesis AR-H2 --dry_run
  uv run python scripts/gcp_t4_spot_runner.py --hypothesis AR-H2 --train_py /mnt/data/xautoresearch/train.py
  uv run python scripts/gcp_t4_spot_runner.py --sweep_all

Cost: ~$0.009 per experiment (T4 preemptible, 5 min)
"""

import argparse
import hashlib
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class GCPExperimentResult:
    hypothesis_id: str
    instance_name: str
    zone: str
    val_bpb: float | None      # None if crashed
    peak_vram_mb: float | None
    training_seconds: float | None
    status: str                 # 'success', 'crash', 'preempted', 'timeout', 'dry_run'
    gcs_log_uri: str | None
    cost_usd: float
    elapsed_wall_s: float
    sha256_train_py: str        # SHA-256 of train.py submitted

class GCPSpotRunner:
    PROJECT = "socrate-ai"
    ZONES = ["us-central1-a", "us-central1-b", "us-east1-b"]  # fallback zones
    MACHINE_TYPE = "n1-standard-4"
    ACCELERATOR = "nvidia-tesla-t4"
    COST_PER_HOUR = 0.11  # T4 preemptible USD/hr
    GCS_BUCKET = "gs://socrate-ai-datalake/xautoresearch"
    
    def __init__(self, dry_run: bool = False, max_retries: int = 3):
        self.dry_run = dry_run
        self.max_retries = max_retries
    
    def _run_cmd(self, cmd: list[str]) -> subprocess.CompletedProcess:
        if self.dry_run:
            print("DRY RUN cmd:", " ".join(cmd))
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
        return subprocess.run(cmd, capture_output=True, text=True)

    def create_instance(self, name: str, zone: str, train_py: Path, startup_script: Path, hypothesis_id: str) -> str:
        sha256 = ""
        if train_py.exists():
            sha256 = hashlib.sha256(train_py.read_bytes()).hexdigest()
        
        cmd = [
            "gcloud", "compute", "instances", "create", name,
            f"--project={self.PROJECT}",
            f"--zone={zone}",
            f"--machine-type={self.MACHINE_TYPE}",
            f"--accelerator=type={self.ACCELERATOR},count=1",
            "--maintenance-policy=TERMINATE",
            "--provisioning-model=SPOT",
            "--instance-termination-action=STOP",
            "--image-family=pytorch-latest-gpu",
            "--image-project=deeplearning-platform-release",
            "--boot-disk-size=50GB",
            "--tags=xautoresearch",
            "--scopes=storage-rw",
            f"--metadata-from-file=startup-script={startup_script}",
            f"--metadata=hypothesis={hypothesis_id},train_py_sha={sha256}"
        ]
        
        if self.dry_run:
            print(f"DRY RUN: gcloud compute instances create {name} ...")
        else:
            subprocess.run(cmd, check=True)
            
        return name
    
    def wait_for_completion(self, instance_name: str, zone: str, timeout_s: float = 600) -> str:
        if self.dry_run:
            return "TERMINATED"
            
        start_time = time.time()
        while time.time() - start_time < timeout_s:
            cmd = [
                "gcloud", "compute", "instances", "describe", instance_name,
                f"--zone={zone}",
                "--format=get(status)",
                f"--project={self.PROJECT}"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            status = res.stdout.strip()
            
            if status in ["TERMINATED", "PREEMPTED"]:
                return status
            
            time.sleep(10)
        return "TIMEOUT"
    
    def fetch_log(self, instance_name: str, zone: str) -> str:
        if self.dry_run:
            return "val_bpb=0.997900 peak_vram_mb=4096.5 training_seconds=150.2"
            
        cmd = [
            "gcloud", "compute", "ssh", instance_name,
            f"--zone={zone}",
            f"--project={self.PROJECT}",
            "--command=cat /opt/xautoresearch/run.log || cat ~/run.log"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.stdout
    
    def parse_log(self, log_content: str) -> dict:
        result = {
            "val_bpb": None,
            "peak_vram_mb": None,
            "training_seconds": None
        }
        
        m_val = re.search(r"val_bpb=([\d\.]+)", log_content)
        if m_val:
            result["val_bpb"] = float(m_val.group(1))
            
        m_vram = re.search(r"peak_vram_mb=([\d\.]+)", log_content)
        if m_vram:
            result["peak_vram_mb"] = float(m_vram.group(1))
            
        m_sec = re.search(r"training_seconds=([\d\.]+)", log_content)
        if m_sec:
            result["training_seconds"] = float(m_sec.group(1))
            
        return result
    
    def delete_instance(self, instance_name: str, zone: str) -> None:
        cmd = [
            "gcloud", "compute", "instances", "delete", instance_name,
            f"--zone={zone}",
            f"--project={self.PROJECT}",
            "--quiet"
        ]
        self._run_cmd(cmd)
    
    def backup_to_gcs(self, local_path: Path, gcs_path: str) -> str:
        cmd = ["gsutil", "cp", str(local_path), gcs_path]
        self._run_cmd(cmd)
        return gcs_path
    
    def run_experiment(self, hypothesis_id: str, train_py: Path) -> GCPExperimentResult:
        if not train_py.exists() and not self.dry_run:
            raise FileNotFoundError(f"{train_py} not found")
            
        sha256 = ""
        if train_py.exists():
            sha256 = hashlib.sha256(train_py.read_bytes()).hexdigest()
        
        startup_script = Path("scripts/gcp_t4_startup.sh")
        instance_name = f"xar-{hypothesis_id.lower().replace('_', '-')}-{int(time.time())}"
        
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            zone = self.ZONES[attempt % len(self.ZONES)]
            
            try:
                self.create_instance(instance_name, zone, train_py, startup_script, hypothesis_id)
                status = self.wait_for_completion(instance_name, zone)
                
                if status == "PREEMPTED":
                    self.delete_instance(instance_name, zone)
                    continue
                    
                log_content = self.fetch_log(instance_name, zone)
                parsed = self.parse_log(log_content)
                self.delete_instance(instance_name, zone)
                
                elapsed = time.time() - start_time
                cost = (elapsed / 3600.0) * self.COST_PER_HOUR
                
                final_status = "success" if parsed["val_bpb"] is not None else "crash"
                if self.dry_run:
                    final_status = "dry_run"
                    
                return GCPExperimentResult(
                    hypothesis_id=hypothesis_id,
                    instance_name=instance_name,
                    zone=zone,
                    val_bpb=parsed["val_bpb"],
                    peak_vram_mb=parsed["peak_vram_mb"],
                    training_seconds=parsed["training_seconds"],
                    status=final_status,
                    gcs_log_uri=None,
                    cost_usd=cost,
                    elapsed_wall_s=elapsed,
                    sha256_train_py=sha256
                )
                
            except Exception as e:
                self.delete_instance(instance_name, zone)
                elapsed = time.time() - start_time
                cost = (elapsed / 3600.0) * self.COST_PER_HOUR
                return GCPExperimentResult(
                    hypothesis_id=hypothesis_id,
                    instance_name=instance_name,
                    zone=zone,
                    val_bpb=None,
                    peak_vram_mb=None,
                    training_seconds=None,
                    status=f"error: {str(e)}",
                    gcs_log_uri=None,
                    cost_usd=cost,
                    elapsed_wall_s=elapsed,
                    sha256_train_py=sha256
                )
                
        # If we reach here, we exhausted retries
        elapsed = time.time() - start_time
        cost = (elapsed / 3600.0) * self.COST_PER_HOUR
        return GCPExperimentResult(
            hypothesis_id=hypothesis_id,
            instance_name=instance_name,
            zone=zone,
            val_bpb=None,
            peak_vram_mb=None,
            training_seconds=None,
            status="preempted_max_retries",
            gcs_log_uri=None,
            cost_usd=cost,
            elapsed_wall_s=elapsed,
            sha256_train_py=sha256
        )
    
    def sweep_all(self, hypotheses: dict[str, Path]) -> list[GCPExperimentResult]:
        results = []
        for hyp, path in hypotheses.items():
            results.append(self.run_experiment(hyp, path))
            
        return sorted(results, key=lambda x: (x.val_bpb is None, x.val_bpb))
    
    def select_best(self, results: list[GCPExperimentResult]) -> GCPExperimentResult:
        valid_results = [r for r in results if r.val_bpb is not None]
        if not valid_results:
            return results[0]
        return min(valid_results, key=lambda x: x.val_bpb)
    
    def write_results_tsv(self, results: list[GCPExperimentResult], path: Path) -> None:
        lines = ["hypothesis\tcommit\tval_bpb\tmemory_gb\tstatus\tdescription"]
        for r in results:
            val = f"{r.val_bpb:.6f}" if r.val_bpb is not None else "N/A"
            mem = f"{r.peak_vram_mb/1024:.2f}" if r.peak_vram_mb is not None else "N/A"
            lines.append(f"{r.hypothesis_id}\t{r.sha256_train_py[:7]}\t{val}\t{mem}\t{r.status}\t{r.instance_name}")
            
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis", type=str)
    parser.add_argument("--train_py", type=Path)
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--sweep_all", action="store_true")
    args = parser.parse_args()
    
    runner = GCPSpotRunner(dry_run=args.dry_run)
    
    if args.sweep_all:
        print("Sweeping all... (not fully implemented in CLI demo)")
    elif args.hypothesis and args.train_py:
        res = runner.run_experiment(args.hypothesis, args.train_py)
        print(res)
    elif args.hypothesis and args.dry_run:
        res = runner.run_experiment(args.hypothesis, Path("/tmp/dummy.py"))
        print(res)
