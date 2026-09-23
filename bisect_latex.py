import subprocess
import os

with open("results/200_solutions_dossier.tex", "r") as f:
    lines = f.readlines()

def compile_test(test_lines):
    with open("test.tex", "w") as f:
        f.writelines(test_lines)
    res = subprocess.run(["xelatex", "-interaction=nonstopmode", "test.tex"], capture_output=True)
    return res.returncode == 0

# find where \section{ begins
start = 0
for i, l in enumerate(lines):
    if "\\section{" in l:
        start = i
        break

preamble = lines[:start]
content = lines[start:-1] # exclude \end{document}
end_doc = [lines[-1]]

# bisect content
problems = []
curr = []
for l in content:
    if "\\subsection{" in l and curr:
        problems.append(curr)
        curr = [l]
    else:
        curr.append(l)
if curr: problems.append(curr)

print(f"Found {len(problems)} problems")

good = 0
for i in range(1, len(problems) + 1):
    test = preamble + [line for p in problems[:i] for line in p] + end_doc
    if not compile_test(test):
        print(f"Fails at problem {i}")
        break
    good = i

print(f"Last good problem is {good}")
