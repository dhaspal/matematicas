import random
import sympy as sp

x = sp.Symbol("x")


def generar(dificultad="facil"):
    nivel = 1 if dificultad == "facil" else 2 if dificultad == "medio" else 3
    coef = random.randint(1, 5)
    pot = random.randint(2, 3 if nivel == 1 else 5)
    if nivel == 1:
        expresion = sp.Add(sp.Integer(coef) * x**pot, random.randint(1, 5) * x)
    else:
        expresion = (sp.Integer(coef) * x**pot + random.randint(1, 4)) * sp.sin(x)
    derivada = sp.diff(expresion, x)
    return {
        "expresion": expresion,
        "respuesta": derivada,
        "enunciado": rf"\text{{Calcula }} \frac{{d}}{{dx}}\left({sp.latex(expresion)}\right)",
    }


def resolver_con_pasos(expresion, variable=x):
    expresion = sp.sympify(expresion)
    derivada = sp.diff(expresion, variable)
    pasos = [
        {"titulo": "Identifica la operación", "explicacion": "Reconocemos la variable respecto de la cual se deriva.", "latex": rf"\frac{{d}}{{d{sp.latex(variable)}}}\left({sp.latex(expresion)}\right)", "regla": "derivada"},
        {"titulo": "Aplica las reglas", "explicacion": "Se usan potencia, producto y la derivada de funciones según corresponda.", "latex": sp.latex(derivada), "regla": "potencia y producto"},
    ]
    return pasos, derivada
