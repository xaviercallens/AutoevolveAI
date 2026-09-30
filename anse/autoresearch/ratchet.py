import json
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .ar_record import ARRecord

LAMBDA_VRAM = 0.02
GAMMA_TTS = 0.001

def compute_fitness(pass_at_1: float, vram_peak_gb: float, tts_s: float) -> float:
    return pass_at_1 - LAMBDA_VRAM * vram_peak_gb - GAMMA_TTS * tts_s

@dataclass
class BenchmarkResult:
    pass_at_1: float
    vram_peak_gb: float
    tts_s: float

@dataclass
class RatchetVerdict:
    status: str
    delta_fitness: float

class RatchetGate:
    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def evaluate(self, baseline: BenchmarkResult, arh5: BenchmarkResult) -> RatchetVerdict:
        fit_base = compute_fitness(baseline.pass_at_1, baseline.vram_peak_gb, baseline.tts_s)
        fit_arh5 = compute_fitness(arh5.pass_at_1, arh5.vram_peak_gb, arh5.tts_s)
        delta = fit_arh5 - fit_base
        status = "ACCEPTED" if delta > 0 else "REJECTED"
        return RatchetVerdict(status=status, delta_fitness=delta)

    def commit_if_accepted(self, verdict: RatchetVerdict, record: ARRecord) -> Optional[str]:
        if verdict.status == "ACCEPTED":
            result_file = self.results_dir / "ratchet_results.json"
            record.status = "ACCEPTED"
            record.delta_fitness = verdict.delta_fitness
            record.sha256 = record.compute_sha256()
            
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(record.to_json())
                
            try:
                subprocess.run(['git', 'add', str(result_file)], check=True)
                msg = f"autoresearch({record.id}): ratchet ACCEPTED, delta_fitness={verdict.delta_fitness:.4f}"
                subprocess.run(['git', 'commit', '-m', msg], check=True)
                res = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
                commit_hash = res.stdout.strip()
                record.commit_hash = commit_hash
                return commit_hash
            except subprocess.CalledProcessError:
                return None
        else:
            record.status = "REJECTED"
            record.delta_fitness = verdict.delta_fitness
            return None
