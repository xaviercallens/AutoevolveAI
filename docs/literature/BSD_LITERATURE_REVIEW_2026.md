# BSD Conjecture — Literature Review (assembled 2026-09-27)

Sources: alphaXiv search 2026-09-27 (IDs cited inline) plus foundational
references. This file is the RAG source for the `literature` Chroma
collection; every claim below is attributable to the cited paper.

## The conjecture

For an elliptic curve E/Q, BSD asserts (rank part) that
ord_{s=1} L(E,s) = rank E(Q), and (leading-term part) that
L^(r)(E,1)/r! equals the product of the real period, regulator,
Tamagawa numbers and #Sha(E) / (#E(Q)_tors)^2. The rank part for
ranks 0 and 1 is a theorem in many cases; general rank >= 2 is open.

## Foundational results

- **Gross–Zagier (1986)**: height formula relating Heegner points to
  L'(E/K,1); non-torsion Heegner point iff analytic rank of E/K is 1.
- **Kolyvagin (1988)**: Euler system of Heegner points; if the Heegner
  point is non-torsion then rank E(K) = 1 and Sha(E/K) is finite.
  Combined with Gross–Zagier: analytic rank <= 1 implies BSD rank
  equality and Sha finite.
- **Wiles, Taylor–Wiles, BCDT (1995–2001)**: modularity of E/Q, hence
  analytic continuation and functional equation of L(E,s) — the
  prerequisite for even stating analytic rank unconditionally.
- **Skinner–Urban (2014)**: Iwasawa main conjecture for GL2 (ordinary
  case); yields p-part of BSD formula in rank 0 and, with Kolyvagin,
  rank 1 cases.

## Modern state (papers found on alphaXiv, 2026-09-27)

- **Bhargava–Skinner–Zhang** [ID=1407.1826]: >66% of all E/Q ordered by
  height satisfy the BSD rank conjecture. Method: average Selmer group
  sizes (Bhargava–Shankar) + p-converse theorems.
- **Kolyvagin's conjecture and Sha** [ID=2609.15328, 2026-09]: Heegner
  points detect finiteness of p-primary Sha for semistable E/Q of
  ARBITRARY rank with good reduction hypotheses — the structural route
  past rank 1.
- **Kolyvagin at non-ordinary primes** [ID=2609.13088, 2026-09]:
  extends the Euler-system machinery to non-ordinary (supersingular)
  primes for GL2-type abelian varieties.
- **Main conjectures, non-CM good ordinary** [ID=2412.20078]: Iwasawa
  main conjecture for E/Q at good ordinary p>2 with irreducible residual
  representation — feeds p-parts of the BSD formula.
- **IMC at odd supersingular primes** [ID=1610.10017]: plus/minus
  theory; consequences include p-parts of the BSD leading-term formula.
- **2-part of BSD for quadratic twists** [ID=2102.11808]: generalized
  Birch lemma; explicit infinite twist families with 2-part of BSD.
- **CM curves, supersingular/ramified Iwasawa theory** [ID=2609.13063,
  2608.06879]: plus/minus and epsilon-constant frameworks at the
  remaining bad primes for CM curves.
- **Anticyclotomic IMC for modular forms** [ID=2603.22483]: weight >= 4
  newforms, Heegner-cycle Euler systems.
- **Rank jumps in Z/pZ-extensions** [ID=2107.09166]; **quadratic twist
  rank distribution / Goldfeld** [ID=2412.07308].
- **Exact-arithmetic Selmer modules** [ID=2609.selmer-modules-euler-
  systems-bsd-conjecture, 2026-09-23]: reformulates Selmer theory so
  every invariant is an exact rational and every local condition a
  finite computation — directly relevant to machine-checkable BSD
  verification (our use case).

## What is genuinely open

1. Rank part for any single curve with analytic rank >= 2 (389a1 is
   verified numerically but not proven: no theorem gives rank(389a1)=2
   from L''(1) != 0).
2. Sha finiteness in general (only known when analytic rank <= 1, plus
   the new arbitrary-rank semistable results conditional on Kolyvagin's
   conjecture [2609.15328]).
3. Full BSD formula (leading term) beyond p-parts in restricted cases.

## Implications for this project's pipeline

- Numerical verification across ranks 0–3 is machine-checkable today
  (PARI ellanalyticrank + Sage mwrank descent) — done 2026-09-27 on this
  machine for 11a1/37a1/389a1/5077a1: all four match.
- Formal (Lean 4) targets should follow the exact-arithmetic Selmer
  direction [2609.selmer-...]: finite local computations, exact
  rationals — the shape of statements a kernel can check.
- Mathlib v4.34 has WeierstrassCurve/EllipticCurve with group law and
  LSeries hooks; a faithful BSD *statement* needs Mordell–Weil rank tied
  to E(Q), not a free field (defect found in formal/ANSE/
  BSD_Conjecture.lean on 2026-09-27).
