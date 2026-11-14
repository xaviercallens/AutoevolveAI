"""Independent auditor check: Eq. (13) (as printed) vs the root form of the tangency condition."""
import sympy as sp
import mpmath as mp
import random

c, s, z, x, u = sp.symbols('c s z x u', real=True)
P = 1 - s**2
K = 2 / (1 - s)
# Eq. (13), page-image reading: last term OUTSIDE the root
a = 1 + s
d = (1 + z)**2 / 4
D = a**2 + (1 - d*c)*P
inner = (c/2)*(d*c - z)*(1 - s) + 1 - c
u13 = a**2/D + (1 - z**2)*P*a/D**2 * (1 - x - (1 + z)/4*c*(1 - s))   # x = sqrt(inner)

# my own derivation: feasibility K(1-u) >= ((1-z)+(1+z)w)^2/4, w^2 = 1-c u; tangency = equality.
# eliminate w: (1+z)w = 2 sqrt(K(1-u)) - (1-z)  -> square twice -> R(u) = 0, quadratic in u
L = (1 + z)**2*(1 - c*u) - 4*K*(1 - u) - (1 - z)**2
R = sp.expand(sp.together(L**2 - 16*(1 - z)**2*K*(1 - u)))
num = sp.numer(sp.together(R.subs(u, u13)))
num = sp.Poly(sp.expand(num), x)
rem = num.rem(sp.Poly(x**2 - sp.together(inner), x))
r0 = [sp.simplify(sp.together(cf)) for cf in rem.all_coeffs()]
print("remainder coeffs of R(u13) mod (x^2 - inner):", r0)
print("degree of R in u:", sp.Poly(sp.numer(sp.together(R)), u).degree())

mp.mp.dps = 50
def root_form(cv, Pv, zv):
    sv = mp.sqrt(1 - Pv); Kv = 2/(1 - sv)
    A = Kv - cv*(1 + zv)**2/4; B = cv*(1 - zv**2)/2; C = Kv*(1 - cv) + cv*(1 - zv)**2/4
    w = (B + mp.sqrt(B*B + 4*A*C))/(2*A)
    return (1 - w*w)/cv
def eq13(cv, Pv, zv, sign=1, inside=False):
    sv = mp.sqrt(1 - Pv); av = 1 + sv; dv = (1 + zv)**2/4
    Dv = av*av + (1 - dv*cv)*Pv
    inn = (cv/2)*(dv*cv - zv)*(1 - sv) + 1 - cv
    t = (1 + zv)/4*cv*(1 - sv)
    if inside:
        return av*av/Dv + (1 - zv*zv)*Pv*av/Dv**2*(1 - mp.sqrt(inn - t))
    return av*av/Dv + (1 - zv*zv)*Pv*av/Dv**2*(1 - sign*mp.sqrt(inn) - t)
random.seed(20261101)
m1 = m2 = m3 = mp.mpf(0); minner = mp.mpf(10)
for _ in range(5000):
    cv = mp.mpf(random.uniform(1e-4, 1 - 1e-4)); Pv = mp.mpf(random.uniform(1e-4, 1)); zv = mp.mpf(random.uniform(-1, 1))
    r = root_form(cv, Pv, zv)
    m1 = max(m1, abs(eq13(cv, Pv, zv) - r))
    m2 = max(m2, abs(eq13(cv, Pv, zv, -1) - r))
    m3 = max(m3, abs(eq13(cv, Pv, zv, inside=True) - r))
    sv = mp.sqrt(1 - Pv); minner = min(minner, (cv/2)*((1+zv)**2/4*cv - zv)*(1 - sv) + 1 - cv)
print("max|eq13(+) - root| =", mp.nstr(m1, 5))
print("max|eq13(-branch) - root| =", mp.nstr(m2, 5))
print("max|eq13(term inside root) - root| =", mp.nstr(m3, 5))
print("min inner (radicand) =", mp.nstr(minner, 5))
