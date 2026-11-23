import random
import sympy as sp


def generar(dificultad="facil"):
    u = sp.Matrix([random.randint(-5, 5) for _ in range(2)])
    v = sp.Matrix([random.randint(-5, 5) for _ in range(2)])
    operacion = random.choice(["punto", "suma", "norma"])
    if operacion == "punto":
        respuesta, enunciado = u.dot(v), rf"{sp.latex(u)} \cdot {sp.latex(v)}"
    elif operacion == "suma":
        respuesta, enunciado = u + v, rf"{sp.latex(u)} + {sp.latex(v)}"
    else:
        respuesta, enunciado = u.norm(), rf"\left\lVert {sp.latex(u)} \right\rVert"
    return {"respuesta": respuesta, "enunciado": enunciado, "operacion": operacion,
            "u": [int(x) for x in u], "v": [int(x) for x in v]}


def calcular(operacion, u, v=None):
    um = sp.Matrix(u)
    vm = sp.Matrix(v) if v else None
    if operacion == "punto":
        result = um.dot(vm)
    elif operacion == "suma":
        result = um + vm
    elif operacion == "cruz":
        result = sp.Matrix.hstack(um, vm).det() if False else um.cross(vm)
    elif operacion == "norma":
        result = um.norm()
    elif operacion == "proyeccion":
        result = (um.dot(vm) / vm.dot(vm)) * vm
    else:
        raise ValueError("Operación vectorial no válida.")
    pasos = [
        {"titulo": "Sustituye los vectores", "explicacion": "Se colocan las componentes dadas en la operación elegida.", "latex": sp.latex(um)},
        {"titulo": "Resultado", "explicacion": "El cálculo se simplifica componente a componente.", "latex": sp.latex(result)},
    ]
    return result, pasos
