import uuid
import sympy as sp
from fastapi import APIRouter, HTTPException
from models.schemas import EjercicioResponse, VerificarRequest, VerificarResponse, PasoItem
from services import derivadas, integrales, vectores, matrices
from services.verificador import verificar_expresion
from utils.parser import parsear_expresion

router = APIRouter(prefix="/api/ejercicios", tags=["ejercicios"])
CACHE = {}


@router.get("/generar", response_model=EjercicioResponse)
def generar(tema: str = "derivadas", dificultad: str = "facil"):
    tema = tema.lower()
    if tema == "derivadas":
        datos = derivadas.generar(dificultad)
    elif tema == "integrales":
        datos = integrales.generar(dificultad)
    elif tema == "vectores":
        datos = vectores.generar(dificultad)
    elif tema == "matrices":
        datos = matrices.generar(dificultad)
    else:
        raise HTTPException(status_code=400, detail="Tema no válido.")
    ejercicio_id = str(uuid.uuid4())
    CACHE[ejercicio_id] = datos
    correcta = datos["respuesta"]
    if hasattr(correcta, "shape"):
        opciones_respuestas = [
            correcta,
            correcta + sp.ones(*correcta.shape),
            -correcta,
            correcta * 2,
        ]
    elif tema == "integrales":
        opciones_respuestas = [
            correcta,
            sp.diff(correcta, sp.Symbol("x")) if isinstance(correcta, sp.Basic) else correcta,
            correcta + sp.Integer(1),
            correcta - sp.Integer(1),
        ]
    else:
        opciones_respuestas = [
            correcta,
            correcta + 1,
            correcta - 1,
            correcta * 2,
        ]

    opciones_latex = [sp.latex(opcion) for opcion in opciones_respuestas]
    opciones_respuesta = {sp.latex(opcion): sp.sstr(opcion) for opcion in opciones_respuestas}
    datos["opciones"] = opciones_latex
    datos["opciones_respuesta"] = opciones_respuesta
    import random
    random.shuffle(opciones_latex)
    datos["opciones"] = opciones_latex
    tipo = "texto"
    if tema in {"vectores", "matrices"}:
        tipo = "texto"
    return EjercicioResponse(id=ejercicio_id, tema=tema, dificultad=dificultad,
                             enunciado=datos["enunciado"], tipo_respuesta=tipo, opciones=opciones_latex,
                             pista="Aplica la regla correspondiente y simplifica.")


@router.post("/verificar", response_model=VerificarResponse)
def verificar(peticion: VerificarRequest):
    datos = CACHE.get(peticion.ejercicio_id)
    if not datos:
        raise HTTPException(status_code=404, detail="El ejercicio ya no está disponible.")
    try:
        correcta = datos["respuesta"]
        respuesta_mapeada = datos.get("opciones_respuesta", {}).get(peticion.respuesta)
        respuesta_usuario = respuesta_mapeada if respuesta_mapeada is not None else peticion.respuesta
        correcta_texto = sp.sstr(correcta)
        es_integral = peticion.tema == "integrales"
        correcto = verificar_expresion(respuesta_usuario, correcta_texto, es_integral)
    except ValueError as error:
        return VerificarResponse(correcto=False, solucion_latex=sp.latex(datos["respuesta"]),
                                 retroalimentacion=str(error))
    if peticion.tema == "derivadas":
        pasos, _ = derivadas.resolver_con_pasos(datos["expresion"])
    elif peticion.tema == "integrales":
        pasos, _ = integrales.resolver_con_pasos(datos["expresion"])
    elif peticion.tema == "vectores":
        pasos = [{"titulo": "Identifica la operación", "explicacion": "Trabaja con las componentes dadas.", "latex": datos["enunciado"]},
                 {"titulo": "Resultado", "explicacion": "Esta es la solución calculada por SymPy.", "latex": sp.latex(datos["respuesta"])}]
    else:
        pasos = [{"titulo": "Resultado", "explicacion": "Esta es la solución calculada por SymPy.", "latex": sp.latex(datos["respuesta"])}]
    return VerificarResponse(
        correcto=correcto,
        solucion_latex=sp.latex(datos["respuesta"]),
        pasos=[PasoItem(**paso) for paso in pasos],
        retroalimentacion="¡Correcto! Has resuelto el ejercicio." if correcto else "No es correcto todavía. Compara con la solución y revisa los pasos.",
    )


@router.post("/paso")
def siguiente_paso(payload: dict):
    pasos = payload.get("pasos", [])
    indice = int(payload.get("indice", 0))
    if indice >= len(pasos):
        return {"completado": True}
    paso = pasos[indice]
    opciones = [
        paso["opcion_correcta"],
        paso["distractor_1"],
        paso["distractor_2"],
    ]
    import random
    random.shuffle(opciones)
    return {"completado": False, "pregunta": paso["pregunta"], "opciones": opciones,
            "respuesta": paso["opcion_correcta"], "explicacion": paso["explicacion"]}
