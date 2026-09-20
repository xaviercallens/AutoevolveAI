from __future__ import annotations

import json

import execution_attestation
from execution_attestation import (
    _audit_single_file,
    generate_attestation_proof,
)


class TestAttestationGate:
    def test_pass_stub_detected(self, tmp_path):
        f = tmp_path / "stub.py"
        f.write_text("def f():\n    pass\n")
        violations = _audit_single_file(str(f))
        assert len(violations) > 0

    def test_ellipsis_stub_detected(self, tmp_path):
        f = tmp_path / "stub.py"
        f.write_text("def f():\n    ...\n")
        violations = _audit_single_file(str(f))
        assert len(violations) > 0

    def test_not_implemented_detected(self, tmp_path):
        f = tmp_path / "stub.py"
        f.write_text("def f():\n    raise NotImplementedError\n")
        violations = _audit_single_file(str(f))
        assert len(violations) > 0

    def test_mock_data_detected(self, tmp_path):
        f = tmp_path / "prod.py"
        f.write_text("def f():\n    mock_user = {'id': 1}\n    return mock_user\n")
        violations = _audit_single_file(str(f))
        assert len(violations) > 0

    def test_real_implementation_passes(self, tmp_path):
        f = tmp_path / "real.py"
        f.write_text("def add(a, b):\n    return a + b\n")
        violations = _audit_single_file(str(f))
        assert len(violations) == 0

    def test_attestation_proof_generates_token(self, tmp_path, monkeypatch):
        att_file = tmp_path / ".antigravity_attestation"
        monkeypatch.setattr(execution_attestation, "ATTESTATION_FILE", att_file)
        token = generate_attestation_proof("some_module")
        assert isinstance(token, str)
        assert att_file.exists() is True

    def test_attestation_proof_contains_metadata(self, tmp_path, monkeypatch):
        att_file = tmp_path / ".antigravity_attestation"
        monkeypatch.setattr(execution_attestation, "ATTESTATION_FILE", att_file)
        generate_attestation_proof("some_module")
        data = json.loads(att_file.read_text())
        assert "proof_token" in data
        assert "status" in data
        assert "verifier" in data

    def test_docstring_only_is_stub(self, tmp_path):
        f = tmp_path / "stub.py"
        f.write_text("def f():\n    '''docstring'''\n")
        violations = _audit_single_file(str(f))
        assert len(violations) > 0

    def test_test_files_skip_fake_data_check(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        f = test_dir / "test_stuff.py"
        f.write_text("def f():\n    mock_user = {'id': 1}\n    return mock_user\n")
        violations = _audit_single_file(str(f))
        assert len(violations) == 0
