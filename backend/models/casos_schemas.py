from typing import Optional
from pydantic import BaseModel, Field


class VerificarPruebaRequest(BaseModel):
    seed: str
    dificultad: str = Field(pattern="^(facil|medio|dificil)$")
    prueba_id: str = Field(min_length=1, max_length=40)
    respuesta: str = Field(max_length=500)


class AcusarRequest(BaseModel):
    seed: str
    dificultad: str = Field(pattern="^(facil|medio|dificil)$")
    sospechoso_id: str = Field(min_length=1, max_length=40)


class CalcularPruebaRequest(BaseModel):
    prueba_id: str = Field(pattern="^(hora|sangre|vector|hill|lagrange)$")
    datos: dict
