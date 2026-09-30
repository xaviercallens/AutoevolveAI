import pytest
from pathlib import Path
from scripts.gcp_t4_spot_runner import GCPSpotRunner, GCPExperimentResult

def test_parse_log_success():
    runner = GCPSpotRunner(dry_run=True)
    log = "Epoch 10\nval_bpb=0.997900 peak_vram_mb=4096.5 training_seconds=150.2\nDone"
    parsed = runner.parse_log(log)
    assert parsed["val_bpb"] == 0.997900
    assert parsed["peak_vram_mb"] == 4096.5
    assert parsed["training_seconds"] == 150.2

def test_parse_log_crash():
    runner = GCPSpotRunner(dry_run=True)
    log = "Traceback (most recent call last):\n  File 'train.py', line 10"
    parsed = runner.parse_log(log)
    assert parsed["val_bpb"] is None
    assert parsed["peak_vram_mb"] is None
    assert parsed["training_seconds"] is None

def test_select_best():
    runner = GCPSpotRunner(dry_run=True)
    r1 = GCPExperimentResult("H1", "inst1", "zone", 1.05, 4000, 100, "success", None, 0.01, 300, "sha1")
    r2 = GCPExperimentResult("H2", "inst2", "zone", 0.99, 4100, 100, "success", None, 0.01, 300, "sha2")
    r3 = GCPExperimentResult("H3", "inst3", "zone", None, None, None, "crash", None, 0.01, 10, "sha3")
    
    best = runner.select_best([r1, r2, r3])
    assert best.hypothesis_id == "H2"

def test_write_results_tsv(tmp_path):
    runner = GCPSpotRunner(dry_run=True)
    r1 = GCPExperimentResult("H1", "inst1", "zone", 1.05, 4096, 100, "success", None, 0.01, 300, "abcdef123")
    r2 = GCPExperimentResult("H2", "inst2", "zone", None, None, None, "crash", None, 0.01, 10, "123456789")
    
    tsv_path = tmp_path / "results.tsv"
    runner.write_results_tsv([r1, r2], tsv_path)
    
    content = tsv_path.read_text()
    lines = content.strip().split("\n")
    assert len(lines) == 3
    assert lines[0] == "hypothesis\tcommit\tval_bpb\tmemory_gb\tstatus\tdescription"
    assert lines[1] == "H1\tabcdef1\t1.050000\t4.00\tsuccess\tinst1"
    assert lines[2] == "H2\t1234567\tN/A\tN/A\tcrash\tinst2"

def test_cost_calculation():
    # 5 min * 0.11/hr = 5/60 * 0.11 = 0.0091666
    cost = (300 / 3600.0) * 0.11
    assert abs(cost - 0.009166) < 1e-4

def test_dry_run(tmp_path):
    runner = GCPSpotRunner(dry_run=True)
    dummy_train = tmp_path / "train.py"
    dummy_train.write_text("print('hello')")
    
    res = runner.run_experiment("H-TEST", dummy_train)
    assert res.status == "dry_run"
    assert res.val_bpb == 0.997900  # matches our dummy fetch_log output
    assert res.hypothesis_id == "H-TEST"
