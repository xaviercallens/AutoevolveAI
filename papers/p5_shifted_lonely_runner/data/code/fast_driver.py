"""Driver: run the C search (cover_ls_fast) per n, then round and certify with both exact checkers."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cover_ls import certify  # noqa: E402

FAST = os.path.join(HERE, "cover_ls_fast")  # built from cover_ls_fast.c (current version)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", required=True)
    ap.add_argument("--budget", type=float, default=600.0, help="CPU seconds per attempt")
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--slack", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--swap-factor", type=float, default=0.0, help="if >0, allow velocity swaps with w <= swap_factor*n+2")
    ap.add_argument("--pworse", type=float, default=0.3, help="prob. of keeping a worsening move (C default 0.3)")
    ap.add_argument("--rw", type=int, default=4, help="random-walk move every RW stalled sweeps (C default 4)")
    ap.add_argument("--cpu-offset", type=float, default=0.0, help="CPU seconds already spent before this run (ledger)")
    ap.add_argument("--total-cpu-budget", type=float, default=0.0, help="stop before an attempt once offset + spent >= this")
    args = ap.parse_args()
    spent = 0.0
    env = dict(os.environ, SLR_PWORSE=str(args.pworse), SLR_RW=str(args.rw))
    x, y = args.ns.split("-") if "-" in args.ns else (args.ns, args.ns)
    logf = open(args.log, "a")

    def log(m: str) -> None:
        logf.write(m + "\n")
        logf.flush()

    tmpdir = os.path.join(os.path.dirname(HERE), "logs", "fast_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    for n in range(int(x), int(y) + 1):
        path = os.path.join(args.outdir, f"cert_n{n:03d}.json")
        if args.skip_existing and os.path.exists(path):
            log(f"n={n} skip (certificate exists)")
            continue
        q = n + 1
        dnum, dden = args.slack * q - 1, args.slack * q * q
        tot = 0.0
        done = False
        for at in range(args.attempts):
            if args.total_cpu_budget > 0 and args.cpu_offset + spent >= args.total_cpu_budget:
                log(f"STOP total CPU budget reached: offset={args.cpu_offset:.0f} spent={spent:.0f} budget={args.total_cpu_budget:.0f}")
                logf.close()
                return
            seed = args.seed * 100000 + n * 100 + at
            out = os.path.join(tmpdir, f"s_n{n:03d}_seed{seed}.txt")
            t0 = time.time()
            cmd = ["taskset", "-c", "1", FAST, str(n), str(dnum), str(dden), str(seed), str(args.budget), out]
            if args.swap_factor > 0:
                cmd.append(f"swap{int(args.swap_factor * n) + 2}")
            r = subprocess.run(cmd, capture_output=True, text=True, env=env)
            endline = [ln for ln in r.stderr.splitlines() if ln.startswith("END")]
            log(f"n={n} attempt={at} seed={seed} slack={args.slack} swap={args.swap_factor} pworse={args.pworse} rw={args.rw} budget={args.budget} rc={r.returncode} {endline[-1] if endline else r.stderr[-200:]}")
            try:
                dt = float(endline[-1].split("cpu=")[1])
            except (IndexError, ValueError):
                dt = time.time() - t0
            tot += dt
            spent += dt
            if r.returncode == 0:
                rows = [ln.split() for ln in open(out).read().splitlines() if ln.strip()]
                vv = [int(r_[0]) for r_ in rows]
                s = [float(r_[1]) for r_ in rows]
                ok, info = certify(vv, s, 1, q, path, dnum / dden,
                                   {"method": "cover_ls_fast (C) coordinate fold moves" + (" + velocity swaps" if args.swap_factor > 0 else ", v=[n]"),
                                    "v_is_[n]": vv == list(range(1, n + 1)), "seed": seed,
                                    "search_radius": f"{dnum}/{dden}", "cpu_s_this_n": tot,
                                    "pworse": args.pworse, "rw": args.rw, "swap_factor": args.swap_factor})
                log(f"n={n} certify={'OK' if ok else 'FAIL'} D={info.get('D')} {info.get('checker2', info.get('reason'))}")
                if ok:
                    done = True
                    break
        log(f"n={n} RESULT {'CERTIFIED' if done else 'OPEN'} cpu_total={tot:.1f}")
    logf.close()


if __name__ == "__main__":
    main()
