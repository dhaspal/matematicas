import sympy as sp
from utils.parser import parsear_expresion


def verificar_expresion(respuesta_usuario: str, correcta: str, es_integral_indefinida: bool = False):
    try:
        usuario = parsear_expresion(respuesta_usuario)
        objetivo = parsear_expresion(correcta)
        if es_integral_indefinida:
            C = sp.Symbol("C")
            diferencia = sp.diff(sp.cancel(usuario - objetivo), sp.Symbol("x"))
            if sp.simplify(diferencia) == 0:
                return True
            for simbolo in (C,):
                objetivo_sin_c = objetivo.subs(simbolo, 0)
                usuario_sin_c = usuario.subs(simbolo, 0)
                if sp.simplify(sp.diff(usuario_sin_c - objetivo_sin_c, sp.Symbol("x"))) == 0:
                    return True
        if sp.simplify(sp.cancel(usuario - objetivo)) == 0:
            return True
        return False
    except ValueError as error:
        raise error
