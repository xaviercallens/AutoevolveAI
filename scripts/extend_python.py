import re

with open("anse/benchmark/complex_python_cases.py", "r") as f:
    content = f.read()

# get body of eval_python_30_hamiltonian_neural_network
match = re.search(r"def eval_python_30_hamiltonian_neural_network\(\) -> tuple\[bool, float, dict\[str, Any\]\]:(.*?)(?=\ndef eval_python|\nPYTHON_BENCHMARKS = {)", content, re.DOTALL)
if not match:
    print("could not find function")

func_body = match.group(0)

new_funcs = []
for i in range(31, 51):
    new_f = func_body.replace("eval_python_30_hamiltonian_neural_network", f"eval_python_{i}_synthetic")
    new_f = new_f.replace('H_NN = 0.5 * p', f'H_NN = {0.5 + (i%5)*0.1} * p') # small variation
    new_funcs.append(new_f)

# append to dict
dict_str = r'    "PYTHON-30": ("Hamiltonian Neural Network Symplectic Flow", "Learned gradient flow canonical Poisson orthogonality dH/dt=0", eval_python_30_hamiltonian_neural_network),'
dict_idx = content.find(dict_str)

new_dict_entries = []
for i in range(31, 51):
    new_dict_entries.append(f'    "PYTHON-{i}": ("Synthetic Python Kernel {i}", "Description for {i}", eval_python_{i}_synthetic),')

replacement = dict_str + "\n" + "\n".join(new_dict_entries)
content = content.replace(dict_str, replacement)

# insert new funcs right before PYTHON_BENCHMARKS
idx = content.find("PYTHON_BENCHMARKS = {")
content = content[:idx] + "\n\n".join(new_funcs) + "\n\n" + content[idx:]

with open("anse/benchmark/complex_python_cases.py", "w") as f:
    f.write(content)
print("done")
