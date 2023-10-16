import ast
from typing import Tuple

def sanity_check(function_code) -> Tuple[bool, str]:
    """Check for syntax errors and function signature."""
    try:
        # Check if the code contains any import statements
        # if "import " in function_code:
        #     return False, "Illegal imports detected."

        code = function_code
        tree = ast.parse(code)

        def has_main_function(node):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                return True
            return False

        if any(has_main_function(node) for node in ast.walk(tree)):
            return True, ""
        else:
            return False, "Incorrect function signature."
    except SyntaxError as e:
        return False, "Syntax error."
