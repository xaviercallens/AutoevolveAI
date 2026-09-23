with open("results/200_solutions_dossier.tex", "r") as f:
    text = f.read()

text = text.replace("\\usepackage[T1]{fontenc}\\n\\usepackage{lmodern}\\n\\UseRawInputEncoding", "\\usepackage[T1]{fontenc}\n\\usepackage{lmodern}\n\\usepackage[utf8]{inputenc}")
with open("results/200_solutions_dossier.tex", "w") as f:
    f.write(text)
