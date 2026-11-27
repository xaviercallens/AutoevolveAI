# facts_fss.md: every number in sec_fss.tex, with the command that printed it

All numbers are Tier X (floating point) unless stated. Run on 2026-10-11, 2 cores (`taskset -c 6,7`).

## 1. Rust `fss-lattice` (rusty-SUNDIALS, branch physics/jellium-wigner-2026-10-11)

Commit adding the command: `3eba703141d92fc5a5568a5c2a28e5edb208d25a` (parent b7e4380; from `git rev-parse HEAD`
right after committing). Not pushed. The listing in sec_fss.tex is `git show 3eba703:crates/qf-yukawa-crystal/src/main.rs`,
lines 607-633 (checked with `sed -n 607,633p`). A later commit 91ba196 (parent session, jel-main streaming) sits on top.

Build / checks (from the crate's workspace, `--manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-jellium/Cargo.toml`):
- `cargo build -q --release -j 2 --offline -p qf-yukawa-crystal` -> exit 0
- `cargo fmt -p qf-yukawa-crystal` -> reformatted the one `println!` header line
- `cargo clippy -q --release -j 2 --offline -p qf-yukawa-crystal` -> one pre-existing warning (`type_complexity`, main.rs:446, snapshot arm), none in the new code
- `cargo test -q --release -j 2 --offline -p qf-yukawa-crystal -- --test-threads=2` -> `running 10 tests ... test result: ok. 10 passed; 0 failed` (plus two empty targets)

Command: `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-jellium/target/release/yukawa_crystal fss-lattice <any dir>`
(`time`: real 0m0.281s). Output (identical before and after `cargo fmt`):
```
kappa nx ny N lx ly sides_ge_2rc e_box_per_particle e_tri_direct_sum e_box_minus_e_tri
2 6 12 72 6.4474 11.1673 false 3.927326193182643e-1 3.935333668255099e-1 -8.007e-4
2 16 18 288 17.1931 16.7509 true 3.935333668255304e-1 3.935333668255099e-1 2.054e-14
2 32 36 1152 34.3862 33.5018 true 3.935333668252588e-1 3.935333668255099e-1 -2.511e-13
2 48 54 2592 51.5794 50.2527 true 3.935333668256187e-1 3.935333668255099e-1 1.088e-13
1 6 12 72 6.4474 11.1673 false 1.563725839041460e0 1.607609217185270e0 -4.388e-2
1 16 18 288 17.1931 16.7509 true 1.607609217185348e0 1.607609217185270e0 7.794e-14
1 32 36 1152 34.3862 33.5018 true 1.607609217184786e0 1.607609217185270e0 -4.841e-13
1 48 54 2592 51.5794 50.2527 true 1.607609217184156e0 1.607609217185270e0 -1.114e-12
```
Derived in the text (arithmetic on the numbers above and Table tab:num-refs / FACTS §4):
- 8.007e-4 / 7.43e-3 = 0.108 ("about a tenth of the square-triangular gap"); 8.007e-4 / 4e-10 = 2.0e6 ("two million times the P1 tolerance", tolerance 1e-9*|e_tri| ~ 3.9e-10 from Ch3).
- 4.388e-2 / 9.54e-3 = 4.6 ("more than four times").
- max |diff| for passing boxes: 1.114e-12. Pair terms at N=2592: 2592*2591/2 = 3,357,936 ("up to 3.4e6").
- Python companion value 0.393533366826 at N=72 is quoted from Ch3 (ch3_yukawa_small.py output), not re-run.

## 2. Python `code/fss_disk.py`

Command (from papers/textbook_universal_optimality/):
`taskset -c 6,7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I code/fss_disk.py figures_v2/fss_disk.pdf`
(first run `time`: real 12.5 s). Full output:
```
exact limit theta_A(1)-1 = 0.159595266963928   theta_Z2(1)-1 = 0.180340599016096
offsets used: 120  (|v|^2 <= 40.0); radii: 362 distinct disks
control brute vs offsets: n=   55  e_offsets=0.133466896335072  e_brute=0.133466896335072  diff=-5.6e-17
control brute vs offsets: n=  199  e_offsets=0.145954450343741  e_brute=0.145954450343741  diff=-5.6e-17
control brute vs offsets: n=  385  e_offsets=0.149227076580003  e_brute=0.149227076580003  diff=-2.8e-17
control brute vs offsets: n=  793  e_offsets=0.152547797510471  e_brute=0.152547797510471  diff=-5.6e-17

   R        n      e(R)               e(R)-e_inf      (n-pi R^2)/R
   3.95     55  0.133466896335072  -2.612837e-02  +1.5266
   8.22    211  0.146729163409227  -1.286610e-02  -0.1478
  12.23    475  0.150519096113905  -9.076171e-03  +0.4274
  18.09   1039  0.153601535482390  -5.993731e-03  +0.5845
  26.79   2245  0.155540998312996  -4.054269e-03  -0.3566
  39.68   4939  0.156847172637246  -2.748094e-03  -0.1822
  58.76  10867  0.157729126813296  -1.866140e-03  +0.3176
  87.02  23785  0.158339845552686  -1.255421e-03  -0.0759
 130.00  53071  0.158755808502495  -8.394585e-04  -0.1594
max |n - pi R^2|/R over all disks: 1.5266; for R > 60: 0.4676
edge prediction (Tier C): beta = 0.054618,  c_pred = -2 sqrt(pi) beta = -0.193616

fits over disks with n >= nmin (Tier X):
 nmin=  100 (347 disks, n up to 53071)
   e_inf + c/sqrt(N) + d/N : e_inf=0.159599494 bias=+4.23e-06 c=-0.19398 d=0.0040  rms resid=1.80e-04
   e_inf + c/sqrt(N)       : e_inf=0.159595622 bias=+3.55e-07 c=-0.19365
   e_inf + d/N  (neg ctrl) : e_inf=0.157066869 bias=-2.53e-03 d=-2.1793
 nmin= 1000 (229 disks, n up to 53071)
   e_inf + c/sqrt(N) + d/N : e_inf=0.159597422 bias=+2.15e-06 c=-0.19398 d=0.0132  rms resid=2.86e-05
   e_inf + c/sqrt(N)       : e_inf=0.159594746 bias=-5.21e-07 c=-0.19355
   e_inf + d/N  (neg ctrl) : e_inf=0.158334757 bias=-1.26e-03 d=-5.6471

square lattice Z^2, 3-term fit (n >= 100): e_inf=0.180356622  minus theta_Z2-1: +1.60e-05  minus theta_A-1: +2.076e-02
figure written: .../figures_v2/fss_disk.pdf
```
The block above is the second run (after changing only the figure's axis limits/markers), saved to
`/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/fss/fss_disk_out.txt`; the first run printed the same numbers
(checked line by line by eye, not by diff).

Derived in the text:
- |c - c_pred| / |c_pred| = (0.19398 - 0.193616)/0.193616 = 0.19% ("0.2% apart").
- Continuum estimate beta = 1/(2 pi) = 0.159155, c = -2 sqrt(pi)/(2 pi) = -1/sqrt(pi) = -0.5642 (Tier C arithmetic); ratio 0.5642/0.1936 = 2.9 ("three times").
- 2.53e-3 / 4.23e-6 = 598 ("about 600 times"); theta_Z2-1 - (theta_A-1) = 0.180340599 - 0.159595267 = 2.0745e-2; 2.53e-3 / 2.0745e-2 = 0.122 ("12%").
- theta_A(1) = 1.159595266963928 also appears in Ch1 Exercise ex:py-theta (independent script) - consistent.

## 3. Tier C statements (human proofs in sec_fss.tex, not formalised)
- Proposition fss:prop:box (min-image box energy = e_lat when min(Lx,Ly) >= 2 rc).
- Corollary fss:cor:small (too-small box -> strictly below e_lat; uses V_sf >= 0 by convexity of V).
- Proposition fss:prop:identity (e(R) = e_inf - B(R)/N(R)).
- Scaling argument (heuristic): B ~ 2 pi R beta, beta = (1/pi) sum g |v|, c_pred = -2 sqrt(pi) beta.
- Lattice-point bound used: only Ch5 Lemma ch5:lem:count, |N(r) - pi r^2| <= C(r+1).
