from pathlib import Path
from .base import HypothesisBase

class AR_H2_GQA(HypothesisBase):
    ID = "AR-H2"
    TITLE = "Grouped Query Attention"
    DESCRIPTION = "Reduce KV heads from 6 to 2 to save VRAM and memory bandwidth"
    
    def apply(self, train_py_path: Path) -> str:
        content = train_py_path.read_text()
        # Find `n_kv_head: int = 6` -> replace with `n_kv_head: int = 2`
        content = content.replace("n_kv_head: int = 6", "n_kv_head: int = 2")
        return content
