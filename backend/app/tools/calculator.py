import ast
import operator
from typing import Any

# Supported math operators for safe evaluation
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return safe_eval_math(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = safe_eval_math(node.left)
        right = safe_eval_math(node.right)
        if op_type is ast.Div and right == 0:
            raise ZeroDivisionError("division by zero")
        return OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = safe_eval_math(node.operand)
        return OPERATORS[op_type](operand)
    else:
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

def execute_calculator(expression: str) -> dict[str, Any]:
    """Safely evaluates an arithmetic expression."""
    clean_expr = expression.strip().replace("^", "**")
    try:
        parsed = ast.parse(clean_expr, mode="eval")
        val = safe_eval_math(parsed)
        return {
            "result": round(val, 6) if isinstance(val, float) else val,
            "expression": clean_expr
        }
    except Exception as e:
        return {
            "is_error": True,
            "content": f"Calculator Error: {type(e).__name__}: {str(e)}",
            "expression": clean_expr
        }
