"""Stream-extract the Zenodo 14452152 DAC_data.tar.gz (untrusted data) into a directory on disk 2.

Everything is extracted except the SinglePath_Intrinsic_Cycle results, of which only the materials named on the
command line are kept (they are used to check which single path the stored files actually ran). Member names
are sanitised (no absolute paths, no '..', regular files only)."""

from __future__ import annotations

import sys
import tarfile
from pathlib import Path


def main() -> int:
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    keep_single = set(sys.argv[3:])
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    with tarfile.open(src, "r|gz") as tf:
        for m in tf:
            name = m.name
            if not m.isfile() or name.startswith("/") or ".." in Path(name).parts:
                continue
            if "/SinglePath_Intrinsic_Cycle/" in name:
                stem = Path(name).name.replace("SinglePathIDC_", "").replace(".json", "")
                if stem not in keep_single:
                    continue
            out = dest / name
            out.parent.mkdir(parents=True, exist_ok=True)
            f = tf.extractfile(m)
            if f is None:
                continue
            out.write_bytes(f.read())
            n += 1
            if n % 2000 == 0:
                print(n, name, flush=True)
    print("extracted", n, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
