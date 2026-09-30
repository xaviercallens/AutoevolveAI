"""
tests/test_xar_bridge.py
=========================
Unit tests for the xAutoresearch ↔ ANSE bridge.
All tests run on CPU without GPU, GCS, or model downloads.
"""

import json
import tempfile
from pathlib import Path

import pytest

from anse.autoresearch.xar_bridge import (
    XARHypothesisRecord,
    XARResultsReader,
    QualityGateExtractor,
    HallucinationBenchmark,
    XAutoresearchBridge,
    ANSEIntegrationResult,
)


# ── Sample TSV content ─────────────────────────────────────────────────────────

SAMPLE_TSV = """\
commit\tval_bpb\tmemory_gb\tanse_gate\tstatus\tdescription
abc1234\t0.998000\t12.5\tn/a\tkeep\tAR-H1 T4 baseline
def5678\t0.995000\t12.3\tn/a\tkeep\tAR-H2 GQA: n_kv_head=2
ghi9012\t0.989000\t12.8\t0.820\tkeep\tAR-H4 quality_gate: NAR pre-filter
jkl3456\t0.980000\t12.5\tn/a\tkeep\tAR-H7 window=SSSS: all sliding
mno7890\t0.000000\t0.0\tn/a\tcrash\tAR-H5 OOM on T4
"""

SAMPLE_TRAIN_PY_WITH_GATE = """\
import torch
import torch.nn as nn

class GPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.quality_gate = nn.Linear(512, 1, bias=False)

    def forward(self, x, targets):
        hidden = x
        q = torch.sigmoid(self.quality_gate(hidden)).squeeze(-1)
        loss_per_token = nn.CrossEntropyLoss(reduction='none')(x, targets)
        loss = (loss_per_token * (q > 0.3).float()).mean()
        loss += 0.01 * (q - 0.5).pow(2).mean()
        return loss
"""

SAMPLE_TRAIN_PY_NO_GATE = """\
import torch
import torch.nn as nn

class GPT(nn.Module):
    def forward(self, x, targets):
        return nn.CrossEntropyLoss()(x, targets)
"""


# ── XARHypothesisRecord ────────────────────────────────────────────────────────

def test_record_is_valid_with_bpb():
    r = XARHypothesisRecord(
        "AR-H4", "abc1234", 0.989, 12800.0, 300.0, "keep", "test"
    )
    assert r.is_valid()


def test_record_is_invalid_crash():
    r = XARHypothesisRecord(
        "AR-H5", "def0000", None, None, None, "crash", "OOM"
    )
    assert not r.is_valid()


def test_record_to_tsv_row():
    r = XARHypothesisRecord(
        "AR-H4", "ghi9012", 0.989, 12800.0, 300.0, "keep", "NAR pre-filter",
        anse_gate_quality=0.82,
    )
    row = r.to_tsv_row()
    parts = row.split("\t")
    assert parts[0] == "ghi9012"
    assert parts[1] == "0.989000"
    assert parts[4] == "keep"
    assert "NAR" in parts[5]


# ── XARResultsReader ───────────────────────────────────────────────────────────

def test_reader_parses_tsv():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        f.write(SAMPLE_TSV)
        tsv_path = Path(f.name)

    try:
        reader = XARResultsReader(tsv_path)
        records = reader.read()
        assert len(records) == 5
        valid = [r for r in records if r.is_valid()]
        assert len(valid) == 4  # crash excluded
    finally:
        tsv_path.unlink()


def test_reader_selects_best():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        f.write(SAMPLE_TSV)
        tsv_path = Path(f.name)

    try:
        reader = XARResultsReader(tsv_path)
        best = reader.best()
        assert best is not None
        assert best.val_bpb == pytest.approx(0.980, abs=0.001)
        assert best.status == "keep"
    finally:
        tsv_path.unlink()


def test_reader_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        f.write("commit\tval_bpb\tmemory_gb\tanse_gate\tstatus\tdescription\n")
        tsv_path = Path(f.name)

    try:
        reader = XARResultsReader(tsv_path)
        assert reader.best() is None
    finally:
        tsv_path.unlink()


def test_reader_nonexistent_file():
    reader = XARResultsReader(Path("/nonexistent/results.tsv"))
    assert reader.read() == []
    assert reader.best() is None


# ── QualityGateExtractor ───────────────────────────────────────────────────────

def test_extractor_detects_gate():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_TRAIN_PY_WITH_GATE)
        py_path = Path(f.name)

    try:
        extractor = QualityGateExtractor(py_path)
        assert extractor.has_quality_gate()
        config = extractor.extract_gate_config()
        assert config["has_gate"] is True
        assert config["threshold"] == pytest.approx(0.3, abs=0.01)
    finally:
        py_path.unlink()


def test_extractor_no_gate():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_TRAIN_PY_NO_GATE)
        py_path = Path(f.name)

    try:
        extractor = QualityGateExtractor(py_path)
        assert not extractor.has_quality_gate()
    finally:
        py_path.unlink()


def test_extractor_sha256_deterministic():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_TRAIN_PY_WITH_GATE)
        py_path = Path(f.name)

    try:
        ext1 = QualityGateExtractor(py_path)
        ext2 = QualityGateExtractor(py_path)
        assert ext1.sha256() == ext2.sha256()
        assert len(ext1.sha256()) == 64
    finally:
        py_path.unlink()


# ── HallucinationBenchmark ─────────────────────────────────────────────────────

def test_benchmark_mock_run():
    bench = HallucinationBenchmark(laya_model=None)
    result = bench.run()
    assert "accuracy" in result
    assert "hallucination_rate" in result
    assert 0.0 <= result["accuracy"] <= 1.0
    assert 0.0 <= result["hallucination_rate"] <= 1.0
    assert result.get("note") == "mock — no Laya model loaded"


def test_benchmark_has_correct_n_total():
    bench = HallucinationBenchmark()
    result = bench.run()
    assert result["n_total"] == 12  # canonical 12-case benchmark


# ── XAutoresearchBridge ────────────────────────────────────────────────────────

def test_bridge_load_best_no_tsv(tmp_path):
    """When no results.tsv exists, returns mock baseline record."""
    bridge = XAutoresearchBridge(
        xar_repo_path=tmp_path / "nonexistent",
        results_dir=tmp_path / "results",
    )
    best = bridge.load_best_hypothesis()
    assert best is not None
    assert best.hypothesis_id == "AR-H1"  # mock baseline
    assert best.val_bpb == pytest.approx(1.0, abs=0.01)


def test_bridge_load_best_from_tsv(tmp_path):
    xar_repo = tmp_path / "xautoresearch"
    xar_repo.mkdir()
    (xar_repo / "results.tsv").write_text(SAMPLE_TSV)

    bridge = XAutoresearchBridge(
        xar_repo_path=xar_repo,
        results_dir=tmp_path / "results",
    )
    best = bridge.load_best_hypothesis()
    assert best is not None
    assert best.val_bpb == pytest.approx(0.980, abs=0.001)


def test_bridge_measure_integration_mock(tmp_path):
    bridge = XAutoresearchBridge(
        xar_repo_path=tmp_path / "xar",
        results_dir=tmp_path / "results",
    )
    hypothesis = XARHypothesisRecord(
        "AR-H4", "test123", 0.989, 12800.0, 300.0, "keep",
        "NAR pre-filter", anse_gate_quality=0.82
    )
    result = bridge.measure_integration(hypothesis)
    assert isinstance(result, ANSEIntegrationResult)
    assert result.hypothesis_id == "AR-H4"
    assert result.val_bpb == pytest.approx(0.989)
    assert len(result.sha256_receipt) == 64


def test_bridge_write_receipt(tmp_path):
    bridge = XAutoresearchBridge(
        xar_repo_path=tmp_path / "xar",
        results_dir=tmp_path / "results",
    )
    hypothesis = XARHypothesisRecord(
        "AR-H4", "test123", 0.989, 12800.0, 300.0, "keep", "NAR pre-filter"
    )
    integration = bridge.measure_integration(hypothesis)
    receipt_path = bridge.write_receipt(integration)

    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text())
    assert "hypothesis_id" in data
    assert "_sha256" in data
    assert len(data["_sha256"]) == 64


def test_bridge_apply_no_gate(tmp_path):
    """apply_to_laya_scorehead returns False when no quality_gate in train.py."""
    xar_repo = tmp_path / "xar"
    xar_repo.mkdir()
    (xar_repo / "train.py").write_text(SAMPLE_TRAIN_PY_NO_GATE)

    bridge = XAutoresearchBridge(
        xar_repo_path=xar_repo,
        results_dir=tmp_path / "results",
    )
    hypothesis = XARHypothesisRecord(
        "AR-H1", "abc", 0.998, None, None, "keep", "baseline"
    )
    result = bridge.apply_to_laya_scorehead(hypothesis, laya_model=None)
    assert result is False


def test_bridge_apply_with_gate(tmp_path):
    """apply_to_laya_scorehead returns True when quality_gate found (no model needed)."""
    xar_repo = tmp_path / "xar"
    xar_repo.mkdir()
    (xar_repo / "train.py").write_text(SAMPLE_TRAIN_PY_WITH_GATE)

    bridge = XAutoresearchBridge(
        xar_repo_path=xar_repo,
        results_dir=tmp_path / "results",
    )
    hypothesis = XARHypothesisRecord(
        "AR-H4", "ghi", 0.989, None, None, "keep", "NAR pre-filter"
    )
    result = bridge.apply_to_laya_scorehead(hypothesis, laya_model=None)
    assert result is True  # gate found, no model = dry apply
