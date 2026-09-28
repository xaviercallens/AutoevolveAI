"""Round-3 response: build two isolated /tmp copies of the frozen H0 pipeline, one per interpreter.

The only patch is the chain output directory of fit_real.py (the original writes to disk 2 and would
overwrite the recorded chains). Results land under /tmp/r3resp/<env>/results/bao_bbn_h0/fit.json,
never under the repository. Run with either interpreter; it only copies files.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run")
BASE = Path("/tmp/r3resp")
OLD = 'CHAINS = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/cosmo3/bao_bbn_h0/chains")'


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def copy_glob(src: Path, dst: Path, patterns: tuple[str, ...]) -> list[str]:
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for pat in patterns:
        for f in sorted(src.glob(pat)):
            if f.is_file():
                shutil.copy2(f, dst / f.name)
                copied.append(f.name)
    return copied


def build(env: str) -> dict[str, object]:
    root = BASE / env
    if root.exists():
        shutil.rmtree(root)
    scripts = copy_glob(WT / "scripts" / "bao_bbn_h0", root / "scripts" / "bao_bbn_h0", ("*.py",))
    res = root / "results" / "bao_bbn_h0"
    inputs = copy_glob(WT / "results" / "bao_bbn_h0", res,
                       ("preregistration.json", "preregistration_amendment_1.json", "rd_camb_table.npz",
                        "rd_camb_validation.json", "anchor_reproduction.json",
                        "fit_attempt1_fittingformula_UNREAD_AT_AMENDMENT.json"))
    copy_glob(WT / "results" / "bao_bbn_h0" / "controls", res / "controls", ("*.json",))
    fr = root / "scripts" / "bao_bbn_h0" / "fit_real.py"
    txt = fr.read_text()
    if OLD not in txt:
        raise SystemExit("CHAINS line not found; refusing to run unpatched")
    fr.write_text(txt.replace(OLD, f'CHAINS = Path("{root}/chains")'))
    (root / "chains").mkdir()
    unchanged = {n: sha(root / "scripts" / "bao_bbn_h0" / n) == sha(WT / "scripts" / "bao_bbn_h0" / n)
                 for n in scripts}
    return {"root": str(root), "scripts_identical_to_repo": unchanged, "inputs": inputs}


def main() -> None:
    BASE.mkdir(exist_ok=True)
    out = {env: build(env) for env in ("cosmo", "pta")}
    (BASE / "setup.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
