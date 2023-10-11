import ast


def sanity_check(function_code) -> bool:
    """Check for syntax errors and function signature."""
    try:
        # Check if the code contains any import statements
        if "import " in function_code:
            return False, "Illegal imports detected."

        code = function_code
        tree = ast.parse(code)
        func_def = tree.body[0]
        if (
            isinstance(func_def, ast.FunctionDef)
            and func_def.name == "motor_value"
        ):
            return True, ""
        else:
            return False, "Incorrect function signature."
    except SyntaxError as e:
        return False, "Syntax error."