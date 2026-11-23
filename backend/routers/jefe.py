import random
import sympy as sp
from fastapi import APIRouter

router = APIRouter(prefix="/api/jefe", tags=["jefe"])

@router.get("/generar")
def generar():
    x, y = sp.symbols("x y")
    a = random.randint(1, 3)
    funcion = a * x**2 + y**2
    restriccion = x + y - 4
    gradiente = [sp.diff(funcion, x), sp.diff(funcion, y)]
    lam = sp.Symbol("lambda")
    ecuaciones = [
        gradiente[0] - lam * sp.diff(restriccion, x),
        gradiente[1] - lam * sp.diff(restriccion, y),
        restriccion,
    ]
    solucion = sp.solve(ecuaciones, (x, y, lam), dict=True)[0]
    punto_texto = f"({sp.sstr(solucion[x])}, {sp.sstr(solucion[y])})"
    etapas = [
        {"tipo": "gradiente", "pregunta": "Calcula el gradiente de f.", "respuesta": f"({gradiente[0]}, {gradiente[1]})",
         "opciones": opciones_jefe(
             f"({gradiente[0]}, {gradiente[1]})",
             rf"\left({sp.latex(gradiente[0])}, {sp.latex(gradiente[1])}\right)",
             [
                 (f"({sp.diff(funcion, y)}, {sp.diff(funcion, x)})", rf"\left({sp.latex(sp.diff(funcion, y))}, {sp.latex(sp.diff(funcion, x))}\right)"),
                 (f"({gradiente[0] + 1}, {gradiente[1]})", rf"\left({sp.latex(gradiente[0] + 1)}, {sp.latex(gradiente[1])}\right)"),
                 (f"(0, {gradiente[1]})", rf"\left(0, {sp.latex(gradiente[1])}\right)")
             ]), "pista": "Deriva respecto de x y luego respecto de y."},
        {"tipo": "sistema", "pregunta": "Indica x+y bajo la restricción x+y=4.", "respuesta": "4",
         "opciones": opciones_jefe("4", "4", [("2", "2"), ("3", "3"), ("8", "8")]), "pista": "La restricción ya está planteada."},
        {"tipo": "critico", "pregunta": "Calcula el punto crítico (x, y).", "respuesta": punto_texto.replace(" ", ""),
         "opciones": opciones_jefe(punto_texto.replace(" ", ""), punto_texto.replace(" ", ""), [("(1,3)", "(1,3)"), ("(3,1)", "(3,1)"), ("(4,0)", "(4,0)")]), "pista": "Iguala ∇f = λ∇g."},
    ]
    return {"funcion": sp.latex(funcion), "restriccion": sp.latex(restriccion),
            "gradiente": sp.latex(sp.Matrix(gradiente)), "etapas": etapas,
            "vidas": 3, "vida_jefe": 100}

@router.post("/verificar-etapa")
def verificar_etapa(payload: dict):
    respuesta = str(payload.get("respuesta", "")).strip().replace(" ", "")
    esperada = str(payload.get("esperada", "")).strip().replace(" ", "")
    normalizada = respuesta.replace(" ", "")
    # También admite expresiones simbólicas simples.
    correcto = normalizada == esperada
    try:
        correcto = correcto or sp.simplify(parsear_simple(normalizada) - parsear_simple(esperada)) == 0
    except Exception:
        pass
    return {"correcto": correcto, "mensaje": "Etapa superada." if correcto else "Respuesta incorrecta. Usa la pista si la necesitas."}

def parsear_simple(texto):
    return sp.sympify(texto.replace("^", "**"), locals={"x": sp.Symbol("x"), "y": sp.Symbol("y")})

def opciones_jefe(valor_correcto, latex_correcto, distractores):
    opciones = [{"valor": valor_correcto, "latex": latex_correcto}, *[
        {"valor": valor, "latex": latex} for valor, latex in distractores
    ]]
    random.shuffle(opciones)
    return opciones
