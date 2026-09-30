from dataclasses import dataclass
from pathlib import Path
import hashlib
import subprocess
import os
import tempfile

@dataclass
class HypothesisResult:
    hypothesis_id: str
    title: str
    val_bpb: float | None
    peak_vram_mb: float | None
    training_seconds: float | None
    status: str
    description: str
    train_py_sha256: str
    notes: str

class HypothesisBase:
    ID: str = "AR-H0"
    TITLE: str = "Base"
    DESCRIPTION: str = ""
    
    def apply(self, train_py_path: Path) -> str:
        """Returns modified train.py content as string."""
        raise NotImplementedError
    
    def cpu_validate(self, modified_train_py: str) -> bool:
        """Quick CPU sanity check: does the code run for 10 steps without crash?"""
        # We'll rely on the HypothesisRunner to do the orchestration, but 
        # this is kept here for interface compatibility per the prompt.
        pass
    
    def sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
