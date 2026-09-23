with open("results/200_solutions_dossier.tex", "r") as f:
    text = f.read()

# strip out verbatim blocks to check pure tex
import re
text = re.sub(r'\\begin{verbatim}.*?\\end{verbatim}', '', text, flags=re.DOTALL)
text = re.sub(r'\\begin{equation\*}.*?\\end{equation\*}', '', text, flags=re.DOTALL)

def check(t):
    count = 0
    for i, c in enumerate(t):
        if c == '{':
            # check if escaped
            if i > 0 and t[i-1] == '\\': continue
            count += 1
        elif c == '}':
            if i > 0 and t[i-1] == '\\': continue
            count -= 1
            if count < 0: return i
    return count

print("Unbalanced braces:", check(text))
