#!/bin/bash
# EG-CB68 main runs (after the controls). Frozen binary; cores 2,3 only.
# Part T: triangle-rooted caps 30..35, both orbits: oracle A with certificate -> streaming checker; oracle B for
#         counter + transcript-hash agreement.
# Part R: arbitrary-root (no Berge triangle assumed) caps 29..34, oracles A and B.
set -u
cd "$(dirname "$0")/.."
S=/home/callensxavier_gmail_com/EG-CB68_scratch/certs
mkdir -p "$S" data/main logs/main
B=code/cb_search
for cap in 30 31 32 33 34 35; do
  for o in 1 2; do
    taskset -c 2 $B $cap $o A -cert $S/T_cap${cap}_o$o.cert > data/main/T_cap${cap}_o${o}_A.json
    taskset -c 3 $B $cap $o B > data/main/T_cap${cap}_o${o}_B.json
    taskset -c 2 python3 -I code/cb_check.py $S/T_cap${cap}_o$o.cert --json data/main/T_cap${cap}_o${o}_check.json > /dev/null
    sha256sum $S/T_cap${cap}_o$o.cert >> logs/main/cert_sha256.txt
    gzip -9 -f $S/T_cap${cap}_o$o.cert
    sha256sum $S/T_cap${cap}_o$o.cert.gz >> logs/main/cert_sha256.txt
  done
done
echo T-done
for cap in 29 30 31 32 33 34; do
  taskset -c 2 $B $cap 0 A > data/main/R_cap${cap}_A.json &
  taskset -c 3 $B $cap 0 B > data/main/R_cap${cap}_B.json
  wait
done
echo R-done
