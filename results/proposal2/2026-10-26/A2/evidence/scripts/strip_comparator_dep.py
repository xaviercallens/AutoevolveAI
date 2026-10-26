"""In the build COPY only: drop the Comparator require (and its manifest entries Comparator, lean4export).

No corpus module imports Comparator; the require only provides the `lake exe comparator` tool.
Writes the originals next to the edited files as *.orig for the provenance diff.
"""
import json
import re
from pathlib import Path

P = Path("/home/callensxavier_gmail_com/proposal2/A2/ns-copy")
lf = P / "lakefile.toml"
mf = P / "lake-manifest.json"
lf_src = lf.read_text()
mf_src = mf.read_text()
(P / "lakefile.toml.orig").write_text(lf_src)
(P / "lake-manifest.json.orig").write_text(mf_src)
new_lf, n = re.subn(r'\[\[require\]\]\nname = "Comparator"\nscope = "leanprover"\ngit = "[^"]+"\nrev = "[^"]+"\n\n?', "", lf_src)
assert n == 1, n
lf.write_text(new_lf)
m = json.loads(mf_src)
before = [p["name"] for p in m["packages"]]
m["packages"] = [p for p in m["packages"] if p["name"] not in ("Comparator", "lean4export")]
mf.write_text(json.dumps(m, indent=1) + "\n")
print("removed", sorted(set(before) - {p["name"] for p in m["packages"]}))
