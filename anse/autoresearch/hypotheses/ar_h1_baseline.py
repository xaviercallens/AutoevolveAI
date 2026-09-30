from pathlib import Path
from .base import HypothesisBase

class AR_H1_Baseline(HypothesisBase):
    ID = "AR-H1"
    TITLE = "Baseline nanochat"
    DESCRIPTION = "Run train.py as-is to establish reference val_bpb"
    
    def apply(self, train_py_path: Path) -> str:
        return train_py_path.read_text()
