"""Run the Elenchus ledger gate on ledger.json and record its verbatim output and exit code in gate_output.txt."""
from __future__ import annotations

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
