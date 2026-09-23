import re

def extend_dict(path, key_prefix):
    with open(path, "r") as f:
        content = f.read()
    
    # find the last key matching the prefix
    keys = re.findall(rf'"{key_prefix}-(\d+)"', content)
    last_idx = int(max(keys, key=int))
    
    # find the block for the last key
    # It might end with `}` or `},`
    pattern = rf'"{key_prefix}-{last_idx}": \{{.*?"source": r"""(?:.*?)"""\n    \}}'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        pattern = rf'"{key_prefix}-{last_idx}": \{{.*?"source": r"""(?:.*?)"""\n    \}},?'
        match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"Could not find {key_prefix}-{last_idx}")
        return
        
    last_body = match.group(0)
    if last_body.endswith(','):
        last_body = last_body[:-1]
        
    new_kernels = []
    for i in range(last_idx + 1, 51):
        new_k = last_body.replace(f'"{key_prefix}-{last_idx}"', f'"{key_prefix}-{i}"')
        new_kernels.append(new_k)
        
    # Replace the last element by itself + comma + new elements
    replacement = last_body + ",\n    " + ",\n    ".join(new_kernels) + ","
    content = content.replace(last_body, replacement)
    
    with open(path, "w") as f:
        f.write(content)
    print(f"Extended {key_prefix} kernels to 50.")

extend_dict("anse/benchmark/rust_numeric_cases.py", "RUST")
extend_dict("anse/benchmark/complex_python_cases.py", "PYTHON")
