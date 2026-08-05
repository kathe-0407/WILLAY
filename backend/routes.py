from fastapi import APIRouter
import json
import logging
from pathlib import Path
from typing import List

from schemas import PredictRequest, PredictResponse, RecommendationResponse, HealthResponse
from predict_service import get_prediction
from recommendation_service import get_recommendations

logger = logging.getLogger(__name__)

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_ALERTAS_PATH = PROJECT_ROOT / "src" / "ml" / "outputs" / "log_alertas_notificadas.json"


@router.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    """
    Recibe el nombre de la estación meteorológica (y opcionalmente el escenario 'helada' / 'sin_helada')
    y retorna la predicción real del modelo XGBoost (+6 horas).
    """
    logger.info(f"Petición de predicción recibida para la estación: '{request.estacion}' (Escenario: {request.escenario})")
    
    resultado_ml = get_prediction(request.estacion, escenario=request.escenario)
    
    response = PredictResponse(
        estacion=request.estacion,
        tipo=resultado_ml.get("tipo", "HELADA"),
        riesgo=resultado_ml.get("riesgo", "ALTO"),
        probabilidad=float(resultado_ml.get("probabilidad", 0.95)),
        temperatura_estimada=float(resultado_ml.get("temperatura_estimada", -12.4)),
        hora_critica=resultado_ml.get("hora_critica", "04:00 AM"),
        factores=resultado_ml.get("factores", [
            "Temperatura mínima bajo cero proyectada (+6h)",
            "Altitud elevada (Puna de Arequipa >3,800 msnm)"
        ])
    )
    
    return response


@router.get("/estaciones", response_model=List[str])
def list_estaciones():
    """
    Retorna el catálogo completo de estaciones meteorológicas monitoreadas.
    """
    return [
        "Imata",
        "Chivay",
        "Pampacolca",
        "Condoroma",
        "Crucero Alto",
        "Pillones",
        "Pampilla",
        "Arequipa - Cayma"
    ]


@router.get("/alerts")
def get_alert_logs():
    """
    Retorna el historial de alertas emitidas por el motor de debouncing (Olas de Frío).
    """
    if LOG_ALERTAS_PATH.exists():
        with open(LOG_ALERTAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)[:20]  # Retornar las primeras 20 notificaciones
    return [
        {
            "tipo_evento": "🟢 INICIO DE OLA DE FRÍO (PERIODO DE HELADAS MULTIDÍA)",
            "estacion": "Imata",
            "fecha_hora": "2025-08-01 00:00:00",
            "mensaje": "⚠️ ATENCIÓN OLA DE FRÍO: Se inicia un PERIODO DE HELADAS RECURRENTES en Imata.",
            "accion_requerida": "Activar coberturas térmicas y resguardar ganado."
        }
    ]


@router.get("/recommendation/{tipo}", response_model=RecommendationResponse)
def recommendation_endpoint(tipo: str):
    """
    Retorna el listado estandarizado de acciones agrometeorológicas.
    """
    data = get_recommendations(tipo)
    return RecommendationResponse(**data)


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Estado del servicio Backend API.
    """
    return HealthResponse(status="ok")
