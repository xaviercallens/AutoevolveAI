#!/bin/bash
# P2 G2: Rust (real-space, uniform grid) cross-check of the sign changes of the E_zp curvature at rho found by the
# Poisson/Duffy code: E_zp at rho and rho +- 0.02 (x direction), gauss:a for a straddling each root.
B=/home/callensxavier_gmail_com/rusty-target-ar/release/lattice_phonon
O=/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/rust_curv
mkdir -p "$O"
printf '0.5 0.866025403784439\n0.52 0.866025403784439\n0.48 0.866025403784439\n' > "$O/taus.txt"
for A in 0.35 0.40 1.50 1.65; do
  taskset -c 4-5 "$B" scan "gauss:$A" 192,384,768 400 "$O/taus.txt" "$O/gauss_$A.csv"
done
echo done > "$O/done"
