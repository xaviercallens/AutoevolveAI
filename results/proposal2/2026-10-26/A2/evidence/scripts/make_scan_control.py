"""Append planted escapes to one scratch Lean file, add an `import Lean` line, write a closure json."""
import json
from pathlib import Path

D = Path("/home/callensxavier_gmail_com/proposal2/A2/controls/scan_plant")
target = D / "NavierStokes" / "ComparatorSolution.lean"
src = target.read_text(encoding="utf-8")
plants = (D / "plants.lean.txt").read_text(encoding="utf-8")
target.write_text("import Lean\n" + src + plants, encoding="utf-8")
(D / "closure.json").write_text(json.dumps({"topo_order": ["NavierStokes.Clean", "NavierStokes.ComparatorSolution"]}))
print("planted into", target)
