import subprocess
BASE_LEAN = """
theorem modus_tollens {p q : Prop} (h1 : p → q) (h2 : ¬q) : ¬p := by
  intro hp
"""
with open("/tmp/test.lean", "w") as f:
    f.write(BASE_LEAN)
res = subprocess.run(["lean", "/tmp/test.lean"], capture_output=True, text=True)
print("STDOUT:", repr(res.stdout))
print("STDERR:", repr(res.stderr))
