#!/bin/bash
# fmt, unit tests (crate), clippy as CI runs it, release build of lattice_phonon; cores 6,7, -j 2.
set -e
M=/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2/Cargo.toml
export CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar
cargo fmt --manifest-path "$M" -p qf-yukawa-crystal
cargo fmt --manifest-path "$M" -p qf-yukawa-crystal --check
taskset -c 6,7 cargo test -j 2 --offline --release --manifest-path "$M" -p qf-yukawa-crystal -- --test-threads=2 2>&1 | grep -E "^test |test result|error|panicked" | tail -80
if [ "$1" = "clippy" ]; then
  cd /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2
  taskset -c 6,7 cargo clippy -j 2 --offline --workspace --features experimental -- -D warnings 2>&1 | tail -15
fi
taskset -c 6,7 cargo build -j 2 --offline --release --manifest-path "$M" -p qf-yukawa-crystal --bin lattice_phonon 2>&1 | tail -2
