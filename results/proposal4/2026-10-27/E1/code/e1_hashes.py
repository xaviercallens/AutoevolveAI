"""Compute sha256 of every code, data and log file of E1 (excluding the cloned repo's .git) -> ../logs/sha256.json."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WH_USED = ["LICENSE", "README.md", "lib/reactions.ini", "lib/reactivity.py", "lib/fusionlib.py", "lib/cross_section.py",
           "lawson-criterion-paper.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    out: dict[str, str] = {}
    for sub in ("code", "data", "logs", "formal"):
        d = ROOT / sub
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            rel = p.relative_to(ROOT).as_posix()
            if not p.is_file() or "__pycache__" in rel or "/wurzel_hsu_code/" in rel or rel.endswith("sha256.json"):
                continue
            out[rel] = sha(p)
    lean_dir = ROOT.parents[3] / "formal_cert" / "Programmes" / "PbIgnition"
    for p in sorted(lean_dir.glob("*.lean")):
        out[f"formal_cert/Programmes/PbIgnition/{p.name}"] = sha(p)
    out["RESULT.md"] = sha(ROOT / "RESULT.md")
    wh = ROOT / "data" / "downloads" / "wurzel_hsu_code"
    for f in WH_USED:
        out[f"data/downloads/wurzel_hsu_code/{f}"] = sha(wh / f)
    (ROOT / "logs" / "sha256.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(out), "files hashed")


if __name__ == "__main__":
    main()
