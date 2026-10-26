#!/bin/bash
# P2 G2: re-run the Rust lattice_phonon binary on finer k-grids (n up to 768) for the gauss:1 headline points.
# cores 4-5, two threads; incremental CSV output.
B=/home/callensxavier_gmail_com/rusty-target-ar/release/lattice_phonon
O=/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2
taskset -c 4-5 "$B" point gauss:1 0.5 0.866025403784439 96,192,384,768 400 > "$O/rust_fine_tri.csv"
taskset -c 4-5 "$B" point gauss:1 0.5 0.966025403784 96,192,384,768 400 > "$O/rust_fine_c1.csv"
taskset -c 4-5 "$B" point gauss:1 0.295 0.9555 96,192,384,768 400 > "$O/rust_fine_c2.csv"
taskset -c 4-5 "$B" point gauss:0.5 0.5 0.966025403784 96,192,384,768 400 > "$O/rust_fine_g05.csv"
taskset -c 4-5 "$B" point gauss:0.5 0.5 0.866025403784439 96,192,384,768 400 > "$O/rust_fine_g05tri.csv"
echo done > "$O/rust_fine.done"
