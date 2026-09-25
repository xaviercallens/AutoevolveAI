#!/usr/bin/env python3
import subprocess
import os

class HardGateCompiler:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    def compile_and_verify(self, file_path, llm_callback=None):
        """
        Executes a file and blocks until Exit Code == 0.
        If it fails, it feeds the stderr/stdout to llm_callback for correction.
        """
        extension = os.path.splitext(file_path)[1]
        
        for attempt in range(self.max_retries):
            if extension == '.lean':
                cmd = ["lake", "env", "lean", file_path]
                cwd = "formal"
            elif extension == '.py':
                cmd = ["python3", file_path]
                cwd = "."
            else:
                return False, "Unsupported extension."

            print(f"[Hard-Gate] Attempt {attempt+1}/{self.max_retries} for {file_path}")
            res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            
            # Lean 4 outputs errors to stdout sometimes.
            output = res.stderr if res.stderr else res.stdout
            
            if res.returncode == 0:
                print(f"[Hard-Gate] SUCCESS: {file_path} compiled cleanly.")
                return True, "Success"
            else:
                print(f"[Hard-Gate] FAILED: {file_path}. Error:\n{output[:200]}...")
                if llm_callback:
                    print("[Hard-Gate] Requesting LLM correction...")
                    # Simulating LLM correction by writing the callback output to file
                    llm_callback(file_path, output)
                else:
                    break
                    
        print(f"[Hard-Gate] FATAL: Failed to compile {file_path} after {self.max_retries} attempts. Pipeline Halted.")
        return False, "Compilation blocked."
