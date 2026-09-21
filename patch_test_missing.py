with open("tests/phase1/test_sandbox.py") as f:
    code = f.read()

old = """    result = sandbox.execute(code, force_tier=2)
    assert result.returncode == 0
    assert result.tier_used == 2
    assert "[WARN] Docker unavailable" in result.stderr"""

new = """    result = sandbox.execute(code, force_tier=2)
    assert result.returncode == -1
    assert result.tier_used == 2
    assert "SANDBOX_UNAVAILABLE" in result.stderr
    assert result.isolation == "none\""""

code = code.replace(old, new)
with open("tests/phase1/test_sandbox.py", "w") as f:
    f.write(code)
