import sympy as sp

c, s, z = sp.symbols("c s z", positive=True)
P = 1 - s**2
a = 1 + s
d = (1 + z) ** 2 / 4
K = 2 / (1 - s)
A = K / c - d
B = (1 - z**2) / 2
C = (1 - z) ** 2 / 4 + K * (1 - c) / c
Disc = sp.simplify(B**2 + 4 * A * C)
w = (B + sp.sqrt(Disc)) / (2 * A)
u = (1 - w**2) / c
D = a**2 + (1 - d * c) * P
# u = a^2/D + (1-z^2) P a / D^2 * (1 - sqrt(inner))  -> find inner
X = sp.simplify((u - a**2 / D) * D**2 / ((1 - z**2) * P * a))
# X = 1 - sqrt(inner)  => inner = (1-X)^2
inner = sp.simplify(sp.expand((1 - X) ** 2))
print("Disc =", sp.factor(Disc))
print("inner(true) =", sp.factor(sp.simplify(inner)))
paper = (c / 2) * (d * c - z) * (1 - s) + 1 - c - ((1 + z) / 4) * c * (1 - s)
print("inner(paper transcription) =", sp.factor(sp.simplify(paper)))
print("difference =", sp.factor(sp.simplify(inner - paper)))
