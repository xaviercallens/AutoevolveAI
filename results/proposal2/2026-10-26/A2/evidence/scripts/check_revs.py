"""Compare git HEAD revisions of candidate prebuilt lake package dirs with the NS lake-manifest."""
import json
import subprocess
import sys
from pathlib import Path

MANIFEST = Path(sys.argv[1])
CANDS = [Path(p) for p in sys.argv[2:]]


def head(p: Path) -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=p, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or ("ERR " + r.stderr.strip()[:200])
    except Exception as e:  # noqa: BLE001
        return f"EXC {e}"


def main() -> None:
    m = json.loads(MANIFEST.read_text())
    want = {p["name"]: p["rev"] for p in m["packages"]}
    for c in CANDS:
        print("==", c)
        for name, rev in want.items():
            d = c / "packages" / name
            if not d.exists():
                print(f"  {name:18s} MISSING (want {rev})")
                continue
            h = head(d)
            print(f"  {name:18s} {'MATCH' if h == rev else 'DIFF '} have={h} want={rev}")
        tc = c / "packages" / "mathlib" / "lean-toolchain"
        if tc.exists():
            print("  mathlib lean-toolchain:", tc.read_text().strip())
        b = c / "packages" / "mathlib" / ".lake" / "build" / "lib" / "lean" / "Mathlib.olean"
        print("  Mathlib.olean exists:", b.exists())


if __name__ == "__main__":
    main()
