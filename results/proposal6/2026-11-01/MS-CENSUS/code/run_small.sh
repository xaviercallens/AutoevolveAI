#!/bin/bash
# run from MS-CENSUS dir: ./code/run_small.sh 3 10
for ((n=$1; n<=$2; n++)); do
  s=$(date +%s)
  ./code/run_n.sh $n
  e=$(date +%s)
  echo "n=$n wall_s=$((e-s))" >> logs/timing.log
done
