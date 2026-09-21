with open("anse/symbolic/sandbox.py") as f:
    code = f.read()

old = """    try:
        import docker  # type: ignore[import-untyped]
        from docker.errors import DockerException  # type: ignore[import-untyped]
        client = docker.from_env()
    except (ImportError, OSError, subprocess.SubprocessError, Exception) as exc:
        is_docker_exc = type(exc).__name__ == "DockerException" or type(exc).__name__ == "ImportError" or isinstance(exc, (OSError, subprocess.SubprocessError))"""

new = """    try:
        import docker  # type: ignore[import-untyped]
        client = docker.from_env()
    except (ImportError, OSError, subprocess.SubprocessError, Exception) as exc:
        is_docker_exc = type(exc).__name__ == "DockerException" or type(exc).__name__ == "ImportError" or isinstance(exc, (OSError, subprocess.SubprocessError))"""

code = code.replace(old, new)
with open("anse/symbolic/sandbox.py", "w") as f:
    f.write(code)
