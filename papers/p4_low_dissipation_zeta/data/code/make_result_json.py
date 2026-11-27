import hashlib
import json
from pathlib import Path

root = Path("results/proposal4/2026-10-27/E3")
files = {}
for p in sorted(list(root.rglob("*")) + list(Path("formal_cert/Programmes/LowDissE3").glob("*.lean"))):
    if p.is_file() and p.name not in ("result.json",) and "__pycache__" not in str(p):
        files[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
out = {"item": "E3", "outcome": "KEEP", "tier": "A pending statement lock (Lean root form + engine-level Eq. (1)); C/X numerical link",
       "prereg_sha256": hashlib.sha256((root / "prereg_E3.json").read_bytes()).hexdigest(),
       "parent_prereg_sha256": hashlib.sha256(Path("results/proposal4/2026-10-27/preregistration.json").read_bytes()).hexdigest(),
       "files_sha256": files}
(root / "result.json").write_text(json.dumps(out, indent=1))
print(len(files), "files")
