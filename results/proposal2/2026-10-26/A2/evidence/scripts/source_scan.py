"""Source-level soundness-escape scan over a set of Lean modules.

usage: source_scan.py <project_root> <closure_json> <out_json> [--all-files]

Comments are stripped (line comments, nested block comments, docstrings) before
matching, and string literals are blanked, so only code counts as a hit. Raw
hits *including* comments are also counted separately for transparency.
"""
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__":
    ROOT = Path(sys.argv[1])
    CLOSURE = json.loads(Path(sys.argv[2]).read_text())
    OUT = Path(sys.argv[3])
    ALL_FILES = "--all-files" in sys.argv

PATTERNS: dict[str, str] = {
    "sorry": r"\bsorry\b",
    "admit": r"\badmit\b",
    "native_decide": r"\bnative_decide\b|\bdecide\s*\+\s*native\b|\bdecide\s*\(\s*config\s*:=\s*\{[^}]*native",
    "ofReduceBool_trustCompiler": r"\bofReduceBool\b|\btrustCompiler\b|\bLean\.reduceBool\b|\breduceBool\b",
    "axiom_decl": r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*axiom\s",
    "implemented_by": r"\bimplemented_by\b",
    "extern": r"@\[\s*extern\b|\bextern\b",
    "unsafe": r"\bunsafe\b",
    "csimp": r"\bcsimp\b",
    "opaque": r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*opaque\s",
    "partial": r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*partial\s+def\b",
    "#exit": r"#exit\b",
    "set_option_debug": r"set_option\s+debug\.",
    "skipKernelTC": r"skipKernelTC",
    "set_option_pp": r"set_option\s+pp\.",
    "set_option_any": r"set_option\s+[A-Za-z_.]+",
    "addDecl_env_mod": r"\baddDecl\b|\baddAndCompile\b|\bmodifyEnv\b|\bsetEnv\b|\bEnvironment\.add\b|\baddDeclCore\b|\bKernel\.",
    "run_cmd_eval": r"#eval\b|\brun_cmd\b|\brun_elab\b|\brun_meta\b|\binitialize\b|\bbuiltin_initialize\b",
    "elab_macro_syntax": r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)?(?:local\s+|scoped\s+)?(?:elab|elab_rules|macro|macro_rules|syntax|declare_syntax_cat|notation|infix|infixl|infixr|prefix|postfix)\b",
    "command_elab_attr": r"@\[\s*(?:command_elab|term_elab|tactic|builtin_\w+|macro|delab|app_unexpander)\b",
    "import_Lean_meta": r"(?m)^[ \t]*(?:public\s+)?import\s+(?:Lean|Lean\.\S*|Qq|Aesop|Batteries\.Lean\S*)\s*$",
    "attribute_instance_local": r"attribute\s*\[\s*(?:local\s+)?instance",
    "Classical_or_choice_tricks": r"\bClassical\.ofNonempty\b|\bInhabited\.default\b.*False",
    "print_axioms": r"#print\s+axioms",
}


def strip_comments_and_strings(src: str) -> str:
    out = []
    i, n, depth = 0, len(src), 0
    in_str = False
    while i < n:
        c = src[i]
        if depth == 0 and not in_str:
            if src.startswith("/-", i):
                depth = 1
                i += 2
                out.append("  ")
                continue
            if src.startswith("--", i):
                j = src.find("\n", i)
                j = n if j < 0 else j
                out.append(" " * (j - i))
                i = j
                continue
            if c == '"':
                in_str = True
                out.append('"')
                i += 1
                continue
            out.append(c)
            i += 1
        elif in_str:
            if c == "\\" and i + 1 < n:
                out.append("  ")
                i += 2
                continue
            if c == '"':
                in_str = False
                out.append('"')
            else:
                out.append("\n" if c == "\n" else " ")
            i += 1
        else:
            if src.startswith("/-", i):
                depth += 1
                i += 2
                out.append("  ")
                continue
            if src.startswith("-/", i):
                depth -= 1
                i += 2
                out.append("  ")
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
    return "".join(out)


def scan_file(p: Path) -> tuple[dict[str, list[dict]], dict[str, int]]:
    raw = p.read_text(encoding="utf-8")
    code = strip_comments_and_strings(raw)
    raw_lines = raw.splitlines()
    hits: dict[str, list[dict]] = {}
    raw_counts: dict[str, int] = {}
    for cat, pat in PATTERNS.items():
        rx = re.compile(pat)
        raw_counts[cat] = len(rx.findall(raw))
        for m in rx.finditer(code):
            line = code.count("\n", 0, m.start()) + 1
            hits.setdefault(cat, []).append({"line": line, "text": raw_lines[line - 1].strip()[:200]})
    return hits, raw_counts


def main() -> None:
    if ALL_FILES:
        files = sorted(ROOT.rglob("*.lean"))
        files = [f for f in files if ".lake" not in f.parts]
    else:
        files = [ROOT / (m.replace(".", "/") + ".lean") for m in CLOSURE["topo_order"]]
    summary: dict[str, int] = {k: 0 for k in PATTERNS}
    raw_summary: dict[str, int] = {k: 0 for k in PATTERNS}
    per_file: dict[str, dict] = {}
    for f in files:
        hits, raw_counts = scan_file(f)
        rel = str(f.relative_to(ROOT))
        for k, v in raw_counts.items():
            raw_summary[k] += v
        if hits:
            per_file[rel] = hits
            for k, v in hits.items():
                summary[k] += len(v)
    OUT.write_text(json.dumps({"n_files": len(files), "code_hits_by_category": summary,
                               "raw_hits_incl_comments": raw_summary, "hits": per_file}, indent=1))
    print("files scanned:", len(files))
    for k in PATTERNS:
        print(f"  {k:28s} code={summary[k]:6d} raw={raw_summary[k]:6d}")


if __name__ == "__main__":
    main()
