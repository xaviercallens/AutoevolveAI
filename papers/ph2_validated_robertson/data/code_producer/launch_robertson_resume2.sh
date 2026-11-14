#!/bin/bash
# Resume after the 2026-11-11 session end killed the driver at t=2599 (checkpoint 2026-11-11 18:16).
# Main session decision 2026-11-12: raise this invocation's CPU cap to 11000 s (about 3 core-hours) so the run can reach
# t=4000; total stays inside the preregistered 10 core-hour cap (about 4.7 core-hours already spent on the driver).
cd "$(dirname "$0")/.."
echo "launch $(date -u +%FT%TZ) RESUME2 from ckpt p=24 tau=1e-22 cpu_cap=29900s cumulative (main-session decision 2026-11-14: the run stopped at t=3800 on the 27700 s cap, 200 short of the t=4000 output time; the cap counts total CPU)" >> logs/robertson_run.log
exec taskset -c 1 sage --python3 code/run_robertson.py logs/enclosure_ckpt.json logs/robertson_run.log 29900 24 1e-22
