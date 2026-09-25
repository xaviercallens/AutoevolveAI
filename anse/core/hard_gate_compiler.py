#!/usr/bin/env python3
import subprocess
import os
from anse.core.semantic_gatekeeper import SemanticGatekeeper

class HardGateCompiler:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries
        self.gatekeeper = SemanticGatekeeper()

    def compile_and_verify(self, file_path, llm_callback=None, topic=None):
        """
        Two-Stage Hard-Gate Verification:
        Stage 1: Deterministic Syntax Compilation (Exit Code == 0 via lake build / python3).
        Stage 2: Semantic & Epistemic Audit (Rejection of Hypothesis Smuggling, Vacuous Structures, Missing Operators).
        Assigns E = 10^6 and triggers retry if any stage fails.
        """
        extension = os.path.splitext(file_path)[1]
        
        for attempt in range(self.max_retries):
            # Stage 1: Syntax Compilation
            if extension == '.lean':
                cmd = ["lake", "env", "lean", file_path]
                cwd = "formal"
                actual_full_path = os.path.join("formal", file_path) if not file_path.startswith("formal/") else file_path
            elif extension == '.py':
                cmd = ["python3", file_path]
                cwd = "."
                actual_full_path = file_path
            else:
                return False, "Unsupported extension."

            print(f"[Hard-Gate] Attempt {attempt+1}/{self.max_retries} for {file_path}")
            res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            output = res.stderr if res.stderr else res.stdout
            
            if res.returncode != 0:
                print(f"[Hard-Gate Stage 1 - Syntax FAILED]: {file_path}. Error:\n{output[:200]}...")
                if llm_callback:
                    print("[Hard-Gate] Requesting LLM correction for Syntax...")
                    llm_callback(file_path, output)
                    continue
                else:
                    return False, f"Compilation failed: {output}"

            # Stage 2: Semantic & Epistemic Hard-Gate
            if os.path.exists(actual_full_path):
                with open(actual_full_path, "r", encoding="utf-8") as f:
                    code_content = f.read()
                
                if extension == '.lean':
                    sem_passed, sem_violations, penalty_energy = self.gatekeeper.audit_lean_code(code_content, topic=topic)
                else:
                    sem_passed, sem_violations, penalty_energy = self.gatekeeper.audit_python_code(code_content)

                if not sem_passed:
                    err_msg = "\n".join([f"[{v.rule}] {v.message}" for v in sem_violations])
                    print(f"[Hard-Gate Stage 2 - Semantic REJECTED: E={penalty_energy:.0f}]:\n{err_msg}")
                    if llm_callback:
                        print("[Hard-Gate] Requesting LLM correction for Epistemic/Semantic Smuggling...")
                        llm_callback(file_path, f"SEMANTIC HARD-GATE REJECTION:\n{err_msg}")
                        continue
                    else:
                        return False, f"Semantic audit rejected: {err_msg}"

            print(f"[Hard-Gate] SUCCESS: {file_path} passed both Syntax & Semantic Audits.")
            return True, "Success"
                    
        print(f"[Hard-Gate] FATAL: Failed to verify {file_path} after {self.max_retries} attempts. Pipeline Halted.")
        return False, "Compilation / Semantic validation blocked."
