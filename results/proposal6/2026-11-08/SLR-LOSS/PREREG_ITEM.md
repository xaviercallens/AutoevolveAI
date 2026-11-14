# SLR-LOSS preregistration (2026-11-08), written before any run

Claim sought: for n in 95..~140, n distinct positive integer velocities with rational shifts whose exact gamma(v;s)=max_t min_i||s_i+v_i t||
is STRICTLY smaller than the exact gamma of Poliakova's rule (arXiv 2609.23952: Sec.3 9->8 rule, E_n>=1 for n>=95, gamma<=1/(n+2); Table 1 rule 19->17, g=2, L=240, gives gamma<=1/(n+3) for n>=118).
Prior art 2026-11-08 (alphaXiv discover_papers + WebSearch, same day): only 2609.23952, 2603.24784, 2608.13599, 2609.06259 ; no sharper bound for n>=95 found. Novelty "to our knowledge" only. Poliakova's E_n>=1 (n>=95) is not claimed as ours.
Tiers: A = none (no Lean). L = Poliakova's rule/bounds (literature). C = our certified numbers (two exact checkers + exact gamma). X = anything about unshifted LRC or E_n beyond the certified radius: not claimed.
Method: generalised cpsat_rule.py (SLR-EXT/code): base 2,4,..,2N (N=n+g, g=gain) at shift 0, pool of 3-smooth multiples of 4 and {3,5}-smooth odds, shifts c/4+j/(8(N+1)), |j|<=J,
open radius r=p/q rational; CP-SAT set cover, every SAT answer rechecked by slr_exact.covers_open and check_cover (C). Exact gamma by bisection on covers_open + exact crossing evaluation (Fractions).
Experiments: E1 baseline exact gamma of her rules (n=95..~140). E2 g=1 strict open radius 1/(n+2) and shrinking. E3 g=2, radius ~1/(n+3) (i.e. E>=2) for n=95..117, and g=3 for n>=118.
Positive controls: her n=95..109 covers reproduced (rule.py) at closed radius via radius 1/(N+1)+eps; SLR-EXT n=63 cert re-checked by new gamma routine (expect 66/4225) and the generalised CP-SAT (N=64, r=1/64) refinds a cover.
Negative controls: known non-cover (SLR-EXT n=63 cert at radius 1/65; tight base 2..2N at radius < 1/(N+1)); radius = exact gamma must be NOT_COVERED; gamma*(1+1e-9) COVERED.
Acceptance: cert counts only if both checkers COVERED at the stated exact radius, with n distinct positive velocities, and new exact gamma < her exact gamma for that n.
Kill: after 6 core-hours (CP-SAT wall x workers) with no n having gamma strictly smaller than her rule's exact gamma -> NEGATIVE, stop. Total cap 20 core-h, cores 1-6 only.
No Lean, no audit, no publish, no commit.
