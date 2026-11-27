import re, json
from pathlib import Path
R = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
FC = R / "formal_cert"
pats = {
    "skipKernelTC": r"skipKernelTC",
    "addDecl": r"addDecl",
    "native_decide": r"native_decide",
    "implemented_by": r"implemented_by|implementedBy",
    # extra, reported separately
    "ofReduceBool": r"ofReduceBool|Lean\.trustCompiler",
    "axiom_decl": r"^\s*(private\s+|protected\s+)?axiom\b",
    "unsafe_or_extern": r"\bunsafe\b|@\[extern|\bopaque\b",
    "sorry": r"\bsorry\b|\badmit\b",
    "debug_opts": r"set_option\s+debug\.",
}
hits = []
nfiles = 0
for sub in ["Triangular", "Autoresearch", "Programmes"]:
    for p in sorted((FC / sub).rglob("*.lean")):
        if "Controls" in p.name or "Reject" in p.name:
            continue
        nfiles += 1
        for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            for k, rx in pats.items():
                if re.search(rx, line):
                    hits.append({"kind": k, "file": str(p.relative_to(R)), "line": i, "text": line.strip()[:200]})
out = R / "results/kernel_replay_2026-10-26/grep_hits.json"
out.write_text(json.dumps({"files_scanned": nfiles, "hits": hits}, indent=1))
import collections
print(nfiles, collections.Counter(h["kind"] for h in hits))
for h in hits:
    print(h["kind"], h["file"], h["line"], h["text"][:120])
