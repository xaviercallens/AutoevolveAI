with open("anse/symbolic/sandbox.py") as f:
    code = f.read()

old = """        is_docker_exc = type(exc).__name__ == "DockerException" or type(exc).__name__ == "ImportError" or isinstance(exc, (OSError, subprocess.SubprocessError))"""
new = """        is_docker_exc = type(exc).__name__ == "DockerException" or isinstance(exc, (ImportError, OSError, subprocess.SubprocessError))"""
code = code.replace(old, new)

with open("anse/symbolic/sandbox.py", "w") as f:
    f.write(code)
