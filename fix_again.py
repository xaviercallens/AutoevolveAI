with open("tests/phase1/test_sandbox.py") as f:
    content = f.read()

old = """    assert result.returncode == 0
    assert "Docker unavailable, fell back to Tier-1" in result.stderr"""
new = '''    assert result.returncode == -1
    assert "SANDBOX_UNAVAILABLE" in result.stderr
    assert result.isolation == "none"'''

content = content.replace(old, new)
with open("tests/phase1/test_sandbox.py", "w") as f:
    f.write(content)
