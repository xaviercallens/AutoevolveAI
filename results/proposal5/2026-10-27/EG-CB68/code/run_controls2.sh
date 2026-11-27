#!/bin/bash
# EG-CB68 controls, second batch (fixes N2: cb_search rejects caps < 8, so N2 uses cap 8; adds P2b set equality,
# P2c genbg + independent cycle filter for v = 14..16, P3b arbitrary-root C16-off cap 19).
set -u
cd "$(dirname "$0")/.."
S=/home/callensxavier_gmail_com/EG-CB68_scratch
B=code/cb_search
C="python3 -I code/cb_check.py"
G=/home/callensxavier_gmail_com/EG-CB68_scratch

# N2 (cap 8): with C8 filter on: no completion; off: Fano (v=7) and Moebius-Kantor 8_3 (v=8) appear
for o in 0 1 2; do
  taskset -c 2 $B 8 $o A -no16 > logs/controls/N2_cap8_o${o}_c8on.json
  taskset -c 2 $B 8 $o A -no8 -no16 -cert $S/N2_cap8_o${o}_c8off.cert -comp $S/N2_cap8_o${o}_c8off.comp > logs/controls/N2_cap8_o${o}_c8off.json
  taskset -c 2 $C $S/N2_cap8_o${o}_c8off.cert --allow-completions --json logs/controls/N2_cap8_o${o}_c8off_check.json > /dev/null
  taskset -c 2 python3 -I code/canon_count.py $S/N2_cap8_o${o}_c8off.comp logs/controls/N2_cap8_o${o}_c8off_canon.json > /dev/null
done

# P2b: set-level equality with genbg for v = 7..13
taskset -c 2 python3 -I code/set_compare.py logs/controls/P2b_set_equality.json \
  7:data/controls/canon_v7.g6:$G/genbg_v7.g6 8:data/controls/canon_v8.g6:$G/genbg_v8.g6 \
  9:data/controls/canon_v9.g6:$G/genbg_v9.g6 10:data/controls/canon_v10.g6:$G/genbg_v10.g6 \
  11:data/controls/canon_v11.g6:$G/genbg_v11.g6 12:data/controls/canon_v12.g6:$G/genbg_v12.g6 \
  13:data/controls/canon_v13.g6:$G/genbg_v13.g6 > /dev/null

# P3b: arbitrary root, C16 off, cap 19
taskset -c 2 $B 19 0 A -no16 -comp $S/P3b_o0.comp > logs/controls/P3b_cap19_o0.json
taskset -c 2 python3 -I code/canon_count.py $S/P3b_o0.comp logs/controls/P3b_canon.json > /dev/null
taskset -c 2 code/g6_cycles < data/controls/canon_v19.g6 > logs/controls/P3_v19_cycles.json

# P2c: genbg (independent generator) + g6_cycles (independent cycle test), v = 7..16:
#      our search says no connected C4/C8-free v_3-configuration exists for v <= 18
for v in 7 8 9 10 11 12 13; do taskset -c 3 code/g6_cycles < $G/genbg_v$v.g6 > logs/controls/P2c_v$v.json; done
for v in 14 15 16; do
  taskset -c 3 nauty-genbg -c -q -d3:3 -D3:3 -Z1 $v $v 2> logs/controls/P2c_genbg_v$v.txt | taskset -c 3 code/g6_cycles > logs/controls/P2c_v$v.json
done
echo controls2-done
