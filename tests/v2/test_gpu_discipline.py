"""Tests for anse.v2.gpu_discipline (card G-1): every GPU/Ollama runner holds the lease."""

from __future__ import annotations

import string
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from anse.v2.gpu_discipline import (
    SCAN_DIRS,
    code_text,
    gpu_evidence,
    holds_lease,
    launched_scripts,
    offenders,
)

REPO = Path(__file__).resolve().parents[2]

LEASED = (
    "import sys\n"
    "sys.path.insert(0, '/mnt/disks/disk-socrateai-local-1/gpu_lease')\n"
    "from gpu_lease import gpu_lease\n"
    "import torch\n"
    "with gpu_lease('x', 'y'):\n"
    "    m = torch.device('cuda')\n"
)


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ── detector on synthetic trees ──────────────────────────────────────────────


def test_synthetic_offender_found_and_leased_file_ignored(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/bad.py", "import torch\nd = torch.device('cuda')\n")
    _write(tmp_path, "scripts/good.py", LEASED)
    found = offenders(tmp_path)
    assert found == [Path("scripts/bad.py")]
    assert Path("scripts/good.py") not in found


def test_comments_and_docstrings_do_not_count(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/prose.py",
           '"""Runs on cuda via localhost:11434 with OLLAMA_HOST set."""\n'
           "x = 1  # torch.device('cuda') would go here\n"
           "def f():\n"
           '    """Also cuda."""\n'
           "    return x\n")
    assert offenders(tmp_path) == []
    stripped = code_text((tmp_path / "scripts/prose.py").read_text())
    assert "cuda" not in stripped
    assert "x = 1" in stripped
    assert "return x" in stripped


def test_each_marker_flags_and_cpu_pin_does_not(tmp_path: Path) -> None:
    cases = {
        "a.py": "URL = 'http://localhost:11434/api/generate'\n",
        "b.py": "import os\nh = os.environ.get('OLLAMA_HOST')\n",
        "c.py": "import torch\nok = torch.cuda.is_available()\n",
        "d.py": "import torch\ndev = torch.device(name)\n",
        "e.py": "model.to(profile.device)\n",
        "f.py": "t = Trainer(device=profile.device)\n",
    }
    for name, text in cases.items():
        _write(tmp_path, f"scripts/{name}", text)
    _write(tmp_path, "scripts/cpu.py",
           "import torch\ndevice = torch.device(\"cpu\")\nm = M().to(device)\n")
    _write(tmp_path, "scripts/cpu2.py", "import torch\nd = torch.device('cpu')\n")
    _write(tmp_path, "scripts/word.py", "cuda_overhead_mb = 450.0\nprint('CUDA driver')\n")
    found = offenders(tmp_path)
    assert found == sorted(Path("scripts") / n for n in cases)
    assert gpu_evidence(code_text(cases["d.py"])) == ["torch.device"]
    assert gpu_evidence(code_text(cases["f.py"])) == ["resolved device"]
    assert gpu_evidence("device = torch.device('cpu')") == []


def test_orchestrator_launching_a_gpu_runner_is_an_offender(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/train.py", "import torch\nd = torch.device('cuda')\n")
    _write(tmp_path, "scripts/clean.py", "print('no gpu here')\n")
    _write(tmp_path, "scripts/orch.py",
           "import subprocess\n"
           "subprocess.run(['python', 'scripts/train.py'])\n"
           "subprocess.run(['python', \"scripts/clean.py\"])\n")
    _write(tmp_path, "scripts/orch_clean.py",
           "import subprocess\nsubprocess.run(['python', 'scripts/clean.py'])\n")
    _write(tmp_path, "scripts/orch_leased.py",
           "from gpu_lease import gpu_lease\nimport subprocess\n"
           "with gpu_lease('a', 'b'):\n    subprocess.run(['python', 'scripts/train.py'])\n")
    found = offenders(tmp_path)
    assert found == [Path("scripts/orch.py"), Path("scripts/train.py")]
    assert launched_scripts(code_text((tmp_path / "scripts/orch.py").read_text())) == [
        "scripts/clean.py", "scripts/train.py"]


def test_scan_scope_dirs_extensions_and_pycache(tmp_path: Path) -> None:
    _write(tmp_path, "v2_runners/probe.py", "import torch\nd = torch.device('cuda')\n")
    _write(tmp_path, "scripts/sub/deep.py", "x = 'localhost:11434'\n")
    _write(tmp_path, "scripts/__pycache__/ghost.py", "x = 'localhost:11434'\n")
    _write(tmp_path, "scripts/notes.txt", "cuda cuda cuda\n")
    _write(tmp_path, "anse/other.py", "d = torch.device('cuda')\n")
    assert SCAN_DIRS == ("scripts", "v2_runners")
    assert offenders(tmp_path) == [Path("scripts/sub/deep.py"), Path("v2_runners/probe.py")]


def test_missing_dirs_and_empty_tree(tmp_path: Path) -> None:
    assert offenders(tmp_path) == []
    (tmp_path / "scripts").mkdir()
    assert offenders(tmp_path) == []


def test_unparsable_file_is_judged_on_raw_text(tmp_path: Path) -> None:
    broken = "def f(:\n    pass  # cuda\n"
    _write(tmp_path, "scripts/broken.py", broken)
    assert code_text(broken) == broken
    assert offenders(tmp_path) == [Path("scripts/broken.py")]


def test_holds_lease_is_a_code_check_not_a_comment_check() -> None:
    assert holds_lease("from gpu_lease import gpu_lease")
    assert not holds_lease(code_text("# gpu_lease is optional\nx = 1\n"))


def test_multiline_docstring_is_blanked_but_following_code_kept() -> None:
    src = 'def f():\n    """line one\n    cuda line two\n    """\n    return "cuda"\n'
    out = code_text(src)
    assert out.count("cuda") == 1
    assert 'return "cuda"' in out
    assert len(out.splitlines()) == len(src.splitlines())


@given(st.text(alphabet=string.ascii_letters + string.digits + string.punctuation + " ",
               max_size=60))
def test_trailing_comment_never_changes_the_verdict(comment: str) -> None:
    base = "value = compute(1, 2)\n"
    with_comment = f"value = compute(1, 2)  # {comment}\n"
    assert code_text(with_comment).rstrip() == code_text(base).rstrip()
    assert gpu_evidence(code_text(with_comment)) == []


# ── the repository itself ────────────────────────────────────────────────────


def test_repository_has_no_unleased_gpu_runner() -> None:
    """Fails, listing them, whenever a scripts/ or v2_runners/ file touches the GPU or
    Ollama without the shared lease (LL.md). Known offenders on 2026-09-28 were
    scripts/nightly_dream_phase.py and scripts/nightly_retrain_at_5am.py; both now lease."""
    found = offenders(REPO)
    assert (REPO / "scripts" / "nightly_dream_phase.py").exists()
    assert found == [], "unleased GPU/Ollama runners: " + ", ".join(str(p) for p in found)
