import re

with open("results/200_solutions_dossier.tex", "r") as f:
    text = f.read()

eqs = re.findall(r'\\begin{equation\*}(.*?)\\end{equation\*}', text, flags=re.DOTALL)
for i, eq in enumerate(eqs):
    begins = re.findall(r'\\begin{([^}]+)}', eq)
    ends = re.findall(r'\\end{([^}]+)}', eq)
    
    # Check if begins matches ends
    b_dict = {}
    for b in begins: b_dict[b] = b_dict.get(b, 0) + 1
    for e in ends: b_dict[e] = b_dict.get(e, 0) - 1
    
    for k, v in b_dict.items():
        if v != 0:
            print(f"Eq {i} has unbalanced environment {k}: {v}")
            print(eq)
