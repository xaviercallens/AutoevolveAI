
with open("tests/phase1/test_sandbox.py") as f:
    content = f.read()

# Add imports
if "import pytest" not in content:
    content = "import pytest\nimport shutil\n" + content
elif "import shutil" not in content:
    content = content.replace("import pytest", "import pytest\nimport shutil")

# 1. pass trusted=True to all executions except for force_tier=2
content = content.replace("sandbox.execute(code)", "sandbox.execute(code, trusted=True)")

# 2. fix test_sandbox_tier2_docker_missing
old_missing = """    result = sandbox.execute(code, force_tier=2)
    assert result.returncode == 0
    assert result.tier_used == 2
    assert "[WARN] Docker unavailable" in result.stderr"""

new_missing = '''    result = sandbox.execute(code, force_tier=2)
    assert result.returncode == -1
    assert result.tier_used == 2
    assert "SANDBOX_UNAVAILABLE" in result.stderr
    assert result.isolation == "none"'''
content = content.replace(old_missing, new_missing)

with open("tests/phase1/test_sandbox.py", "w") as f:
    f.write(content)
