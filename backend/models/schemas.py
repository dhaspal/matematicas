from typing import Any, Optional
from pydantic import BaseModel


class EjercicioResponse(BaseModel):
    id: str
    tema: str
    dificultad: str
    enunciado: str
    tipo_respuesta: str
    opciones: list[str] = []
    pista: str


class VerificarRequest(BaseModel):
    ejercicio_id: str
    tema: str
    respuesta: str
    dificultad: str = "facil"


class PasoItem(BaseModel):
    titulo: str
    explicacion: str
    latex: str
    regla: Optional[str] = None


class VerificarResponse(BaseModel):
    correcto: bool
    solucion_latex: str
    pasos: list[PasoItem] = []
    retroalimentacion: str


class LaboratorioRequest(BaseModel):
    tipo: str
    entrada: dict[str, Any]
