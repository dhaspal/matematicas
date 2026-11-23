import random
import sympy as sp


def generar(dificultad="facil"):
    n = 2
    a = sp.Matrix([[random.randint(-4, 5) for _ in range(n)] for _ in range(n)])
    b = sp.Matrix([[random.randint(-4, 5) for _ in range(n)] for _ in range(n)])
    operacion = random.choice(["suma", "producto", "determinante"])
    if operacion == "suma": result = a + b
    elif operacion == "producto": result = a * b
    else: result = a.det()
    operacion_latex = " + " if operacion == "suma" else r" \cdot " if operacion == "producto" else ""
    enunciado = rf"\text{{Calcula }} {sp.latex(a)}{operacion_latex}{sp.latex(b)}" if operacion != "determinante" else rf"\text{{Calcula }} \det\left({sp.latex(a)}\right)"
    return {"respuesta": result, "enunciado": enunciado,
            "operacion": operacion, "a": a.tolist(), "b": b.tolist()}


def calcular(operacion, a, b=None):
    am = sp.Matrix(a)
    bm = sp.Matrix(b) if b is not None else None
    pasos = [{"titulo": "Matriz inicial", "explicacion": "Se escribe la matriz o matrices dadas.", "latex": sp.latex(am)}]
    if operacion == "suma":
        result = am + bm
    elif operacion == "producto":
        result = am * bm
    elif operacion == "determinante":
        result = am.det()
    elif operacion == "inversa":
        if am.det() == 0:
            raise ValueError("La matriz no tiene inversa porque su determinante es cero.")
        result = am.inv()
    elif operacion == "gauss":
        matriz = am.row_join(sp.eye(am.rows))
        pasos.append({"titulo": "Matriz aumentada", "explicacion": "Se agrega la identidad para transformar la matriz.", "latex": sp.latex(matriz)})
        escalonada, pivots = matriz.rref()
        for indice, fila in enumerate(escalonada.tolist()):
            pasos.append({"titulo": f"Operación de fila {indice + 1}", "explicacion": "Se realizan operaciones elementales hasta alcanzar la forma escalonada reducida.", "latex": sp.latex(sp.Matrix(escalonada.tolist()))})
        return escalonada, pasos
    else:
        raise ValueError("Operación matricial no válida.")
    pasos.append({"titulo": "Resultado", "explicacion": "El cálculo queda expresado en la matriz final.", "latex": sp.latex(result)})
    return result, pasos
