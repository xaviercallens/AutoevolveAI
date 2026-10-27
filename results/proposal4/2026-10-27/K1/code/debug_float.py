"""Debug: compare interval and float surrogate beta at a few classification points (diagnostic only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cert_sign as c  # noqa: E402


def main() -> int:
    d = json.loads(Path(sys.argv[1]).read_text())
    bad = [x for x in d["classification"] if not x["ex"]["float_inside_enclosure"] or not x["fv"]["float_inside_enclosure"]]
    for x in bad[:6]:
        print(x["name"], x["T0"], x["r"], "ex", x["ex"]["beta"], x["ex"]["beta_float"], x["ex"]["float_inside_enclosure"],
              "fv", x["fv"]["beta"], x["fv"]["beta_float"], x["fv"]["float_inside_enclosure"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
