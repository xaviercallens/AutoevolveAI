import hashlib
import json
from pathlib import Path

L = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/DH-Psi2")
r = json.loads((L / "result.json").read_text())
fs = r["files_sha256"]
bad, missing = [], []
for k, v in fs.items():
    p = L / k
    if not p.exists():
        missing.append(k)
        continue
    if hashlib.sha256(p.read_bytes()).hexdigest() != v:
        bad.append(k)
print("entries", len(fs), "missing", missing, "mismatch", bad)
listed = set(fs)
on_disk = {str(p.relative_to(L)) for p in L.rglob("*") if p.is_file() and "__pycache__" not in str(p)}
print("on disk not listed:", sorted(on_disk - listed - {"result.json"}))
print("prereg sha in result:", r["preregistration_sha256"])
print("start", (L / "logs/prereg_sha_start.txt").read_text().strip())
print("end", (L / "logs/prereg_sha_end.txt").read_text().strip())
