#!/bin/bash
# usage: run_n.sh n [ncores<=4]  (run from MS-CENSUS dir)
# splits geng -c n into res/mod parts, each pinned to one of cores 2-5.
n=$1
for k in 0 1 2 3; do
  core=$((k+2))
  ( taskset -c $core nauty-geng -c $n $k/4 2>logs/geng_n${n}_p${k}.err | taskset -c $core ./code/d2c_filter data/d2c_n${n}_p${k}.g6 > logs/census_n${n}_p${k}.log ) &
done
wait
