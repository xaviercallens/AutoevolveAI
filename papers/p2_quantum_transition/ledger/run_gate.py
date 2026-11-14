"""Run the Elenchus ledger gate on ledger.json; record its verbatim output and exit code in gate_output.txt and write gen/gate_line.tex for the paper."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py"


def main() -> int:
    cmd = [sys.executable, "-I", GATE, str(HERE / "ledger.json"), "--evidence-dir", str(HERE / "evidence")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    text = res.stdout + res.stderr + f"exit_code={res.returncode}\n"
    (HERE / "gate_output.txt").write_text(text)
    print(text, end="")
    nblock = len(re.findall(r"^\s*block\b", text, re.M))
    nflag = len(re.findall(r"^\s*flag\b", text, re.M))
    line = (f"exit code {res.returncode}; {nblock} blocking finding(s) and {nflag} flag(s) (the gate's own report; a clean run means the bookkeeping holds, not that any claim is true).")
    (HERE.parent / "gen" / "gate_line.tex").write_text(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
