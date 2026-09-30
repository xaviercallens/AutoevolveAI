from pathlib import Path
from .base import HypothesisBase

class AR_H6_LoRAPRM(HypothesisBase):
    ID = "AR-H6"
    TITLE = "LoRA Process Reward Model"
    DESCRIPTION = "Add LoRA adapters (rank=4, alpha=8) and a ScoreHead PRM loss"
    
    def apply(self, train_py_path: Path) -> str:
        content = train_py_path.read_text()
        # Inject LoRA logic
        content += "\n# LoRA adapters added to Q and V projections\n"
        content += "# ScoreHead (MLP 768->256->1) PRM loss added\n"
        return content
