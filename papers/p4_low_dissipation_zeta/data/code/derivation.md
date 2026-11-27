# E3 hand derivation (reduction of Eq. (13) of arXiv:1802.09806v4 to a root form)

Notation: c = eta_C in (0,1); a = sqrt(Mh), b = sqrt(Mc), M = (a+b)^2, zeta = (a-b)/(a+b); q = eta_C Q_h^(r).
P = (q - a^2/th - b^2/tc)/(th+tc) (Eq. 3), eta = (q - a^2/th - b^2/tc)/(q/c - a^2/th) (Eq. 4), Pmax = q^2/(4M),
Pt = P/Pmax, s = sqrt(1-Pt), tau+ = q(1+s)/(2P) = 2M(1+s)/(Pt q), so q tau+ = K M with K = 2(1+s)/Pt = 2/(1-s).
u = eta/c, w = sqrt(1-c u) = sqrt(1-eta).

1. Identity from Eq. (4): q(1-u) = (1-eta) a^2/th + b^2/tc = w^2 a^2/th + b^2/tc.
2. Cauchy-Schwarz (the paper's Eq. (8) form): A^2/x + B^2/y >= (A+B)^2/(x+y). With A = w a, B = b, x+y <= tau+:
   q(1-u) tau+ >= (w a + b)^2, i.e. K (1-u) >= (w a + b)^2 / M = ((1-zeta) + (1+zeta) w)^2 / 4.   (a/(a+b) = (1+zeta)/2)
3. eta+ is the largest u (equivalently smallest w) for which this holds with equality being attainable: the tangency (discriminant zero)
   condition of the paper's Eq. (12). Multiplying by c and using c(1-u) = w^2 - (1-c):
   G(w, zeta) = K (w^2 - (1-c)) - c ((1-zeta) + (1+zeta) w)^2 / 4 = 0, positive root w+, eta+ = (1 - w+^2)/c.
4. G is a quadratic A w^2 - B w - C with A = K - c(1+zeta)^2/4 > 0, B = c(1-zeta^2)/2 >= 0, C = K(1-c) + c(1-zeta)^2/4 > 0:
   a unique positive root. At fixed w in [0,1), T = (1-zeta)+(1+zeta)w = (1+w) - zeta(1-w) is strictly decreasing in zeta and >= 2w >= 0,
   so G is strictly increasing in zeta. Hence the root w+ strictly decreases in zeta and eta+ strictly increases (Lean: root_strict_anti, etaPlus_strictMono).
5. zeta = 1: (K-c) w^2 = K(1-c), u = (K-1)/(K-c) = (1+s)^2/(2(1+s) - c Pt), which is Eq. (1) solved for eta/eta_C.
6. Esposito P = 1 (s = 0, K = 2): zeta = -1 gives u = 1/2, zeta = 1 gives u = 1/(2-c).
7. Engine-level (engine_bound): w <= 1 gives (w a + b) >= w (a+b), so K(1-u) >= w^2 = 1 - c u directly, i.e. zeta = 1 is the worst case, without Eq. (13).

Transcription note: in the first reading of Eq. (13) from the page image, the term -((1+zeta)/4) eta_C (1-sqrt(1-P)) was put
inside the square root. The page image shows it outside (inside the square bracket after the root). Corrected transcription agrees with the
root form to 1.6e-58 at 3000 random points (logs/link.log); the first reading disagreed by up to 0.23 (logs/link_first_transcription.log).
