from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PredictRequest(BaseModel):
    estacion: str = Field(
        ..., 
        description="Nombre de la estación meteorológica", 
        json_schema_extra={"examples": ["Imata"]}
    )
    fecha: Optional[datetime] = Field(
        None, 
        description="Fecha opcional. Si no se envía, se usa la medición más reciente."
    )
    escenario: Optional[str] = Field(
        None,
        description="Modo demostración opcional: 'helada' o 'sin_helada'"
    )

class PredictResponse(BaseModel):
    estacion: str = Field(..., json_schema_extra={"examples": ["Imata"]})
    tipo: str = Field(..., description="Tipo de evento", json_schema_extra={"examples": ["HELADA"]})
    riesgo: str = Field(..., description="Nivel de riesgo", json_schema_extra={"examples": ["ALTO"]})
    probabilidad: float = Field(..., description="Probabilidad de ocurrencia", json_schema_extra={"examples": [0.93]})
    temperatura_estimada: float = Field(..., json_schema_extra={"examples": [-4.2]})
    hora_critica: str = Field(..., description="Hora estimada del evento crítico", json_schema_extra={"examples": ["04:00"]})
    factores: List[str] = Field(
        ..., 
        description="Razones de la predicción", 
        json_schema_extra={"examples": [["Temperatura mínima muy baja", "Altitud elevada"]]}
    )

class RecommendationResponse(BaseModel):
    titulo: str = Field(..., json_schema_extra={"examples": ["Acciones recomendadas"]})
    acciones: List[str] = Field(..., json_schema_extra={"examples": [["Cubrir cultivos", "Resguardar ganado", "Informar a la comunidad"]]})

class HealthResponse(BaseModel):
    status: str = Field(default="ok", json_schema_extra={"examples": ["ok"]})
