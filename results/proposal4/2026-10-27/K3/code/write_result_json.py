"""Write result.json with sha256 of every file of K3 (and the Lean sources)."""
import hashlib
import json
from pathlib import Path

K3 = Path(__file__).resolve().parents[1]
REPO = K3.parents[3]
files = {}
for p in sorted(K3.rglob("*")):
    if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts:
        files[str(p.relative_to(REPO))] = hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted((REPO / "formal_cert/Programmes/CarbonK3").glob("*.lean")):
    files[str(p.relative_to(REPO))] = hashlib.sha256(p.read_bytes()).hexdigest()
out = {"item": "K3", "outcome": "PARTIAL", "date": "2026-10-31",
       "prereg_sha256": "fc9571ec1eb29f99cd12dd5504efdaaa9dfa55f2b1f1938581573c63a6868699",
       "parent_prereg_sha256": hashlib.sha256((K3.parent / "preregistration.json").read_bytes()).hexdigest(),
       "tiers": {"A_candidate_unaudited": "Lean discrete-case post-cessation CM lemmas",
                 "C": "interval enclosures (b), two-maxima instances (c), hand proofs", "X": "floats, searches"},
       "controls_pass": ["P1", "P2", "P3", "P4", "P5", "closed_form_peak", "N1", "N2", "N3", "N4"],
       "files_sha256": files}
(K3 / "result.json").write_text(json.dumps(out, indent=1))
print(len(files), "files hashed")
