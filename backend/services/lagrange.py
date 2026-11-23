import random
import sympy as sp

x, y, lam = sp.symbols("x y lambda")


def generar(dificultad="facil"):
    a = random.randint(1, 3)
    b = random.randint(1, 3)
    funcion = a * x**2 + b * y**2
    restriccion = x + y - random.randint(2, 6)
    puntos = sp.solve([sp.diff(funcion, x) - lam * sp.diff(restriccion, x),
                       sp.diff(funcion, y) - lam * sp.diff(restriccion, y),
                       restriccion], (x, y, lam), dict=True)
    return {"funcion": funcion, "restriccion": restriccion, "puntos": puntos,
            "enunciado": rf"\text{{Optimiza }} {sp.latex(funcion)} \text{{ sujeto a }} {sp.latex(restriccion)}=0"}


def resolver_con_pasos(funcion, restriccion):
    funcion = sp.sympify(funcion)
    restriccion = sp.sympify(restriccion)
    grad_f = [sp.diff(funcion, x), sp.diff(funcion, y)]
    grad_g = [sp.diff(restriccion, x), sp.diff(restriccion, y)]
    ecuaciones = [grad_f[0] - lam * grad_g[0], grad_f[1] - lam * grad_g[1], restriccion]
    puntos = sp.solve(ecuaciones, (x, y, lam), dict=True)
    pasos = [
        {"titulo": "Calcula gradientes", "explicacion": "El gradiente contiene las derivadas parciales de la función.", "latex": rf"\nabla f = \left({sp.latex(grad_f[0])},{sp.latex(grad_f[1])}\right)"},
        {"titulo": "Plantea la restricción", "explicacion": "También calculamos el gradiente de la restricción.", "latex": rf"\nabla g = \left({sp.latex(grad_g[0])},{sp.latex(grad_g[1])}\right)"},
        {"titulo": "Sistema de Lagrange", "explicacion": "Igualamos gradientes con el multiplicador y añadimos la restricción.", "latex": rf"\nabla f = \lambda\nabla g,\quad g(x,y)=0"},
        {"titulo": "Resuelve el sistema", "explicacion": "SymPy calcula los puntos críticos que cumplen todas las ecuaciones.", "latex": ",\\ ".join([sp.latex(p) for p in puntos])},
    ]
    return pasos, puntos
