import re

def extend_file(filename, prefix, last_idx, end_pattern):
    with open(filename, 'r') as f:
        content = f.read()
    
    # find the block for last_idx
    # It starts with f'"{prefix}-{last_idx}": {'
    start_str = f'    "{prefix}-{last_idx}": {{'
    start_idx = content.find(start_str)
    
    # find the next `    },` or `    }\n}`
    end_idx = content.find('    },\n}', start_idx)
    if end_idx == -1:
        end_idx = content.find('    }\n}', start_idx)
    if end_idx == -1:
        print("Could not find end")
        return
        
    block = content[start_idx:end_idx+5]
    
    new_blocks = []
    for i in range(last_idx + 1, 51):
        new_b = block.replace(f'"{prefix}-{last_idx}"', f'"{prefix}-{i}"')
        new_blocks.append(new_b)
        
    replacement = block + ",\n" + ",\n".join(new_blocks)
    content = content[:start_idx] + replacement + content[end_idx+5:]
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Extended {filename}")

extend_file("anse/benchmark/rust_numeric_cases.py", "RUST", 30, "")
extend_file("anse/benchmark/complex_python_cases.py", "PYTHON", 30, "")
