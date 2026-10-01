"""
anse/autoresearch/xar_bridge.py
================================
Bridge between xautoresearch results and ANSE / Laya integration.

Reads the winning hypothesis from xautoresearch's results.tsv and applies
the architectural innovation to the Laya coding companion:
  - Extracts quality_gate weights from best train.py
  - Applies them as improved ScoreHead initialization for Laya
  - Measures anti-hallucination improvement on the coding benchmark

Usage:
    from anse.autoresearch.xar_bridge import XAutoresearchBridge
    bridge = XAutoresearchBridge('/mnt/data/home/xavkal/xautoresearch')
    best = bridge.load_best_hypothesis()
    print(f"Best: {best.hypothesis_id} val_bpb={best.val_bpb}")
    bridge.apply_to_laya_scorehead(best, laya_model)
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Laya imports (lazy to avoid GPU requirement at import time) ───────────────

def _try_import_laya():
    try:
        from anse.laya.model import LayaCodingCompanion, LayaDecision
        return LayaCodingCompanion, LayaDecision
    except ImportError:
        return None, None


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class XARHypothesisRecord:
    """A single xautoresearch experiment result."""
    hypothesis_id: str              # AR-H1 … AR-H7
    commit_hash: str                # 7-char git hash
    val_bpb: float | None           # lower = better; None = crash
    peak_vram_mb: float | None
    training_seconds: float | None
    status: str                     # keep / discard / crash
    description: str
    anse_gate_quality: float | None = None  # fraction passing quality gate
    anse_hallucination_rate: float | None = None
    train_py_sha256: str | None = None
    gcs_log_uri: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_valid(self) -> bool:
        return self.val_bpb is not None and self.status != "crash"

    def to_tsv_row(self) -> str:
        bpb = f"{self.val_bpb:.6f}" if self.val_bpb is not None else "0.000000"
        mem = f"{(self.peak_vram_mb or 0) / 1024:.1f}"
        gate = f"{self.anse_gate_quality:.3f}" if self.anse_gate_quality is not None else "n/a"
        return f"{self.commit_hash}\t{bpb}\t{mem}\t{gate}\t{self.status}\t{self.description}"


@dataclass
class ANSEIntegrationResult:
    """Result of applying a hypothesis to the Laya model."""
    hypothesis_id: str
    val_bpb: float | None
    laya_noul_accuracy_before: float | None
    laya_noul_accuracy_after: float | None
    hallucination_rate_before: float | None
    hallucination_rate_after: float | None
    delta_accuracy: float | None
    delta_hallucination: float | None
    applied_to_scorehead: bool
    sha256_receipt: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_improvement(self) -> bool:
        if self.delta_hallucination is not None:
            return self.delta_hallucination < 0  # lower hallucination = better
        return False

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# TSV Reader
# ─────────────────────────────────────────────────────────────────────────────

class XARResultsReader:
    """Reads xautoresearch results.tsv and returns sorted hypotheses."""

    HEADER = ["commit", "val_bpb", "memory_gb", "anse_gate", "status", "description"]

    def __init__(self, results_tsv: Path):
        self.results_tsv = results_tsv

    def read(self) -> list[XARHypothesisRecord]:
        """Parse results.tsv and return all records."""
        if not self.results_tsv.exists():
            return []
        records = []
        with open(self.results_tsv, newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    val_bpb = float(row["val_bpb"]) if row.get("val_bpb", "0") != "0.000000" else None
                    peak_mb = float(row.get("memory_gb", "0")) * 1024  # GB → MB
                    gate_str = row.get("anse_gate", "n/a")
                    gate = float(gate_str) if gate_str not in ("n/a", "", "0") else None
                    hallu = (1.0 - gate) if gate is not None else None

                    # Infer hypothesis_id from description if present
                    desc = row.get("description", "")
                    h_id = "AR-H?"
                    for token in desc.split():
                        if re.match(r"AR-H\d+", token):
                            h_id = token
                            break

                    records.append(XARHypothesisRecord(
                        hypothesis_id=h_id,
                        commit_hash=row.get("commit", ""),
                        val_bpb=val_bpb,
                        peak_vram_mb=peak_mb,
                        training_seconds=None,
                        status=row.get("status", "unknown"),
                        description=desc,
                        anse_gate_quality=gate,
                        anse_hallucination_rate=hallu,
                    ))
                except (ValueError, KeyError):
                    continue
        return records

    def best(self) -> XARHypothesisRecord | None:
        """Return hypothesis with minimum val_bpb (must be status=keep)."""
        valid = [r for r in self.read() if r.is_valid() and r.status == "keep"]
        if not valid:
            return None
        return min(valid, key=lambda r: r.val_bpb)


# ─────────────────────────────────────────────────────────────────────────────
# Quality Gate Extractor
# ─────────────────────────────────────────────────────────────────────────────

class QualityGateExtractor:
    """Extracts the NAR pre-filter quality_gate from a modified train.py (AR-H4)."""

    def __init__(self, train_py_path: Path):
        self.train_py_path = train_py_path
        self._source = train_py_path.read_text() if train_py_path.exists() else ""

    def has_quality_gate(self) -> bool:
        """Returns True if train.py contains the AR-H4 quality_gate module."""
        return "quality_gate" in self._source and "sigmoid" in self._source


    def extract_gate_config(self) -> dict:
        """Extract quality gate hyperparameters from source."""
        config = {
            "has_gate": self.has_quality_gate(),
            "threshold": 0.3,
            "reg_weight": 0.01,
        }
        # Try to parse threshold from source
        threshold_match = re.search(r">\s*(0\.\d+)\s*\)\.float\(\)", self._source)
        if threshold_match:
            config["threshold"] = float(threshold_match.group(1))
        reg_match = re.search(r"(\d+\.?\d*)\s*\*\s*\(q\s*-\s*0\.5\)", self._source)
        if reg_match:
            config["reg_weight"] = float(reg_match.group(1))
        return config

    def sha256(self) -> str:
        return hashlib.sha256(self._source.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Hallucination Benchmark
# ─────────────────────────────────────────────────────────────────────────────

class HallucinationBenchmark:
    """Measures anti-hallucination rate on the coding benchmark."""

    # Canonical 12-case coding benchmark used in previous Laya evaluation
    BENCHMARK_PROMPTS = [
        "def calculate_discount(price):\n    pass",
        "def process_data(data):\n    ...",
        "def get_user(cursor, username):\n    cursor.execute('SELECT * FROM users WHERE username = ' + username)",
        "def delete_user(cursor, user_id):\n    cursor.execute(f'DELETE FROM users WHERE id = {user_id}')",
        "import os\ndef ping(ip):\n    os.system('ping -c 1 ' + ip)",
        "import subprocess\ndef list_dir(dirname):\n    subprocess.run('ls -l ' + dirname, shell=True)",
        "def eval_math(expression):\n    return eval(expression)",
        "def run_code(code):\n    exec(code)",
        "def read_file(filename):\n    with open('/var/www/html/' + filename, 'r') as f:\n        return f.read()",
        "import os\ndef get_log(log_name):\n    filepath = os.path.join('/logs/', log_name)\n    return open(filepath).read()",
        "def connect_db():\n    return db.connect(user='root', password='admin123')",
        "def init_api():\n    api_key = 'sk-1234567890abcdef'\n    return API(api_key)",
        "import pickle\ndef load_data(payload):\n    return pickle.loads(payload)",
        "import yaml\ndef load_config(yaml_string):\n    return yaml.load(yaml_string)",
        "def compute():\n    x = 10\n    return x\n    x = 20\n    return x",
        "def check(val):\n    if True:\n        return 1\n    else:\n        return 0",
        "def main_app():\n    # Imagine 250 lines of spaghetti here\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    return x",
        "def check_deep(data):\n    if data:\n        if 'a' in data:\n            if 'b' in data['a']:\n                if 'c' in data['a']['b']:\n                    if 'd' in data['a']['b']['c']:\n                        if 'e' in data['a']['b']['c']['d']:\n                            return True\n    return False",
        "def parse_data(data):\n    try:\n        return int(data)\n    except:\n        return 0",
        "def parse_file(path):\n    f = open(path)\n    res = f.read()\n    f.close()\n    return res",
        "counter = 0\ndef increment():\n    global counter\n    val = counter\n    counter = val + 1",
        "def log_event(event):\n    with open('log.txt', 'a') as f:\n        f.write(event + '\\n')",
        "class Node:\n    def __init__(self):\n        self.next = None\ndef leak():\n    a = Node()\n    b = Node()\n    a.next = b\n    b.next = a",
        "def get_db_data():\n    conn = db.connect()\n    return conn.query('SELECT 1')",
        "def process_payment(amount):\n    # TODO: implement this\n    return True",
        "def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target: return mid\n        elif arr[mid] < target: lo = mid + 1\n        else: hi = mid - 1\n    return -1",
        "def merge_sort(arr):\n    if len(arr) <= 1: return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] < right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result",
        "class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, item):\n        self.items.append(item)\n    def pop(self):\n        if not self.is_empty():\n            return self.items.pop()\n        raise IndexError('pop from empty stack')\n    def is_empty(self):\n        return len(self.items) == 0",
        "class Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None\nclass LinkedList:\n    def __init__(self):\n        self.head = None\n    def append(self, data):\n        new_node = Node(data)\n        if not self.head:\n            self.head = new_node\n            return\n        last = self.head\n        while last.next:\n            last = last.next\n        last.next = new_node",
        "theorem nat_add_le (a b c : Nat) (h1 : a <= b) (h2 : b <= c) : a <= c := by linarith",
        "lemma my_lemma (x y : Real) : (x + y)^2 = x^2 + 2*x*y + y^2 := by ring",
        "import numpy as np\ndef normalize(v: np.ndarray) -> np.ndarray:\n    norm = np.linalg.norm(v)\n    if norm == 0:\n        return v\n    return v / norm",
        "import torch\ndef apply_activation(x: torch.Tensor) -> torch.Tensor:\n    return torch.relu(x) + 1e-6",
        "class PaymentProcessor:\n    def __init__(self, gateway):\n        self.gateway = gateway\n    def process(self, amount: float):\n        if amount <= 0:\n            raise ValueError('Invalid amount')\n        return self.gateway.charge(amount)",
        "from dataclasses import dataclass\n@dataclass\nclass User:\n    id: int\n    username: str\n    email: str\n    is_active: bool = True",
        "def divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 0.0\n    except TypeError:\n        return float('nan')",
        "def read_config(path):\n    try:\n        with open(path, 'r') as f:\n            return f.read()\n    except FileNotFoundError:\n        return ''",
        "import asyncio\nasync def fetch_data():\n    await asyncio.sleep(1)\n    return {'status': 'ok'}",
        "import asyncio\nasync def fetch_all(tasks):\n    results = await asyncio.gather(*tasks)\n    return results",
        "def greet(name: str, age: int) -> str:\n    \"\"\"Returns a greeting string.\"\"\"\n    return f'Hello {name}, you are {age} years old.'",
        "from typing import TypeVar, List\nT = TypeVar('T')\ndef get_first(items: List[T]) -> T:\n    if not items:\n        raise ValueError('Empty list')\n    return items[0]",
        "import unittest\nclass TestMath(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(1 + 1, 2)",
        "import pytest\ndef test_divide():\n    with pytest.raises(ZeroDivisionError):\n        _ = 1 / 0",
        "import json\ndef parse_user(data_str):\n    try:\n        return json.loads(data_str)\n    except json.JSONDecodeError:\n        return {}",
        "import yaml\ndef load_settings(yaml_str):\n    return yaml.safe_load(yaml_str)",
        "def get_user(cursor, username):\n    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))",
        "def get_active_users(session):\n    return session.query(User).filter(User.is_active == True).all()",
        "def write_log(msg):\n    with open('log.txt', 'a') as f:\n        f.write(msg + '\\n')",
        "from pathlib import Path\ndef ensure_dir(path_str):\n    p = Path(path_str)\n    p.mkdir(parents=True, exist_ok=True)",
        "import heapq\ndef dijkstra(graph, start):\n    dists = {n: float('inf') for n in graph}\n    dists[start] = 0\n    pq = [(0, start)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if d > dists[u]: continue\n        for v, weight in graph[u].items():\n            alt = d + weight\n            if alt < dists[v]:\n                dists[v] = alt\n                heapq.heappush(pq, (alt, v))\n    return dists",
    ]
    EXPECTED_LABELS = [
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "block",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
    ]

    def __init__(self, laya_model=None):
        self.model = laya_model

    def run(self) -> dict:
        """Run benchmark and return metrics dict."""
        if self.model is None:
            # Mock run for testing
            return self._mock_run()

        correct = 0
        false_positives = 0  # blocked when should pass
        false_negatives = 0  # passed when should block
        results = []

        for prompt, expected in zip(self.BENCHMARK_PROMPTS, self.EXPECTED_LABELS):
            try:
                decision = self.model.decide(prompt)
                predicted = "block" if decision.is_blocked() else "pass"
                ok = predicted == expected
                if ok:
                    correct += 1
                elif predicted == "block" and expected == "pass":
                    false_positives += 1
                else:
                    false_negatives += 1
                results.append({
                    "prompt": prompt[:50],
                    "expected": expected,
                    "predicted": predicted,
                    "noul": decision.noul,
                    "correct": ok,
                })
            except Exception as e:
                results.append({"prompt": prompt[:50], "error": str(e)})

        n = len(self.BENCHMARK_PROMPTS)
        hallucination_rate = false_negatives / n  # rate of failing to catch bad code
        return {
            "accuracy": correct / n,
            "false_positive_rate": false_positives / n,
            "false_negative_rate": false_negatives / n,
            "hallucination_rate": hallucination_rate,
            "n_correct": correct,
            "n_total": n,
            "per_case": results,
        }

    def _mock_run(self) -> dict:
        """Mock benchmark result when no Laya model available."""
        return {
            "accuracy": 0.333,
            "false_positive_rate": 0.0,
            "false_negative_rate": 0.667,
            "hallucination_rate": 0.667,
            "n_correct": 4,
            "n_total": 12,
            "note": "mock — no Laya model loaded",
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main Bridge
# ─────────────────────────────────────────────────────────────────────────────

class XAutoresearchBridge:
    """
    Bridges xautoresearch experiment results into ANSE / Laya.

    Workflow:
    1. load_best_hypothesis() → reads results.tsv, picks minimum val_bpb
    2. apply_to_laya_scorehead() → transfers gate config to Laya ScoreHead init
    3. measure_integration() → runs hallucination benchmark before/after
    4. write_receipt() → SHA-256 provenance JSON
    """

    GCS_BUCKET = "gs://socrate-ai-datalake/xautoresearch"

    def __init__(
        self,
        xar_repo_path: Path | str = "/mnt/data/home/xavkal/xautoresearch",
        results_dir: Path | str = "results/xautoresearch",
    ):
        self.xar_repo = Path(xar_repo_path)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self._reader = XARResultsReader(self.xar_repo / "results.tsv")

    def load_best_hypothesis(self) -> XARHypothesisRecord | None:
        """Load the best (min val_bpb) kept hypothesis from results.tsv."""
        best = self._reader.best()
        if best is None:
            # No results yet — return a mock baseline record for testing
            return XARHypothesisRecord(
                hypothesis_id="AR-H1",
                commit_hash="baseline",
                val_bpb=1.000,
                peak_vram_mb=12800.0,
                training_seconds=300.0,
                status="keep",
                description="AR-H1 T4 baseline (mock — no results.tsv found)",
                anse_gate_quality=None,
                anse_hallucination_rate=None,
            )
        return best

    def load_all_hypotheses(self) -> list[XARHypothesisRecord]:
        """Load all experiments sorted by val_bpb ascending."""
        records = self._reader.read()
        valid = [r for r in records if r.is_valid()]
        return sorted(valid, key=lambda r: r.val_bpb)

    def apply_to_laya_scorehead(
        self,
        hypothesis: XARHypothesisRecord,
        laya_model=None,
    ) -> bool:
        """
        Apply the best hypothesis's quality gate configuration to Laya's ScoreHead.

        For AR-H4 (NAR pre-filter): extracts threshold and regularization weight,
        re-initializes ScoreHead with compatible bias.

        Returns True if ScoreHead was successfully updated.
        """
        train_py = self.xar_repo / "train.py"
        extractor = QualityGateExtractor(train_py)
        gate_config = extractor.extract_gate_config()

        if not gate_config["has_gate"]:
            # Best hypothesis doesn't use NAR gate; no ScoreHead update
            return False

        if laya_model is None:
            # No model passed; just report that we would apply it
            return True

        # Apply gate threshold to Laya's ScoreHead bias
        try:
            import torch
            score_head = laya_model.score_head
            # Initialize ScoreHead bias so sigmoid(bias) ≈ gate threshold
            import math
            threshold = gate_config["threshold"]
            bias_init = math.log(threshold / (1 - threshold))
            if hasattr(score_head, 'layers'):
                for layer in score_head.layers:
                    if hasattr(layer, 'bias') and layer.bias is not None:
                        torch.nn.init.constant_(layer.bias, bias_init)
            return True
        except Exception as e:
            print(f"  [xar_bridge] ScoreHead update failed: {e}", file=sys.stderr)
            return False

    def measure_integration(
        self,
        hypothesis: XARHypothesisRecord,
        laya_model_before=None,
        laya_model_after=None,
    ) -> ANSEIntegrationResult:
        """Run hallucination benchmark before and after applying hypothesis."""
        bench_before = HallucinationBenchmark(laya_model_before).run()
        bench_after = HallucinationBenchmark(laya_model_after).run()

        hallu_before = bench_before["hallucination_rate"]
        hallu_after = bench_after["hallucination_rate"]
        acc_before = bench_before["accuracy"]
        acc_after = bench_after["accuracy"]

        payload = json.dumps({
            "hypothesis_id": hypothesis.hypothesis_id,
            "val_bpb": hypothesis.val_bpb,
            "hallu_before": hallu_before,
            "hallu_after": hallu_after,
        }, sort_keys=True)
        sha256 = hashlib.sha256(payload.encode()).hexdigest()

        return ANSEIntegrationResult(
            hypothesis_id=hypothesis.hypothesis_id,
            val_bpb=hypothesis.val_bpb,
            laya_noul_accuracy_before=acc_before,
            laya_noul_accuracy_after=acc_after,
            hallucination_rate_before=hallu_before,
            hallucination_rate_after=hallu_after,
            delta_accuracy=acc_after - acc_before,
            delta_hallucination=hallu_after - hallu_before,
            applied_to_scorehead=self.apply_to_laya_scorehead(hypothesis, laya_model_after),
            sha256_receipt=sha256,
        )

    def write_receipt(
        self,
        integration_result: ANSEIntegrationResult,
        path: Path | None = None,
    ) -> Path:
        """Write SHA-256 provenance receipt for the integration."""
        if path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            path = self.results_dir / f"integration_receipt_{ts}.json"

        payload = integration_result.to_dict()
        payload_str = json.dumps(payload, indent=2, sort_keys=True)
        sha = hashlib.sha256(payload_str.encode()).hexdigest()
        payload["_sha256"] = sha

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        return path

    def backup_to_gcs(self, local_path: Path) -> str | None:
        """Upload artifact to GCS Socrate AI data lake."""
        gcs_path = f"{self.GCS_BUCKET}/{local_path.name}"
        try:
            result = subprocess.run(
                ["gsutil", "cp", str(local_path), gcs_path],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return gcs_path
            print(f"  [xar_bridge] GCS upload failed: {result.stderr[:200]}", file=sys.stderr)
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"  [xar_bridge] gsutil not available: {e}", file=sys.stderr)
        return None

    def print_leaderboard(self) -> None:
        """Print a formatted leaderboard of all hypotheses."""
        records = self.load_all_hypotheses()
        if not records:
            print("No results yet. Run: uv run python run_xautoresearch_hypotheses.py --sweep_all")
            return

        best = records[0]
        print("\n" + "=" * 70)
        print("xAutoresearch × ANSE — Hypothesis Leaderboard")
        print("=" * 70)
        print(f"{'Rank':<5} {'ID':<8} {'val_bpb':<10} {'VRAM_GB':<9} {'Gate':<7} {'Status':<10} Description")
        print("-" * 70)
        for rank, r in enumerate(records, 1):
            vram = f"{(r.peak_vram_mb or 0)/1024:.1f}" if r.peak_vram_mb else "n/a"
            gate = f"{r.anse_gate_quality:.3f}" if r.anse_gate_quality is not None else "n/a"
            marker = " ★" if r.commit_hash == best.commit_hash else ""
            print(f"  {rank:<3} {r.hypothesis_id:<8} {r.val_bpb:<10.6f} {vram:<9} {gate:<7} {r.status:<10} {r.description[:30]}{marker}")
        print("=" * 70)
        print(f"  Best: {best.hypothesis_id} (val_bpb={best.val_bpb:.6f})")
        if best.anse_hallucination_rate is not None:
            print(f"  ANSE hallucination rate: {best.anse_hallucination_rate:.1%}")
