"""
Utility functions for static and dynamic code analysis.

This module includes functions for syntax validation, quality scoring (linting,
complexity, typing, docstrings), and functional correctness checking. These
functions are designed to be pure or to have their side effects managed by
callers, often using decorators like `@safe` from the `returns` library.
"""

import ast
import json
import os
import re
import subprocess
import tempfile
import textwrap
from pathlib import Path

import dspy

from . import config
from .evaluation import CodeQualityScores, TestCase


def extract_python_code(text: str) -> str:
    """Extracts Python code from a markdown block, returns original text if no block is found."""
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    return match.group(1).strip() if match else text


def check_syntax(code: str) -> tuple[bool, str | None, str | None]:
    """
    Checks for valid Python syntax and a top-level function definition.

    Returns a tuple indicating validity, the function name, and an error message.
    This format is consumed by a wrapper that converts it into a `Result` monad.
    """
    try:
        tree = ast.parse(code)
        func_node = next((n for n in tree.body if isinstance(n, ast.FunctionDef)), None)
        if not func_node:
            return False, None, "No top-level function definition found."
        return True, func_node.name, None
    except SyntaxError as e:
        return False, None, f"Syntax Error: {e}"


def _get_ast_based_scores(tree: ast.AST, func_name: str | None) -> tuple[float, float]:
    """Calculates docstring and typing scores from a parsed AST."""
    all_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if not all_funcs:
        return 0.0, 0.0

    target_funcs = [f for f in all_funcs if f.name == func_name] if func_name else all_funcs
    if not target_funcs:
        return 0.0, 0.0

    docstring_score = sum(1.0 for f in target_funcs if ast.get_docstring(f)) / len(target_funcs)

    typed_elements, typeable_elements = 0, 0
    for func_node in target_funcs:
        args = func_node.args
        typed_elements += sum(1 for arg in args.args if arg.annotation is not None)
        typed_elements += 1 if func_node.returns is not None else 0
        typeable_elements += len(args.args) + 1

    typing_score = typed_elements / typeable_elements if typeable_elements > 0 else 0.0
    return docstring_score, typing_score


def check_code_quality(code: str, func_name: str | None = None) -> CodeQualityScores:
    """
    Analyzes Python code for quality metrics using flake8 and AST.

    This function performs I/O by creating a temporary file and running a
    subprocess. It is designed to be wrapped by a decorator like `@safe`
    or `@impure_safe` to handle potential exceptions.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)

    try:
        # Exceptions from subprocess.run will be caught by the @safe wrapper in the caller.
        result = subprocess.run(
            [
                "flake8",
                f"--max-complexity={config.FLAKE8_MAX_COMPLEXITY}",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            check=False,  # We manually check output, not exit code.
        )
        all_issues = result.stdout.strip().splitlines() if result.stdout else []

        complexity_warnings = [
            issue for issue in all_issues if config.FLAKE8_COMPLEXITY_CODE in issue
        ]
        linting_issues = [
            issue for issue in all_issues if config.FLAKE8_COMPLEXITY_CODE not in issue
        ]

        complexity_score = 1.0 if not complexity_warnings else 0.0
        linting_score = max(0.0, 1.0 - (config.LINTING_PENALTY_PER_ISSUE * len(linting_issues)))

        # A SyntaxError here will be caught by the @safe wrapper in the caller.
        tree = ast.parse(code)
        docstring_score, typing_score = _get_ast_based_scores(tree, func_name)

        return CodeQualityScores(
            linting_score=linting_score,
            complexity_score=complexity_score,
            typing_score=typing_score,
            docstring_score=docstring_score,
            linting_issues=linting_issues,
        )
    finally:
        # Ensure the temporary file is always cleaned up.
        if tmp_path.exists():
            os.unlink(tmp_path)


def _build_execution_script(func_name: str, test_case: TestCase) -> str:
    """Constructs a Python script to execute a function with a given test case."""
    args_json = json.dumps(test_case.args)
    kwargs_json = json.dumps(test_case.kwargs)

    return textwrap.dedent(
        f"""
        import json
        import sys

        # This script assumes the function '{func_name}' has been defined in the
        # execution context by the dspy.PythonInterpreter.

        args = json.loads('''{args_json}''')
        kwargs = json.loads('''{kwargs_json}''')

        result = {func_name}(*args, **kwargs)
        print(json.dumps(result))
        """
    )


def check_functional_correctness(code: str, func_name: str, test_cases: list[TestCase]) -> int:
    """
    Executes test cases against code in a sandboxed Python interpreter.

    This function can raise exceptions if the provided code is invalid or if
    the test execution fails unexpectedly. It is designed to be wrapped by a

    decorator like `@safe` to handle these failures gracefully.
    """
    if not test_cases:
        return 0

    passed_count = 0
    # A failure in the interpreter setup will be caught by the @safe wrapper.
    with dspy.PythonInterpreter() as interp:
        interp.execute(code)  # Define the function in the interpreter's scope.
        for test in test_cases:
            # Handle failures for individual test cases gracefully to allow others to run.
            try:
                exec_script = _build_execution_script(func_name, test)
                actual_output_json = interp.execute(exec_script)
                actual_output = json.loads(actual_output_json)

                # Normalize expected output to ensure consistent comparison.
                normalized_expected_output = json.loads(json.dumps(test.expected_output))
                if actual_output == normalized_expected_output:
                    passed_count += 1
            except Exception:
                # If a single test case fails to execute or assert, continue to the next.
                continue
    return passed_count
