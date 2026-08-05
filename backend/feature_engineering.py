import pandas as pd
import logging
from exceptions import InvalidFeatureError

logger = logging.getLogger(__name__)

def build_features(estacion_data: pd.Series, medicion_data: pd.Series) -> dict:
    """
    Construye el vector de características exacto que requiere el contrato de IA.
    
    Contrato esperado por la IA:
    - temperatura_inst
    - temperatura_max
    - temperatura_min
    - humedad_inst
    - precipitacion_hora
    - precipitacion_dia
    - altitud
    - latitud
    - longitud
    - hora
    - mes
    """
    try:
        # Extraemos mes y hora asumiendo que 'fecha' ya es un datetime de Pandas
        fecha = medicion_data['fecha']
        mes = fecha.month
        hora = fecha.hour
        
        features = {
            "temperatura_inst": float(medicion_data['temperatura_inst']),
            "temperatura_max": float(medicion_data['temperatura_max']),
            "temperatura_min": float(medicion_data['temperatura_min']),
            "humedad_inst": float(medicion_data['humedad_inst']),
            "precipitacion_hora": float(medicion_data.get('precipitacion_hora', 0.0)),
            "precipitacion_dia": float(medicion_data.get('precipitacion_dia', 0.0)),
            "altitud": float(estacion_data['altitud']),
            "latitud": float(estacion_data['latitud']),
            "longitud": float(estacion_data['longitud']),
            "hora": int(hora),
            "mes": int(mes)
        }
        
        logger.info("Vector de características construido exitosamente.")
        return features
        
    except KeyError as e:
        logger.error(f"Falta una columna requerida para generar features: {e}")
        raise InvalidFeatureError(f"No se pudo construir el vector de features. Falta el dato: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al construir features: {e}")
        raise InvalidFeatureError(f"Error interno al procesar los datos meteorológicos: {str(e)}")
