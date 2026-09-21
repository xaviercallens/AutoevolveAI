
files_to_patch = ["tests/phase1/test_agent_loop.py", "tests/phase1/test_e2e_phase1.py"]

for fpath in files_to_patch:
    with open(fpath) as f:
        content = f.read()

    if "import pytest" not in content:
        content = "import pytest\nimport shutil\n" + content
    elif "import shutil" not in content:
        content = content.replace("import pytest", "import pytest\nimport shutil")

    lines = content.split("\n")
    new_lines = []

    skip_decorator = (
        "@pytest.mark.skipif(shutil.which('docker') is None, reason=\"Requires docker\")"
    )

    for line in lines:
        if line.startswith("def test_") or line.startswith("class Test"):
            if new_lines and new_lines[-1] != skip_decorator:
                new_lines.append(skip_decorator)
        new_lines.append(line)

    with open(fpath, "w") as f:
        f.write("\n".join(new_lines))
