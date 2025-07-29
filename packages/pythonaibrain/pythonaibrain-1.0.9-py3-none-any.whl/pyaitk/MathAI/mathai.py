import sympy as sp # pip install sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy.abc import _clash
import re
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

transformations = standard_transformations + (implicit_multiplication_application,)
local_dict = dict(_clash)

# Additional symbols
x, y, z, a, b, c, n, m, r, t, theta = sp.symbols('x y z a b c n m r t theta')

# Add custom dictionary for functions and constants
local_dict.update({
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'cot': sp.cot,
    'sec': sp.sec,
    'csc': sp.csc,
    'log': sp.log,
    'ln': sp.ln,
    'e': sp.E,
    'pi': sp.pi,
    'sqrt': sp.sqrt,
    'diff': sp.diff,
    'integrate': sp.integrate,
    'limit': sp.limit,
    'det': sp.det,
    'Matrix': sp.Matrix,
    'solve': sp.solve,
    'factor': sp.factor,
    'expand': sp.expand
})

def handle_equations(input_str):
    equations = input_str.split(" and ")
    parsed_eqs = []
    symbols_set = set()
    for eq in equations:
        lhs, rhs = eq.split("=")
        lhs = parse_expr(lhs, transformations=transformations, local_dict=local_dict)
        rhs = parse_expr(rhs, transformations=transformations, local_dict=local_dict)
        parsed_eqs.append(sp.Eq(lhs, rhs))
        symbols_set |= lhs.free_symbols | rhs.free_symbols
    solution = sp.solve(parsed_eqs, tuple(symbols_set), dict=True)
    return f"Solution: {solution}"

def handle_matrix(expr):
    matrix = parse_expr(expr, transformations=transformations, local_dict=local_dict)
    if isinstance(matrix, sp.Matrix):
        det = matrix.det()
        inv = matrix.inv() if matrix.det() != 0 else "Not Invertible"
        return f"Matrix: {matrix}\nDeterminant: {det}\nInverse: {inv}"
    return "Not a valid matrix expression."

def solve_expression(expr):
    try:
        if " and " in expr and "=" in expr:
            return handle_equations(expr)

        if expr.lower().startswith("matrix"):
            return handle_matrix(expr.split("=", 1)[-1].strip())

        parsed = parse_expr(expr, transformations=transformations, local_dict=local_dict, evaluate=False)
        simplified = sp.simplify(parsed)
        numeric = simplified.evalf()

        return f"Simplified: {simplified}\nNumeric: {numeric}"

    except Exception as e:
        return f"[ERROR] {str(e)}"

def MathAI(message: str = '1X + 2X - 3X'):
    expr = message.strip()
    result = solve_expression(expr)
    return result

