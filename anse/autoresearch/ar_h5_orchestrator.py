import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
import json

@dataclass
class AR_H5_Result:
    prompt: str
    answer: Optional[str]
    tree_nodes: int
    branches_killed: int
    sandbox_errors: int
    laya_calls: int
    elapsed_s: float
    vram_peak_gb: float
    success: bool
    trace_path: Optional[Path]

class AR_H5_Orchestrator:
    def __init__(
        self,
        policy: Any,
        value: Any,
        sandbox: Any,
        max_depth: int = 5,
        k: int = 3,
        tau_noul: float = 0.3,
        timeout_s: float = 120.0,
        results_dir: Path = Path("results/ar_h5"),
    ):
        self.policy = policy
        self.value = value
        self.sandbox = sandbox
        self.max_depth = max_depth
        self.k = k
        self.tau_noul = tau_noul
        self.timeout_s = timeout_s
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self, prompt: str) -> AR_H5_Result:
        start_time = time.time()
        
        queue = [{"state": "", "depth": 0}]
        nodes_explored = 0
        branches_killed = 0
        sandbox_errors = 0
        laya_calls = 0
        final_answer = None
        
        while queue and (time.time() - start_time) < self.timeout_s:
            current = queue.pop(0)
            nodes_explored += 1
            
            if current["depth"] >= self.max_depth:
                final_answer = self.policy.synthesize_final(current["state"], prompt)
                break
                
            branches = self.policy.generate_branches(current["state"], prompt, k=self.k)
            nouls, passes = self.value.gate_batch(branches)
            laya_calls += 1
            
            for branch, passed in zip(branches, passes):
                if passed:
                    sandbox_res = self.sandbox.run_auto(branch)
                    if sandbox_res.is_error:
                        sandbox_errors += 1
                        branches_killed += 1
                    else:
                        queue.append({"state": current["state"] + "\n" + branch, "depth": current["depth"] + 1})
                else:
                    branches_killed += 1
                    
        elapsed = time.time() - start_time
        success = final_answer is not None
        
        result = AR_H5_Result(
            prompt=prompt,
            answer=final_answer,
            tree_nodes=nodes_explored,
            branches_killed=branches_killed,
            sandbox_errors=sandbox_errors,
            laya_calls=laya_calls,
            elapsed_s=elapsed,
            vram_peak_gb=self.policy.vram_usage_gb,
            success=success,
            trace_path=None
        )
        
        trace_path = self._save_trace(result)
        result.trace_path = trace_path
        return result
        
    def _save_trace(self, result: AR_H5_Result) -> Path:
        trace_id = int(time.time() * 1000)
        trace_file = self.results_dir / f"trace_{trace_id}.json"
        
        with open(trace_file, "w") as f:
            json.dump({
                "prompt": result.prompt,
                "answer": result.answer,
                "success": result.success,
                "elapsed_s": result.elapsed_s,
                "vram_peak_gb": result.vram_peak_gb
            }, f, indent=2)
            
        return trace_file
