import re

with open("scripts/execute_200_unified_eval_and_learn.py", "r") as f:
    content = f.read()

content = content.replace("100-Problem", "200-Problem")
content = content.replace("50 Advanced Mathematics", "100 Advanced Mathematics")
content = content.replace("25 High-Performance Rust", "50 High-Performance Rust")
content = content.replace("25 Complex Python", "50 Complex Python")
content = content.replace("100_unified_eval_report", "200_unified_eval_report")
content = content.replace("rl_energy_model_unified.pt", "rl_energy_model_unified_200.pt")
content = content.replace("dpo_100_unified_dataset", "dpo_200_unified_dataset")
content = content.replace("100 unified preference", "200 unified preference")
content = content.replace("100 preference pairs", "200 preference pairs")
content = content.replace("from scripts.execute_50_physics_math_tribunal import get_50_problems", "from scripts.execute_50_physics_math_tribunal import get_50_problems\nfrom scripts.execute_100_physics_math_tribunal import get_50_ultra_complex_problems")
content = content.replace("execute_50_math_physics_suite()", "execute_100_math_physics_suite()")
content = content.replace("Executing 50 Mathematics", "Executing 100 Mathematics")
content = content.replace("Completed 50 Math", "Completed 100 Math")

# Fix math problem loading
math_func_old = r"""def execute_100_math_physics_suite\(\) -> List\[ProblemEvaluationRecord\]:
    .*?
    problems = get_50_problems\(\)
    records: List\[ProblemEvaluationRecord\] = \[\]"""
math_func_new = r"""def execute_100_math_physics_suite() -> List[ProblemEvaluationRecord]:
    logger.info("Executing 100 Mathematics & Theoretical Physics Problems...")
    problems = get_50_problems() + get_50_ultra_complex_problems()
    records: List[ProblemEvaluationRecord] = []"""
content = re.sub(r"def execute_100_math_physics_suite\(\) -> List\[ProblemEvaluationRecord\]:.*?records: List\[ProblemEvaluationRecord\] = \[\]", math_func_new, content, flags=re.DOTALL)

content = content.replace("sorted(list(RUST_KERNELS.keys()))[:25]", "sorted(list(RUST_KERNELS.keys()))[:50]")
content = content.replace("list(PYTHON_BENCHMARKS.items())[:25]", "list(PYTHON_BENCHMARKS.items())[:50]")
content = content.replace("100 (50 Math/Physics Formal + 25 Rust SIMD + 25 Python Physics)", "200 (100 Math/Physics Formal + 50 Rust SIMD + 50 Python Physics)")
content = content.replace("Math & Physics Formal (50)", "Math & Physics Formal (100)")
content = content.replace("Rust Numerical Kernels (25)", "Rust Numerical Kernels (50)")
content = content.replace("Python Physics Kernels (25)", "Python Physics Kernels (50)")
content = content.replace("Total Evaluated Problems : 100", "Total Evaluated Problems : 200")
content = content.replace("total_records != 100", "total_records != 200")
content = content.replace("Expected 100, got", "Expected 200, got")
content = content.replace("math_records = execute_50_math_physics_suite()", "math_records = execute_100_math_physics_suite()")

with open("scripts/execute_200_unified_eval_and_learn.py", "w") as f:
    f.write(content)
print("patched")
