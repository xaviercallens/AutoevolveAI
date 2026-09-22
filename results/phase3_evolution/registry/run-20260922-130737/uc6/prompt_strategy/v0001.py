"""Default swappable prompt strategy component for ANSE (Directive D8)."""

def format_pain_prompt(
    task: str,
    code: str,
    energy: float,
    category: str,
    returncode: int,
    stderr: str,
    stdout: str,
    model_tier: str = ">3B",
    test_feedback: str = "",
) -> str:
    feedback = f"{test_feedback}\n" if test_feedback else ""
    if model_tier == "<=3B":
        code_snip = code[:200] if code else "(no code block found)"
        stderr_snip = stderr[:200] if stderr else "(empty)"
        return (
            f"TASK: {task}\n\n"
            f"PAIN SIGNAL: Your previous attempt failed with Energy {energy:.1f} ({category}).\n"
            f"Failing code summary:\n```python\n{code_snip}\n```\n"
            f"Execution feedback:\n---\n{feedback}Return code: {returncode}\nStderr:\n{stderr_snip}\n---\n"
            "Analyze the failure and provide the complete fixed Python code in a ```python ... ``` block."
        )
    else:
        code_snip = code[-4000:] if code else "(no code block was found in your reply)"
        stderr_snip = stderr[-1000:] if stderr else "(empty)"
        stdout_snip = stdout[-1000:] if stdout else "(empty)"
        return (
            f"TASK: {task}\n\n"
            f"PAIN SIGNAL: Your previous attempt failed with Energy {energy:.1f} ({category}).\n"
            f"Your previous code:\n```python\n{code_snip}\n```\n"
            f"Execution feedback:\n---\n{feedback}Return code: {returncode}\nStderr:\n{stderr_snip}\nStdout:\n{stdout_snip}\n---\n"
            "Analyze the failure, correct the bug, and provide the complete fixed Python code in a ```python ... ``` block."
        )
