"""Run a JAX script on the Cloud TPU named by AUTOEVOLVE_TPU_NAME / AUTOEVOLVE_TPU_ZONE.

Ships local files to the TPU VM home directory, runs one command inside `~/venv-tpu`, and
fetches result files back. Uses `gcloud compute tpus tpu-vm scp/ssh --internal-ip` (the dev VM
and the TPU share a VPC). Every step is a real subprocess; failures raise `TPURunError`
carrying the actual stderr -- nothing is retried or faked.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class TPURunError(RuntimeError):
    """A gcloud step failed; the message carries its real output."""


@dataclass(frozen=True)
class TPUTarget:
    name: str
    zone: str
    internal_ip: bool = True

    @classmethod
    def from_env(cls) -> TPUTarget:
        name = os.environ.get("AUTOEVOLVE_TPU_NAME", "").strip()
        zone = os.environ.get("AUTOEVOLVE_TPU_ZONE", "").strip()
        if not name or not zone:
            raise TPURunError("set AUTOEVOLVE_TPU_NAME and AUTOEVOLVE_TPU_ZONE")
        return cls(name, zone)


def _gcloud() -> str:
    exe = shutil.which("gcloud")
    if exe is None:
        raise TPURunError("gcloud not on PATH")
    return exe


def _base(verb: str) -> list[str]:
    return [_gcloud(), "compute", "tpus", "tpu-vm", verb]


def _flags(target: TPUTarget) -> list[str]:
    flags = [f"--zone={target.zone}"]
    if target.internal_ip:
        flags.append("--internal-ip")
    return flags


def _run(cmd: list[str], timeout_s: float) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired as exc:
        raise TPURunError(f"timed out after {timeout_s}s: {cmd[3:6]}") from exc
    if result.returncode != 0:
        raise TPURunError(f"exit {result.returncode}: {(result.stderr or result.stdout).strip()[-800:]}")
    return result


def upload(target: TPUTarget, files: list[Path], timeout_s: float = 300.0) -> None:
    if not files:
        return
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise TPURunError(f"local files missing: {missing}")
    cmd = [*_base("scp"), *_flags(target), *map(str, files), f"{target.name}:~/"]
    _run(cmd, timeout_s)


def fetch(target: TPUTarget, remote_names: list[str], dest: Path, timeout_s: float = 300.0) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    for name in remote_names:
        cmd = [*_base("scp"), *_flags(target), f"{target.name}:~/{name}", str(dest)]
        _run(cmd, timeout_s)
    return [dest / Path(n).name for n in remote_names]


def run_command(target: TPUTarget, command: str, timeout_s: float = 600.0) -> str:
    """Run `command` inside ~/venv-tpu on the TPU VM; return stdout. Raises on non-zero exit."""
    remote = f". ~/venv-tpu/bin/activate && {command}"
    cmd = [*_base("ssh"), target.name, *_flags(target), f"--command={remote}"]
    return _run(cmd, timeout_s).stdout


def run_job(
    target: TPUTarget,
    files: list[Path],
    command: str,
    results: list[str],
    dest: Path,
    timeout_s: float = 600.0,
) -> tuple[str, list[Path]]:
    """Upload `files`, run `command`, fetch `results` into `dest`. Returns (stdout, fetched paths)."""
    upload(target, files)
    out = run_command(target, command, timeout_s)
    return out, (fetch(target, results, dest) if results else [])
