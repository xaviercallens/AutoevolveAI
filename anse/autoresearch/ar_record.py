import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List

@dataclass
class ARRecord:
    id: str
    title: str
    hypothesis: str
    status: str
    fitness_baseline: Optional[float]
    fitness_arh5: Optional[float]
    delta_fitness: Optional[float]
    commit_hash: Optional[str]
    timestamp_start: str
    timestamp_end: Optional[str]
    benchmark: str
    n_problems: int
    n_pass_baseline: int
    n_pass_arh5: int
    vram_peak_gb_baseline: float
    vram_peak_gb_arh5: float
    tts_s_baseline: float
    tts_s_arh5: float
    notes: List[str]
    sha256: str

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, sort_keys=True)

    @classmethod
    def from_json(cls, s: str) -> 'ARRecord':
        d = json.loads(s)
        return cls(**d)

    def compute_sha256(self) -> str:
        d = asdict(self)
        d['sha256'] = ""
        s = json.dumps(d, sort_keys=True)
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    def save(self, path: Path) -> None:
        self.sha256 = self.compute_sha256()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

class ARRecordRegistry:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.records: List[ARRecord] = []
        self.load()

    def load(self) -> None:
        if not self.file_path.exists():
            return
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.records.append(ARRecord.from_json(line))

    def save_all(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            for r in self.records:
                r.sha256 = r.compute_sha256()
                f.write(r.to_json() + '\n')

    def add_record(self, record: ARRecord) -> None:
        self.records.append(record)
        self.save_all()
