import random
import re
import sympy as sp
from fastapi import APIRouter, HTTPException, Query
from models.casos_schemas import AcusarRequest, VerificarPruebaRequest
from services.casos.generador import crear_caso


router = APIRouter(prefix="/api/casos", tags=["casos"])


def _random_seed():
    return str(random.randint(100000, 999999))


@router.get("/generar")
def generar(
    dificultad: str = Query("facil", pattern="^(facil|medio|dificil)$"),
    seed: str | None = None,
):
    seed = seed.strip()[:80] if seed and seed.strip() else _random_seed()
    try:
        caso = crear_caso(seed, dificultad)
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"No pude generar el caso: {error}")
    public = {key: value for key, value in caso.items() if not key.startswith("_")}
    return public


def _normalizar(texto):
    return re.sub(r"\s+", "", str(texto).upper())


def _comparar(prueba_id, respuesta, solucion):
    normalizada = _normalizar(respuesta)
    if prueba_id == "hora":
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", normalizada)
        if not match:
            return False
        actual = int(match.group(1)) * 60 + int(match.group(2))
        smatch = re.fullmatch(r"(\d{1,2}):(\d{2})", str(solucion))
        if not smatch:
            return False
        esperada = int(smatch.group(1)) * 60 + int(smatch.group(2))
        return abs(actual - esperada) <= 5
    if prueba_id == "sangre":
        if normalizada in {"SI", "SÍ", "S", "1", "LEtal".upper()}:
            return bool(solucion >= 25)
        if normalizada in {"NO", "N", "0"}:
            return bool(solucion < 25)
        try:
            return abs(float(normalizada.replace(",", ".")) - float(solucion)) / max(abs(float(solucion)), 1) <= 0.01
        except ValueError:
            return False
    if prueba_id == "vector":
        try:
            return int(normalizada) == int(solucion)
        except ValueError:
            return False
    if prueba_id == "hill":
        return normalizada == _normalizar(solucion)
    if prueba_id == "lagrange":
        match = re.fullmatch(r"\(([-+]?\d+(?:[.,]\d+)?),([-+]?\d+(?:[.,]\d+)?)\)", normalizada)
        if not match:
            return False
        actual = (float(match.group(1).replace(",", ".")), float(match.group(2).replace(",", ".")))
        return abs(actual[0] - solucion[0]) <= 0.05 and abs(actual[1] - solucion[1]) <= 0.05
    return False


def _pasos(prueba_id, caso):
    prueba = next(item for item in caso["pruebas"] if item["id"] == prueba_id)
    solution = caso["_solutions"][prueba_id]
    data = prueba["datos"]
    if prueba_id == "hora":
        ta = sp.Integer(data["Ta"])
        t, k = sp.Symbol("t", positive=True), sp.Symbol("k", positive=True)
        measured = sp.Float(data["temperatura"])
        return [
            {"titulo": "Modelo de enfriamiento", "explicacion": "Se sustituye la temperatura ambiente y la temperatura medida.", "latex": rf"T(t)={ta}+({37-ta})e^{{-kt}}"},
            {"titulo": "Despeja el tiempo", "explicacion": "Se aisla el término exponencial y se aplica el logaritmo natural.", "latex": rf"t=-\frac{{\ln(({sp.latex(measured)}-{ta})/(37-{ta}))}}{{{sp.latex(data['k'])}}}"},
            {"titulo": "Resultado", "explicacion": "La hora estimada corresponde a la hora de hallazgo menos el tiempo transcurrido.", "latex": rf"{solution}"},
        ], {"tipo": "derivada", "Ta": data["Ta"], "temperatura": data["temperatura"], "k": data["k"], "t": float(solution.replace(":", ".")) if False else 3.0}
    if prueba_id == "sangre":
        a, k, t1, t2 = data["A"], data["k"], data["t1"], data["t2"]
        return [
            {"titulo": "Antiderivada", "explicacion": "Se integra la concentración exponencial.", "latex": rf"\int {a}e^{{-{k}t}}\,dt"},
            {"titulo": "Evalúa los límites", "explicacion": "Se resta el valor inferior del valor superior.", "latex": rf"\left[{a}/{k}e^{{-{k}t}}\right]_{{{t1}}}^{{{t2}}}"},
            {"titulo": "Dosis acumulada", "explicacion": "El resultado se compara con el umbral forense.", "latex": f"{solution:.4f}"},
        ], caso["_graphs"]["sangre"]
    if prueba_id == "vector":
        a, b = data["A"], data["B"]
        return [
            {"titulo": "Dirección", "explicacion": "Se resta el punto inicial al punto de impacto final.", "latex": rf"d=B-A={sp.latex(sp.Matrix(b)-sp.Matrix(a))}"},
            {"titulo": "Distancia punto-recta", "explicacion": "Para cada posición se calcula la distancia a la trayectoria.", "latex": r"d(P,r)=\frac{|(P-A)\times d|}{|d|}"},
            {"titulo": "Posición compatible", "explicacion": "La posición con distancia mínima coincide con la trayectoria.", "latex": str(solution)},
        ], caso["_graphs"]["vector"]
    if prueba_id == "hill":
        matrix = sp.Matrix(data["matriz"])
        inverse = matrix.inv_mod(26)
        return [
            {"titulo": "Determinante", "explicacion": "Se obtiene el determinante y su inverso módulo 26.", "latex": rf"\det(K)={matrix.det()}"},
            {"titulo": "Inverso modular", "explicacion": "SymPy calcula la matriz inversa módulo 26.", "latex": sp.latex(inverse)},
            {"titulo": "Descifra los bloques", "explicacion": "Cada bloque se multiplica por la matriz inversa y se reduce módulo 26.", "latex": rf"\text{{Resultado: }}{solution}"},
        ], {"tipo": "matriz", "matriz": data["matriz"]}
    punto = solution
    data = prueba["datos"]
    return [
        {"titulo": "Función objetivo", "explicacion": "Se define la distancia al cuadrado y la restricción.", "latex": rf"(x-{data['a']})^2+(y-{data['b']})^2"},
        {"titulo": "Sistema de Lagrange", "explicacion": "Se iguala el gradiente a lambda por el gradiente de la restricción.", "latex": rf"\nabla f=\lambda\nabla({data['p']}x+{data['q']}y-{data['c']})"},
        {"titulo": "Punto crítico", "explicacion": "Se resuelve el sistema y se obtiene el punto óptimo.", "latex": rf"\left({punto[0]:.2f},{punto[1]:.2f}\right)"},
    ], caso["_graphs"]["lagrange"]


@router.post("/verificar-prueba")
def verificar_prueba(peticion: VerificarPruebaRequest):
    if not peticion.respuesta or len(peticion.respuesta.strip()) == 0:
        raise HTTPException(status_code=422, detail="Debes escribir una respuesta.")
    try:
        caso = crear_caso(peticion.seed, peticion.dificultad)
    except Exception:
        raise HTTPException(status_code=422, detail="No se pudo reconstruir el caso.")
    if peticion.prueba_id not in {p["id"] for p in caso["pruebas"]}:
        raise HTTPException(status_code=404, detail="La prueba no existe en este caso.")
    solution = caso["_solutions"][peticion.prueba_id]
    correcta = _comparar(peticion.prueba_id, peticion.respuesta, solution)
    if correcta:
        pasos, grafica = _pasos(peticion.prueba_id, caso)
        solution_public = str(solution)
        if peticion.prueba_id == "lagrange":
            solution_public = f"({solution[0]:.2f},{solution[1]:.2f})"
        suspects_to_discard = [
            suspect["id"] for suspect in caso["sospechosos"]
            if suspect["id"] != caso["_culprit"]
        ]
        return {
            "correcta": True,
            "solucion": solution_public,
            "pasos": pasos,
            "interpretacion": "La prueba confirma el perfil matemático compatible y descarta a los sospechosos restantes.",
            "sospechosos_descartados": suspects_to_discard,
            "grafica": grafica,
            "retroalimentacion": "Prueba resuelta. La evidencia fue añadida a tu libreta.",
        }
    feedback = {
        "hora": "Revisa la relación entre temperatura, constante k y el tiempo transcurrido.",
        "sangre": "Integra en el intervalo y compara el resultado con 25.",
        "vector": "Calcula la distancia de cada posición a la recta definida por A y B.",
        "hill": "Reduce el mensaje de nuevo bloque por bloque módulo 26.",
        "lagrange": "Escribe el punto como (x,y) y verifica el sistema de restricciones.",
    }[peticion.prueba_id]
    return {
        "correcta": False,
        "solucion": None,
        "pasos": [],
        "interpretacion": "",
        "sospechosos_descartados": [],
        "grafica": None,
        "retroalimentacion": feedback,
    }


@router.get("/pista")
def pista(seed: str, dificultad: str = Query("facil", pattern="^(facil|medio|dificil)$"),
          prueba_id: str = Query(..., min_length=1, max_length=40), nivel: int = Query(1, ge=1, le=2)):
    hints = {
        "hora": ["Despeja el tiempo de la ecuación de enfriamiento.", "Aplica logaritmo natural y resta a la hora del hallazgo."],
        "sangre": ["Calcula una integral definida entre t1 y t2.", "La antiderivada es (A/k)e^(-kt); evalúa los límites."],
        "vector": ["Forma d = B-A y usa la distancia punto-recta.", "La posición correcta tiene la distancia mínima/cero."],
        "hill": ["Necesitas el determinante y la inversa módulo 26.", "Multiplica cada bloque cifrado por K^-1 mod 26."],
        "lagrange": ["Forma ∇f = λ∇g con la restricción.", "Resuelve el sistema y sustituye x,y en la función."],
    }
    if prueba_id not in hints:
        raise HTTPException(status_code=404, detail="Prueba no encontrada.")
    return {"nivel": nivel, "pista": hints[prueba_id][nivel - 1]}


@router.post("/acusar")
def acusar(peticion: AcusarRequest):
    caso = crear_caso(peticion.seed, peticion.dificultad)
    suspect_ids = {s["id"] for s in caso["sospechosos"]}
    if peticion.sospechoso_id not in suspect_ids:
        raise HTTPException(status_code=404, detail="El sospechoso no existe.")
    correcto = peticion.sospechoso_id == caso["_culprit"]
    culprit = next(s for s in caso["sospechosos"] if s["id"] == caso["_culprit"])
    return {
        "correcto": correcto,
        "culpable": culprit["nombre"] if correcto else None,
        "resumen_final": (
            "La cadena de evidencia mostró que solo el perfil compatible sobrevivió a las cinco pruebas: "
            "enfriamiento, farmacocinética, trayectoria, Hill y optimización."
            if correcto else "La acusación no coincide con el perfil reconstruido por las pruebas."
        ),
    }
