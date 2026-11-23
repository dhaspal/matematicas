import sympy as sp
from tokenize import TokenError
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor


TRANSFORMACIONES = standard_transformations + (implicit_multiplication_application, convert_xor)
PERSMITIDOS = {"x", "y", "z", "a", "b", "c", "t"}


def parsear_expresion(texto: str, variables_extra: dict[str, sp.Symbol] | None = None):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Escribe una expresión antes de calcular.")
    texto = texto.strip().replace("π", "pi")
    locales = {"pi": sp.pi, "E": sp.E, "exp": sp.exp, "sin": sp.sin, "cos": sp.cos,
               "tan": sp.tan, "sqrt": sp.sqrt, "ln": sp.log, "log": sp.log}
    locales.update({nombre: sp.Symbol(nombre) for nombre in PERSMITIDOS})
    if variables_extra:
        locales.update(variables_extra)
    try:
        return parse_expr(texto, local_dict=locales, transformations=TRANSFORMACIONES, evaluate=True)
    except (SyntaxError, TypeError, TokenError, NameError, AttributeError):
        raise ValueError("No pude entender esa expresión.")

