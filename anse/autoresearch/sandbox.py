import subprocess
import sys
import time
import tempfile
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SandboxResult:
    code: str
    stdout: str
    stderr: str
    returncode: int
    elapsed_s: float
    is_error: bool
    error_type: str  # 'syntax', 'runtime', 'timeout', 'lean4_error', ''

class AR_H5_Sandbox:
    def __init__(
        self,
        python_timeout_s: float = 10.0,
        lean4_timeout_s: float = 30.0,
        max_output_chars: int = 2000,
    ):
        self.python_timeout_s = python_timeout_s
        self.lean4_timeout_s = lean4_timeout_s
        self.max_output_chars = max_output_chars
        
    def _extract_code(self, text: str, lang: str = "python") -> str:
        pattern = rf"```{lang}\n(.*?)\n```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[-1]
        return text

    def run_python(self, code: str) -> SandboxResult:
        code = self._extract_code(code, "python")
        
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            return SandboxResult(
                code=code, stdout="", stderr=str(e), returncode=1,
                elapsed_s=0.0, is_error=True, error_type="syntax"
            )

        start = time.time()
        try:
            process = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=self.python_timeout_s
            )
            elapsed = time.time() - start
            return SandboxResult(
                code=code,
                stdout=process.stdout[:self.max_output_chars],
                stderr=process.stderr[:self.max_output_chars],
                returncode=process.returncode,
                elapsed_s=elapsed,
                is_error=process.returncode != 0,
                error_type="runtime" if process.returncode != 0 else ""
            )
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start
            return SandboxResult(
                code=code,
                stdout=e.stdout.decode()[:self.max_output_chars] if e.stdout else "",
                stderr=e.stderr.decode()[:self.max_output_chars] if e.stderr else "",
                returncode=-1,
                elapsed_s=elapsed,
                is_error=True,
                error_type="timeout"
            )

    def run_lean4(self, proof: str) -> SandboxResult:
        proof = self._extract_code(proof, "lean")
        start = time.time()
        
        with tempfile.NamedTemporaryFile(suffix=".lean", mode="w", delete=False) as f:
            f.write(proof)
            f_path = f.name
            
        try:
            process = subprocess.run(
                ["lake", "env", "lean", f_path],
                capture_output=True,
                text=True,
                timeout=self.lean4_timeout_s
            )
            elapsed = time.time() - start
            Path(f_path).unlink(missing_ok=True)
            
            return SandboxResult(
                code=proof,
                stdout=process.stdout[:self.max_output_chars],
                stderr=process.stderr[:self.max_output_chars],
                returncode=process.returncode,
                elapsed_s=elapsed,
                is_error=process.returncode != 0,
                error_type="lean4_error" if process.returncode != 0 else ""
            )
        except Exception as e:
            elapsed = time.time() - start
            Path(f_path).unlink(missing_ok=True)
            return SandboxResult(
                code=proof,
                stdout="",
                stderr=str(e)[:self.max_output_chars],
                returncode=-1,
                elapsed_s=elapsed,
                is_error=True,
                error_type="lean4_error"
            )

    def run_auto(self, text: str) -> SandboxResult:
        if 'theorem ' in text or 'by ' in text:
            return self.run_lean4(text)
        return self.run_python(text)
        
    def score_penalty(self, result: SandboxResult) -> float:
        return 0.1 if result.is_error else 1.0
