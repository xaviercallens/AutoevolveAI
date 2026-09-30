from pathlib import Path
from .base import HypothesisBase

class AR_H7_SlidingWindow(HypothesisBase):
    ID = "AR-H7"
    TITLE = "Sliding Window Attention"
    DESCRIPTION = "Change window_pattern to all sliding window (SSSS)"
    
    def apply(self, train_py_path: Path) -> str:
        content = train_py_path.read_text()
        content = content.replace('window_pattern: str = "SSSL"', 'window_pattern: str = "SSSS"')
        return content
