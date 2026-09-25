"""Tests for bootstrap_from_datalake: vendored modules and fetch verification."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.bootstrap_from_datalake import Artifact, fetch


class TestFetchSizeVerification:
    """Verify that fetch() enforces size matching against bucket reports."""

    def test_fetch_wrong_size_raises_with_both_sizes(self, tmp_path: Path) -> None:
        """When downloaded file has wrong size, raise RuntimeError naming both."""
        artifact = Artifact(
            remote="gs://bucket/file.bin",
            local="test/file.bin",
            size_bytes=1000,
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Mock subprocess.run to succeed but simulate wrong file size
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Create actual file with wrong size
            dest.write_bytes(b"x" * 500)

            with pytest.raises(RuntimeError) as exc_info:
                fetch(artifact, tmp_path, force=False)

            error_msg = str(exc_info.value)
            assert "500" in error_msg, f"Got size 500 should be in: {error_msg}"
            assert "1000" in error_msg, f"Expected size 1000 should be in: {error_msg}"
            assert "size mismatch" in error_msg.lower()

    def test_fetch_success_reported_but_file_missing_raises(self, tmp_path: Path) -> None:
        """When subprocess reports success but file doesn't exist, raise RuntimeError."""
        artifact = Artifact(
            remote="gs://bucket/missing.bin",
            local="test/missing.bin",
            size_bytes=1000,
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Mock subprocess.run to report success
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Do NOT create the file

            with pytest.raises(RuntimeError) as exc_info:
                fetch(artifact, tmp_path, force=False)

            error_msg = str(exc_info.value)
            assert "does not exist" in error_msg.lower()
            assert str(dest) in error_msg

    def test_fetch_empty_file_raises(self, tmp_path: Path) -> None:
        """When file exists but is empty (0 bytes), raise RuntimeError."""
        artifact = Artifact(
            remote="gs://bucket/empty.bin",
            local="test/empty.bin",
            size_bytes=0,  # size_bytes=0 means we need to query bucket
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)

        with patch("subprocess.run") as mock_run:
            with patch("scripts.bootstrap_from_datalake.gcloud_size") as mock_size:
                # gcloud_size says the bucket has 100 bytes
                mock_size.return_value = 100
                # subprocess.run succeeds but creates empty file
                mock_run.return_value = MagicMock(returncode=0)
                dest.write_bytes(b"")

                with pytest.raises(RuntimeError) as exc_info:
                    fetch(artifact, tmp_path, force=False)

                error_msg = str(exc_info.value)
                assert "size mismatch" in error_msg.lower() or "empty file" in error_msg.lower()

    def test_fetch_download_failure_raises(self, tmp_path: Path) -> None:
        """When download command fails, raise RuntimeError with stderr."""
        artifact = Artifact(
            remote="gs://bucket/fail.bin",
            local="test/fail.bin",
            size_bytes=1000,
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stderr="Access denied"
            )

            with pytest.raises(RuntimeError) as exc_info:
                fetch(artifact, tmp_path, force=False)

            error_msg = str(exc_info.value)
            assert "download failed" in error_msg.lower()
            assert "Access denied" in error_msg

    def test_fetch_success_returns_path(self, tmp_path: Path) -> None:
        """When fetch succeeds (size matches), return the dest path."""
        artifact = Artifact(
            remote="gs://bucket/good.bin",
            local="test/good.bin",
            size_bytes=100,
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Write file of exact expected size
            dest.write_bytes(b"x" * 100)

            result = fetch(artifact, tmp_path, force=False)

            assert result == dest
            assert result.stat().st_size == 100

    def test_fetch_skip_if_present_with_correct_size(self, tmp_path: Path) -> None:
        """If file exists with correct size and not forced, skip download."""
        artifact = Artifact(
            remote="gs://bucket/cached.bin",
            local="test/cached.bin",
            size_bytes=50,
            purpose="test artifact",
        )
        dest = tmp_path / artifact.local
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"y" * 50)

        with patch("subprocess.run") as mock_run:
            result = fetch(artifact, tmp_path, force=False)

            # subprocess.run should NOT have been called (file was already present)
            mock_run.assert_not_called()
            assert result == dest


class TestVendoredModuleImports:
    """Verify that vendored rl_common can be imported after path wiring."""

    def test_rl_common_importable(self) -> None:
        """rl_common module is importable from the datalake vendor path."""
        import rl_common

        assert rl_common is not None

    def test_rl_common_has_load_cfg(self) -> None:
        """rl_common exposes load_cfg function."""
        import rl_common

        assert callable(rl_common.load_cfg), "load_cfg should be callable"

    def test_rl_common_has_decision_model(self) -> None:
        """rl_common exposes DecisionModel class."""
        import rl_common

        assert hasattr(rl_common, "DecisionModel"), "DecisionModel should exist"
        assert isinstance(rl_common.DecisionModel, type), "DecisionModel should be a class"
