import random
import re
import sympy as sp
from fastapi import APIRouter, HTTPException, Query
from models.casos_schemas import AcusarRequest, CalcularPruebaRequest, VerificarPruebaRequest
from services.casos.generador import crear_caso


router = APIRouter(prefix="/api/casos", tags=["casos"])


def _random_seed():
    return str(random.randint(100000, 999999))


@router.post("/calcular-prueba")
def calcular_prueba(peticion: CalcularPruebaRequest):
    datos = peticion.datos
    try:
        if peticion.prueba_id == "hora":
            ta = sp.Float(str(datos["Ta"]), 6)
            temperatura = sp.Float(str(datos["temperatura"]), 6)
            k = sp.Float(str(datos["k"]), 6)
            hora_texto = str(datos["hora_hallazgo"]).strip()
            match = re.fullmatch(r"(\d{1,2})(?:[:.](\d{2}))?", hora_texto)
            if not match:
                raise ValueError("Escribe la hora del hallazgo como HH:MM, por ejemplo 20:30.")
            hallazgo_hora = int(match.group(1))
            hallazgo_minutos = int(match.group(2) or 0)
            if hallazgo_hora > 23 or hallazgo_minutos > 59:
                raise ValueError("La hora debe estar entre 00:00 y 23:59.")
            hora_hallazgo = sp.Float(hallazgo_hora + hallazgo_minutos / 60)
            if not (0 <= ta <= 40):
                raise ValueError("La temperatura ambiente debe estar entre 0 y 40 °C.")
            if not (ta < temperatura <= 37):
                raise ValueError("La temperatura medida debe estar por encima de la ambiental y no superar 37 °C.")
            if not (0 < k <= 1):
                raise ValueError("La constante k debe estar entre 0 y 1 h⁻¹.")
            t = -sp.log((temperatura - ta) / (sp.Float(37) - ta)) / k
            horas_transcurridas = float(t)
            if horas_transcurridas <= 0 or horas_transcurridas > 48:
                raise ValueError("Con estos datos el tiempo estimado no es razonable. Revisa temperatura y k.")
            hora_decimal = float(hora_hallazgo) - horas_transcurridas
            if hora_decimal < 0:
                hora_decimal = 24 + hora_decimal
            hh = int(hora_decimal)
            mm = int(round((hora_decimal - hh) * 60))
            if mm >= 60:
                hh = (hh + 1) % 24
                mm = 0
            derivative = -k * (temperatura - ta) * sp.exp(-k * 0)
            return {
                "resultado": f"{hh}:{mm:02d}",
                "valor": horas_transcurridas,
                "horas_transcurridas": round(horas_transcurridas, 2),
                "derivada": round(float(derivative), 3),
                "pasos": [
                    {"titulo": "Modelo de Newton", "explicacion": "Se sustituyen Ta, T(t) y k en el modelo de enfriamiento.", "latex": rf"T(t)={sp.latex(ta)}+(37-{sp.latex(ta)})e^{{-{sp.latex(k)}t}}"},
                    {"titulo": "Despeje con logaritmo", "explicacion": "Se despeja el tiempo transcurrido desde el fallecimiento.", "latex": rf"t=-\frac{{\ln((T(t)-T_a)/(37-T_a))}}{{k}}"},
                    {"titulo": "Tiempo calculado", "explicacion": "Se resta el tiempo transcurrido a la hora del hallazgo.", "latex": rf"t={float(t):.2f}\;\text{{h}},\quad hora={hh}:{mm:02d}"},
                    {"titulo": "Razón de enfriamiento", "explicacion": "La derivada indica cuántos grados cambia el cuerpo por hora en ese instante.", "latex": rf"dT/dt={float(derivative):.3f}\;^\circ C/h"},
                ],
                "grafica": {"tipo": "derivada", "Ta": float(ta), "temperatura": float(temperatura), "k": float(k), "t": horas_transcurridas},
            }
        if peticion.prueba_id == "sangre":
            a = sp.Float(str(datos["A"]), 6)
            k = sp.Float(str(datos["k"]), 6)
            t1 = sp.Float(str(datos["t1"]), 6)
            t2 = sp.Float(str(datos["t2"]), 6)
            umbral = sp.Float(str(datos.get("umbral", 25)), 6)
            if a <= 0 or k <= 0 or t1 < 0 or t2 <= t1:
                raise ValueError("A y k deben ser positivos y t2 debe ser mayor que t1.")
            t = sp.Symbol("t", positive=True)
            antiderivada = a * sp.exp(-k * t) / (-k)
            dosis = sp.integrate(a * sp.exp(-k * t), (t, t1, t2))
            letal = float(dosis) >= float(umbral)
            return {
                "resultado": f"{float(dosis):.4f}",
                "valor": float(dosis),
                "letal": letal,
                "pasos": [
                    {"titulo": "Modelo de concentración", "explicacion": "Se integra la concentración durante la ventana de exposición.", "latex": rf"C(t)={sp.latex(a)}e^{{-{sp.latex(k)}t}}"},
                    {"titulo": "Antiderivada", "explicacion": "Se obtiene la integral indefinida de la concentración.", "latex": rf"{sp.latex(antiderivada)}"},
                    {"titulo": "Integral definida", "explicacion": "Se evalúa la dosis acumulada entre t1 y t2.", "latex": rf"\int_{{{sp.latex(t1)}}}^{{{sp.latex(t2)}}}{sp.latex(a)}e^{{-{sp.latex(k)}t}}dt={float(dosis):.4f}"},
                ],
                "grafica": {"tipo": "integral", "datos": {"A": float(a), "k": float(k), "t1": float(t1), "t2": float(t2)}},
            }
        if peticion.prueba_id == "vector":
            a = [sp.Float(str(value), 6) for value in datos["A"]]
            b = [sp.Float(str(value), 6) for value in datos["B"]]
            if len(a) not in (2, 3) or len(a) != len(b):
                raise ValueError("Los puntos A y B deben tener la misma dimensión: 2D o 3D.")
            posiciones = datos["posiciones"]
            am, bm = sp.Matrix(a), sp.Matrix(b)
            d = bm - am
            rows = []
            for i, position in enumerate(posiciones, start=1):
                pm = sp.Matrix([sp.Float(str(value), 6) for value in position])
                if len(position) != len(a):
                    raise ValueError("Todas las posiciones deben tener la misma dimensión.")
                if len(a) == 2:
                    ap = pm - am
                    distance = abs(ap[0] * d[1] - ap[1] * d[0]) / d.norm()
                else:
                    distance = ((pm - am).cross(d).norm()) / d.norm()
                rows.append({"position": i, "distancia": float(distance)})
            compatible = min(rows, key=lambda row: row["distancia"])
            return {
                "resultado": compatible["position"],
                "distancias": rows,
                "pasos": [
                    {"titulo": "Dirección", "explicacion": "Se calcula el vector que une los dos impactos.", "latex": rf"d=B-A={sp.latex(d)}"},
                    {"titulo": "Distancia punto-recta", "explicacion": "Se usa el producto cruz y la norma del vector dirección.", "latex": r"d(P,r)=\frac{|(P-A)\times d|}{|d|}"},
                    {"titulo": "Posición compatible", "explicacion": "La posición con menor distancia se aproxima a la trayectoria.", "latex": f"P_{compatible['position']}"},
                ],
                "grafica": {"tipo": "vector", "datos": {"A": [float(x) for x in a], "B": [float(x) for x in b], "posiciones": posiciones}, "distancias": [row["distancia"] for row in rows]},
            }
        if peticion.prueba_id == "hill":
            matrix = sp.Matrix(datos["matriz"])
            if matrix.rows not in (2, 3) or matrix.rows != matrix.cols:
                raise ValueError("La matriz debe ser cuadrada de 2x2 o 3x3.")
            if sp.gcd(abs(int(matrix.det())), 26) != 1:
                raise ValueError("El determinante debe ser coprimo con 26.")
            cipher = re.sub(r"[^A-Z]", "", str(datos["cifrado"]).upper())
            if len(cipher) % matrix.rows:
                raise ValueError("La longitud del texto cifrado no corresponde con el tamaño de la matriz.")
            inverse = matrix.inv_mod(26)
            decrypted = []
            numbers = [ord(ch) - 65 for ch in cipher]
            for i in range(0, len(numbers), matrix.rows):
                block = sp.Matrix(numbers[i:i + matrix.rows])
                decrypted.extend((inverse * block).applyfunc(lambda value: int(value) % 26))
            text = "".join(chr(int(value) + 65) for value in decrypted).rstrip("X")
            return {
                "resultado": text,
                "pasos": [
                    {"titulo": "Determinante", "explicacion": "El determinante debe tener inverso módulo 26.", "latex": rf"\det(K)={matrix.det()}"},
                    {"titulo": "Matriz inversa modular", "explicacion": "Se calcula K^-1 módulo 26.", "latex": sp.latex(inverse)},
                    {"titulo": "Descifrado", "explicacion": "Cada bloque cifrado se multiplica por la inversa modular.", "latex": rf"\text{{Resultado: }}{text}"},
                ],
                "grafica": {"tipo": "matriz", "matriz": datos["matriz"]},
            }
        if peticion.prueba_id == "lagrange":
            a, b = float(datos["a"]), float(datos["b"])
            p, q, c = float(datos["p"]), float(datos["q"]), float(datos["c"])
            if p == 0 and q == 0:
                raise ValueError("La restricción no puede tener p y q iguales a cero.")
            x, y, lam = sp.symbols("x y lambda")
            objective = (x - a) ** 2 + (y - b) ** 2
            restriction = p * x + q * y - c
            equations = [sp.diff(objective, x) - lam * p, sp.diff(objective, y) - lam * q, restriction]
            solution = sp.solve(equations, (x, y, lam), dict=True)
            if not solution:
                raise ValueError("El sistema no tiene una solución única.")
            point = solution[0]
            px, py = float(point[x]), float(point[y])
            value = float(objective.subs({x: point[x], y: point[y]}))
            return {
                "resultado": f"({px:.2f}, {py:.2f})",
                "punto": [px, py],
                "valor": value,
                "pasos": [
                    {"titulo": "Función objetivo", "explicacion": "Se minimiza la distancia al cuadrado a la escena.", "latex": rf"(x-{a:g})^2+(y-{b:g})^2"},
                    {"titulo": "Restricción", "explicacion": "El punto debe permanecer sobre la ruta.", "latex": rf"{p:g}x+{q:g}y={c:g}"},
                    {"titulo": "Condición de Lagrange", "explicacion": "Se igualan los gradientes.", "latex": r"\nabla f=\lambda\nabla g"},
                    {"titulo": "Punto óptimo", "explicacion": "SymPy resuelve el sistema y obtiene el punto más cercano.", "latex": rf"\left({px:.2f},{py:.2f}\right)"},
                ],
                "grafica": {"tipo": "lagrange", "datos": {"a": a, "b": b, "p": p, "q": q, "c": c}, "punto": [px, py]},
            }
        raise HTTPException(status_code=400, detail="Tipo de prueba no válido.")
    except (KeyError, TypeError, ValueError, sp.SympifyError) as error:
        raise HTTPException(status_code=422, detail=str(error) or "Los datos no son válidos.")


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
