import random
import sympy as sp

x = sp.Symbol("x")


def generar(dificultad="facil"):
    coef = random.randint(1, 5)
    pot = random.randint(1, 4)
    expresion = sp.Integer(coef) * x**pot
    integral = sp.integrate(expresion, x)
    return {"expresion": expresion, "respuesta": integral, "enunciado": rf"\text{{Calcula }} \int {sp.latex(expresion)}\,dx"}


def resolver_con_pasos(expresion, definida=False, a=-1, b=2):
    expresion = sp.sympify(expresion)
    if definida:
        resultado = sp.integrate(expresion, (x, sp.Integer(a), sp.Integer(b)))
        pasos = [
            {"titulo": "Antiderivada", "explicacion": "Primero se obtiene una antiderivada de la función.", "latex": sp.latex(sp.integrate(expresion, x)), "regla": "integral indefinida"},
            {"titulo": "Evalúa los límites", "explicacion": "Se resta el valor en el límite inferior del valor en el superior.", "latex": rf"\left[{sp.latex(sp.integrate(expresion, x))}\right]_{{{a}}}^{{{b}}}", "regla": "Teorema fundamental"},
            {"titulo": "Resultado", "explicacion": "Este valor representa el área neta.", "latex": sp.latex(resultado)},
        ]
    else:
        resultado = sp.integrate(expresion, x)
        pasos = [
            {"titulo": "Identifica la regla", "explicacion": "Se aplica la regla de potencia para cada término.", "latex": sp.latex(expresion), "regla": "potencia"},
            {"titulo": "Integra", "explicacion": "Se suma uno al exponente y se divide por el nuevo exponente.", "latex": sp.latex(resultado) + "+C", "regla": "antiderivada"},
        ]
    return pasos, resultado
