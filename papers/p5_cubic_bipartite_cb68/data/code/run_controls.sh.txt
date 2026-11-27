#!/bin/bash
# EG-CB68 controls, run with the frozen binary (logs/freeze_sha256.txt). Cores 2,3 only.
set -u
cd "$(dirname "$0")/.."
S=/home/callensxavier_gmail_com/EG-CB68_scratch
mkdir -p logs/controls data/controls "$S"
B=code/cb_search
C="python3 -I code/cb_check.py"

# P1: cap 29, both orbits, both oracles; certificate from oracle A checked by the streaming checker
for o in 1 2; do
  for k in A B; do taskset -c 2 $B 29 $o $k > logs/controls/P1_cap29_o${o}_$k.json; done
  taskset -c 2 $B 29 $o A -cert $S/P1_cap29_o$o.cert > /dev/null
  taskset -c 2 $C $S/P1_cap29_o$o.cert --json logs/controls/P1_cap29_o${o}_check.json
done

# N3: tamper tests on the orbit-1 cap-29 certificate
taskset -c 2 python3 -I code/tamper_tests.py $S/P1_cap29_o1.cert $S logs/controls/N3_tamper.json > /dev/null

# P2: filters off, caps 13, triangle roots (both) and arbitrary root; canonical counts per v
for o in 0 1 2; do taskset -c 3 $B 13 $o A -no8 -no16 -comp $S/P2_o$o.comp > logs/controls/P2_cap13_o$o.json; done
cat $S/P2_o1.comp $S/P2_o2.comp > $S/P2_tri.comp
taskset -c 3 python3 -I code/canon_count.py $S/P2_tri.comp logs/controls/P2_canon_triangle.json --g6dir data/controls > /dev/null
taskset -c 3 python3 -I code/canon_count.py $S/P2_o0.comp logs/controls/P2_canon_arbitrary.json > /dev/null
# P2b: nauty genbg, independent of our generator (connected, 3-regular both sides, blocks share <= 1 point)
for v in 7 8 9 10 11 12 13; do taskset -c 3 nauty-genbg -c -d3:3 -D3:3 -Z1 $v $v > $S/genbg_v$v.g6 2> logs/controls/P2b_genbg_v$v.txt; done

# P3: C16 filter off, cap 19, triangle roots: completions must exist
for o in 1 2; do taskset -c 2 $B 19 $o A -no16 -comp $S/P3_o$o.comp > logs/controls/P3_cap19_o$o.json; done
cat $S/P3_o1.comp $S/P3_o2.comp > $S/P3_tri.comp
taskset -c 2 python3 -I code/canon_count.py $S/P3_tri.comp logs/controls/P3_canon.json --g6dir data/controls > /dev/null

# N1: C8 filter off (C16 on), cap 13: completions must appear (Fano at v = 7)
for o in 0 1 2; do taskset -c 2 $B 13 $o A -no8 -comp $S/N1_o$o.comp > logs/controls/N1_cap13_o$o.json; done
cat $S/N1_o1.comp $S/N1_o2.comp > $S/N1_tri.comp
taskset -c 2 python3 -I code/canon_count.py $S/N1_tri.comp logs/controls/N1_canon.json > /dev/null

# N2: with the C8 filter on, cap 7 must produce no completion (Fano/Heawood rejected by the C8 test);
#     with it off, cap 7 must produce exactly the Fano plane.
for o in 0 1 2; do
  taskset -c 2 $B 7 $o A -no16 > logs/controls/N2_cap7_o${o}_c8on.json
  taskset -c 2 $B 7 $o A -no8 -no16 -cert $S/N2_cap7_o${o}_c8off.cert > logs/controls/N2_cap7_o${o}_c8off.json
  taskset -c 2 $C $S/N2_cap7_o${o}_c8off.cert --allow-completions --json logs/controls/N2_cap7_o${o}_c8off_check.json > /dev/null
done
taskset -c 2 python3 -I code/heawood_c8.py logs/controls/N2_heawood.json > /dev/null
echo controls-done
