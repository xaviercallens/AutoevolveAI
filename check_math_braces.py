with open("results/200_solutions_dossier.tex", "r") as f:
    text = f.read()

import re
eqs = re.findall(r'\\begin{equation\*}(.*?)\\end{equation\*}', text, flags=re.DOTALL)
for i, eq in enumerate(eqs):
    count = 0
    for c in eq:
        if c == '{': count += 1
        elif c == '}': count -= 1
    if count != 0:
        print(f"Eq {i} has {count} unbalanced braces:")
        print(eq)
