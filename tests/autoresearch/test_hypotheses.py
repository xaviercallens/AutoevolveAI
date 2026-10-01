import pytest
from pathlib import Path
from anse.autoresearch.hypotheses.base import HypothesisBase
from anse.autoresearch.hypotheses.ar_h1_baseline import AR_H1_Baseline
from anse.autoresearch.hypotheses.ar_h2_gqa import AR_H2_GQA
from anse.autoresearch.hypotheses.ar_h4_nar_prefilter import AR_H4_NARPrefilter
from anse.autoresearch.hypothesis_runner import HypothesisRunner

@pytest.fixture
def mock_train_py(tmp_path):
    train_py = tmp_path / "train.py"
    train_py.write_text(
        "class GPT(nn.Module):\n"
        "    def __init__(self, config):\n"
        "        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)\n"
        "\n"
        "n_kv_head: int = 6\n"
        "window_pattern: str = 'SSSL'\n"
        "Muon(lr=0.02)\n"
        "learning_rate = 0.02\n"
        "print('ok')\n"
    )
    return train_py

def test_ar_h1_apply(mock_train_py):
    hyp = AR_H1_Baseline()
    res = hyp.apply(mock_train_py)
    assert res == mock_train_py.read_text()

def test_ar_h2_gqa_patch(mock_train_py):
    hyp = AR_H2_GQA()
    res = hyp.apply(mock_train_py)
    assert "n_kv_head: int = 2" in res
    assert "n_kv_head: int = 6" not in res

def test_ar_h4_narfilter_apply(mock_train_py):
    hyp = AR_H4_NARPrefilter()
    res = hyp.apply(mock_train_py)
    assert "quality_gate" in res

def test_hypothesis_sha256():
    hyp = HypothesisBase()
    content = "test content"
    assert hyp.sha256(content) == hyp.sha256(content)
    assert hyp.sha256(content) != hyp.sha256(content + "1")

def test_hypothesis_runner_cpu_mock(tmp_path):
    train_py = tmp_path / "train.py"
    # A tiny script that parses correctly and prints 'ok'
    train_py.write_text("print('ok')")
    
    runner = HypothesisRunner(train_py)
    # We will just test with H1 baseline which makes no changes
    hyp = AR_H1_Baseline()
    res = runner.run_cpu_validation(hyp)
    
    assert res.status == 'cpu_validated', f"Failed with notes: {res.notes}"
