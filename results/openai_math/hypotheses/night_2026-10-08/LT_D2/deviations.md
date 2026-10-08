# LT_D2 deviations

## D1 (harness bug, 2026-10-08 ~12:10 UTC, before any Lean verdict)
First `closure` run passed a RELATIVE --lane path; the Lean subprocess runs with cwd = LeanMaster, so FiniteParity
'failed' in 0.4 s with `no such file or directory (error code: 2)`. This is a script defect, not a Lean result.
Fix: `lane = Path(args.lane).resolve()`. The bogus record ({"first_error": "no such file or directory (error code: 2)", "seconds": 0.4, "status": "failed", "timed_out": false}) was removed and the compile rerun.
The preregistered rules are unchanged; the code hash of lt_d2_shim.py in preregistration.json is therefore stale and the
new hash is recorded in result.json.

## D2 (script generalised after the result, 2026-10-08)
After result.json was written, lt_d2_shim.py was generalised (--root repeatable, --final, --challenge, --carry-from) so the same method can run on the triangular-lattice closures. Behaviour for the Lieb-Thirring run is unchanged when invoked with --carry-from <LT_D lane>; the hash recorded in result.json is the one that produced the result.
