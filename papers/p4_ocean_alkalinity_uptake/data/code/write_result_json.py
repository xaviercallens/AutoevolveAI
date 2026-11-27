"""Write result.json with sha256 of every file under K2/ (except result.json itself, pycache, dbg)."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
files = {}
for p in sorted(root.rglob("*")):
    if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts and p.name != "dbg.py":
        files[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
lean = {}
repo = root.parents[3]
for p in sorted((repo / "formal_cert" / "Programmes" / "CarbonateK2").glob("*.lean")):
    lean[str(p.relative_to(repo))] = hashlib.sha256(p.read_bytes()).hexdigest()
meta = json.loads((root / "summary.json").read_text())
meta["files_sha256"] = files
meta["lean_files_sha256"] = lean
meta["parent_preregistration_sha256"] = hashlib.sha256((root.parent / "preregistration.json").read_bytes()).hexdigest()
(root / "result.json").write_text(json.dumps(meta, indent=1) + "\n")
print("files hashed:", len(files))
