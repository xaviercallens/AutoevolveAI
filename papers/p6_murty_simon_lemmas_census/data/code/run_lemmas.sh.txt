#!/bin/bash
# run from MS-CENSUS dir. 4 processes on cores 2-5.
run() { core=$1; shift; for n in "$@"; do taskset -c $core python3 -I code/lemmas.py $n data/lemmas_n${n}.json data/d2c_n${n}_p*.g6 > logs/lemmas_n${n}.log 2>&1; done; }
run 2 11 &
run 3 10 &
run 4 9 8 &
run 5 3 4 5 6 7 &
wait
