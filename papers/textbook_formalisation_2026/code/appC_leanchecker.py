"""Annexe C : compiler les exemples Lean en .olean dans un dossier de travail, puis les rejouer avec leanchecker.

Même chaîne et même LEAN_PATH que scripts/certified_numerics/lean_pinned.py (Lean 4.34.1, Mathlib d13f23b7), mais les
.olean vont dans SCRATCH/olean au lieu du dossier formal_cert/.olean_out codé en dur (méthode de l'audit N4).
Chaque exemple devient le module AppC.E<n>_<nom>. Un module inexistant sert de témoin négatif du rejeu.

Usage : python -I appC_leanchecker.py SCRATCH OUT.json NOM [NOM ...]      (NOM = appC_1_logique, ...)
Le dossier des sources est celui de ce script (code/lean/).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WORKTREE = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path.insert(0, str(WORKTREE / "scripts" / "certified_numerics"))
import lean_pinned  # noqa: E402

SRC_DIR = Path(__file__).resolve().parent / "lean"


def run(cmd: list[str], env: dict[str, str]) -> dict[str, object]:
    t0 = time.time()
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3000)
    return {"cmd": " ".join([Path(cmd[0]).name, *cmd[1:]]), "rc": res.returncode,
            "seconds": round(time.time() - t0, 1), "output": (res.stdout + res.stderr)[-4000:]}


def main(scratch: Path, out: Path, names: list[str]) -> int:
    root, olean = scratch / "src", scratch / "olean"
    (root / "AppC").mkdir(parents=True, exist_ok=True)
    (olean / "AppC").mkdir(parents=True, exist_ok=True)
    lp = lean_pinned.lean_path().replace(str(lean_pinned.OUT), str(olean))
    env = dict(os.environ, LEAN_PATH=lp, PATH=f"{lean_pinned.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    rows: list[dict[str, object]] = []
    for name in names:
        stem = name.replace("appC_", "E")
        mod = f"AppC.{stem}"
        src = root / "AppC" / f"{stem}.lean"
        shutil.copyfile(SRC_DIR / f"{name}.lean", src)
        ol = olean / "AppC" / f"{stem}.olean"
        comp = run([str(lean_pinned.TOOLCHAIN_BIN / "lean"), "-DautoImplicit=false", f"--root={root}",
                    "-o", str(ol), "-i", str(ol.with_suffix(".ilean")), str(src)], env)
        row: dict[str, object] = {"name": name, "module": mod, "compile": comp}
        if comp["rc"] == 0:
            row["leanchecker"] = run([str(lean_pinned.TOOLCHAIN_BIN / "leanchecker"), mod], env)
        rows.append(row)
        chk = row.get("leanchecker", {})
        print(json.dumps({"module": mod, "compile_rc": comp["rc"], "compile_s": comp["seconds"],
                          "leanchecker_rc": chk.get("rc"), "leanchecker_s": chk.get("seconds"),
                          "leanchecker_out": str(chk.get("output", ""))[-600:]}, ensure_ascii=False))
    missing = run([str(lean_pinned.TOOLCHAIN_BIN / "leanchecker"), "AppC.ModuleInexistant"], env)
    rows.append({"name": "temoin_module_inexistant", "leanchecker": missing})
    print(json.dumps({"module": "AppC.ModuleInexistant", "leanchecker_rc": missing["rc"],
                      "out": str(missing["output"])[-300:]}, ensure_ascii=False))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    expected_fail = {"appC_6_contrefacon"}
    ok = all((r.get("leanchecker", {}).get("rc") == 0) == (r["name"] not in expected_fail)
             for r in rows if r["name"] in names) and missing["rc"] != 0
    print(json.dumps({"all_controls_pass": ok}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))
