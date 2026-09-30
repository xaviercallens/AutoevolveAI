import os
import subprocess
import tempfile
from pathlib import Path
from .hypotheses.base import HypothesisBase, HypothesisResult
from .hypotheses.ar_h1_baseline import AR_H1_Baseline
from .hypotheses.ar_h2_gqa import AR_H2_GQA
from .hypotheses.ar_h3_muon_lr import AR_H3_MuonLR
from .hypotheses.ar_h4_nar_prefilter import AR_H4_NARPrefilter
from .hypotheses.ar_h6_lora_prm import AR_H6_LoRAPRM
from .hypotheses.ar_h7_sliding_window import AR_H7_SlidingWindow

class HypothesisRunner:
    def __init__(self, xar_train_py: Path, results_dir: Path = Path('results/xautoresearch')):
        self.xar_train_py = xar_train_py
        self.results_dir = results_dir
        self.hypotheses = [
            AR_H1_Baseline(),
            AR_H2_GQA(),
            AR_H3_MuonLR(),
            AR_H4_NARPrefilter(),
            AR_H6_LoRAPRM(),
            AR_H7_SlidingWindow(),
        ]
        
    def run_cpu_validation(self, hyp: HypothesisBase) -> HypothesisResult:
        """Apply hypothesis, write temp train.py, run 10 steps on CPU, verify no crash."""
        modified_content = hyp.apply(self.xar_train_py)
        
        # Inject CPU overrides at the top
        override_str = (
            "import os\n"
            "os.environ['FORCE_CPU_VALIDATE'] = '1'\n"
            "if os.environ.get('FORCE_CPU_VALIDATE') == '1':\n"
            "    os.environ['CUDA_VISIBLE_DEVICES'] = ''\n"
            "    # TIME_BUDGET = 10\n"
            "    # GPTConfig: depth=2, n_embd=64, n_head=2, sequence_len=32\n"
        )
        final_content = override_str + modified_content
        sha256_hash = hyp.sha256(final_content)
        
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write(final_content)
            temp_path = f.name
            
        try:
            # Run with subprocess timeout=30s
            subprocess.run(
                ["uv", "run", "python", temp_path],
                timeout=30,
                check=True,
                capture_output=True,
                text=True
            )
            status = 'cpu_validated'
            notes = ''
        except subprocess.CalledProcessError as e:
            status = 'crash'
            notes = e.stderr
        except subprocess.TimeoutExpired as e:
            status = 'crash'
            notes = 'timeout'
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
        return HypothesisResult(
            hypothesis_id=hyp.ID,
            title=hyp.TITLE,
            val_bpb=None,
            peak_vram_mb=None,
            training_seconds=None,
            status=status,
            description=hyp.DESCRIPTION,
            train_py_sha256=sha256_hash,
            notes=notes
        )
        
    def run_all_cpu_validation(self) -> list[HypothesisResult]:
        """Run CPU validation for all hypotheses."""
        results = []
        for hyp in self.hypotheses:
            res = self.run_cpu_validation(hyp)
            results.append(res)
        return results
        
    def print_summary(self, results: list[HypothesisResult]) -> None:
        """Print table: ID | Title | CPU Valid | Status | Notes"""
        print(f"{'ID':<10} | {'Title':<30} | {'Status':<15} | {'Notes'}")
        print("-" * 80)
        for res in results:
            print(f"{res.hypothesis_id:<10} | {res.title:<30} | {res.status:<15} | {res.notes}")
