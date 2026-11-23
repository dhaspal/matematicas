import sympy as sp
from fastapi import APIRouter, HTTPException
from models.schemas import LaboratorioRequest
from services import derivadas, integrales, vectores, matrices, lagrange
from utils.parser import parsear_expresion

router = APIRouter(prefix="/api/laboratorio", tags=["laboratorio"])


@router.post("/calcular")
def calcular(peticion: LaboratorioRequest):
    tipo = peticion.tipo
    entrada = peticion.entrada
    try:
        if tipo == "derivada":
            expresion = parsear_expresion(str(entrada["funcion"]))
            pasos, resultado = derivadas.resolver_con_pasos(expresion)
            grafica = {"tipo": "derivada", "funcion": str(expresion)}
        elif tipo in {"integral", "integral_definida"}:
            expresion = parsear_expresion(str(entrada["funcion"]))
            definida = tipo == "integral_definida"
            pasos, resultado = integrales.resolver_con_pasos(expresion, definida,
                                                              entrada.get("a", -1),
                                                              entrada.get("b", 2))
            grafica = {"tipo": "integral", "funcion": str(expresion),
                       "a": entrada.get("a", -1), "b": entrada.get("b", 2)}
        elif tipo == "vector":
            u = entrada["u"]
            v = entrada.get("v")
            resultado, pasos = vectores.calcular(entrada["operacion"], u, v)
            grafica = {"tipo": "vector", "u": u, "v": v}
        elif tipo == "matriz":
            resultado, pasos = matrices.calcular(entrada["operacion"], entrada["a"], entrada.get("b"))
            grafica = {"tipo": "matriz"}
        elif tipo == "lagrange":
            funcion = sp.sympify(entrada["funcion"])
            restriccion = sp.sympify(entrada["restriccion"])
            pasos, resultado = lagrange.resolver_con_pasos(funcion, restriccion)
            grafica = {"tipo": "lagrange", "funcion": str(funcion), "restriccion": str(restriccion)}
        else:
            raise HTTPException(status_code=400, detail="Tipo de cálculo no válido.")
        return {"resultado": sp.latex(resultado), "pasos": pasos, "grafica": grafica}
    except (ValueError, TypeError, sp.SympifyError) as error:
        mensaje = str(error) or "No pude entender la entrada."
        raise HTTPException(status_code=422, detail=mensaje)
