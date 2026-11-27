"""Run one of the M3 scripts with python-flint on sys.path, under `python -I` (which ignores PYTHONPATH and the user site).

usage: python -I with_flint.py FLINT_DIR SCRIPT.py [SCRIPT ARGS...]

FLINT_DIR is a directory that contains the `flint` package: the repository's .scratchpad/b2_pylib (python-flint 0.6.0, used by the
producer) or, for the system python3 of the matching minor version, ~/.local/lib/python3.10/site-packages (python-flint 0.9.0, used by
the independent audit). Nothing is installed by this launcher.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    flint_dir = Path(sys.argv[1]).expanduser().resolve()
    script = Path(sys.argv[2]).resolve()
    if not (flint_dir / "flint").is_dir():
        raise SystemExit(f"no flint package in {flint_dir}")
    sys.path.insert(0, str(flint_dir))
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script)] + sys.argv[3:]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
