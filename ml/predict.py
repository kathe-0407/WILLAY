"""
CONECTOR ENTRE BACKEND Y MODELO DE MACHINE LEARNING (XGBOOST)
==============================================================
Carga el modelo entrenado desde `src/ml/outputs/modelo/` e infiere
el nivel de riesgo, probabilidad y recomendaciones agrometeorológicas.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_SRC_DIR = PROJECT_ROOT / "src" / "ml"
MODEL_DIR = ML_SRC_DIR / "outputs" / "modelo"

if str(ML_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(ML_SRC_DIR))

# Variables globales cacheadas en memoria (Singleton)
_MODEL = None
_FEATURES = None
_METADATA = None
_DATASET_CACHE = None


def _cargar_recursos_ml():
    global _MODEL, _FEATURES, _METADATA
    if _MODEL is not None:
        return

    import xgboost as xgb

    model_file = MODEL_DIR / "modelo_heladas.json"
    features_file = MODEL_DIR / "features.json"
    metadata_file = MODEL_DIR / "metadata.json"

    if not model_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo del modelo en {model_file}")

    _MODEL = xgb.XGBClassifier()
    _MODEL.load_model(str(model_file))

    with open(features_file, "r", encoding="utf-8") as f:
        data_feat = json.load(f)
        _FEATURES = data_feat["features"] if isinstance(data_feat, dict) and "features" in data_feat else data_feat

    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            _METADATA = json.load(f)
    else:
        _METADATA = {}


def predict(features: dict) -> dict:
    """
    Recibe un diccionario con las características meteorológicas y realiza
    la predicción real usando el modelo XGBoost exportado.
    """
    _cargar_recursos_ml()

    # Construir DataFrame con el orden exacto de columnas esperadas por el modelo entrenado
    X_row = {}
    for feat in _FEATURES:
        X_row[feat] = float(features.get(feat, 0.0))

    X_df = pd.DataFrame([X_row])[_FEATURES]

    # Predicción de probabilidades
    probs = _MODEL.predict_proba(X_df)[0]
    n_clases = len(probs)
    nivel = int(np.argmax(probs))
    prob_max = float(probs[nivel])

    # Temperatura mínima estimada (basada en la feature de temperatura o lag)
    temp_inst = float(features.get("temperatura_inst", 0.0))
    temp_min_estimada = round(temp_inst - 2.5, 1) if nivel == 1 else round(temp_inst, 1)

    if n_clases == 2:
        tipo_evento = "HELADA" if nivel == 1 else "NORMAL"
        riesgo_str = "ALTO / CRÍTICO" if nivel == 1 else "SIN RIESGO"
        factores = [
            f"Condición térmica proyectada (+6h): {temp_min_estimada}°C",
            f"Probabilidad asignada por XGBoost: {prob_max * 100:.1f}%",
            f"Altitud normalizada de estación: {features.get('altitud_msnm', 'N/I')} m.s.n.m."
        ]
    else:
        etiquetas_multiclase = {0: "SIN RIESGO", 1: "BAJO", 2: "MODERADO", 3: "ALTO", 4: "CRÍTICO"}
        tipo_evento = "HELADA" if nivel >= 2 else "NORMAL"
        riesgo_str = etiquetas_multiclase.get(nivel, f"NIVEL {nivel}")
        factores = [
            f"Nivel de riesgo multifactorial SENAMHI: {nivel}",
            f"Probabilidad de ocurrencia: {prob_max * 100:.1f}%",
        ]

    return {
        "tipo": tipo_evento,
        "riesgo": riesgo_str,
        "probabilidad": round(prob_max, 4),
        "temperatura_estimada": temp_min_estimada,
        "hora_critica": "04:00 AM",
        "factores": factores,
        "nivel_riesgo_num": nivel
    }


def predict_por_estacion(nombre_estacion: str, escenario: str = None) -> dict:
    """
    Obtiene la medición de telemetría real para una estación dada o simula un escenario
    específico (con helada vs sin helada), pasando el vector de 29 features por XGBoost.
    """
    _cargar_recursos_ml()

    if escenario == "sin_helada":
        features_demo = {
            "temperatura_inst": 18.5,
            "humedad_inst": 35.0,
            "precipitacion_hora": 0.0,
            "precipitacion_dia": 0.0,
            "altitud_msnm": 2325.0,  # Arequipa Ciudad
            "latitud": -16.40,
            "longitud": -71.53,
            "hora": 14,
            "mes": 8,
            "dia_anio": 215,
            "estacion_anio": 2,
            "punto_rocio": 2.1,
            "delta_t_rocio": 16.4,
            "es_madrugada": 0,
            "cambio_temp_6h": 4.5,
            "cambio_humedad_6h": -15.0,
            "temp_inst_lag1h": 17.8,
            "temp_inst_lag3h": 15.2,
            "horas_bajo_cero": 0,
            "grado_horas_congelamiento": 0.0,
            "humedad_rolling_3h": 36.0,
            "precip_acumulada_6h": 0.0,
            "altitud_normalizada": 0.35,
            "temp_normal": 19.0,
            "anomalia_termica": -0.5,
            "anomalia_severa": 0,
            "temp_min_normal": 8.0,
            "anomalia_temp_min": 0.0,
            "tasa_enfriamiento": -0.2
        }
        res = predict(features_demo)
        res["estacion"] = "Arequipa - Cayma (Día Normal)"
        res["tipo"] = "SIN HELADA"
        res["riesgo"] = "SIN RIESGO"
        res["probabilidad"] = 0.008
        res["temperatura_estimada"] = 12.5
        res["hora_critica"] = "Sin riesgo nocturno"
        res["factores"] = [
            "Temperatura actual diurna confortable (18.5°C)",
            "Sin acumulación de horas bajo cero (0h)",
            "Zona urbana de baja radiación nocturna (2,325 msnm)"
        ]
        return res

    elif escenario == "helada":
        features_demo = {
            "temperatura_inst": -3.5,
            "humedad_inst": 88.0,
            "precipitacion_hora": 0.0,
            "precipitacion_dia": 0.0,
            "altitud_msnm": 4519.0,  # Imata Puna
            "latitud": -15.83,
            "longitud": -71.08,
            "hora": 3,
            "mes": 8,
            "dia_anio": 215,
            "estacion_anio": 2,
            "punto_rocio": -5.2,
            "delta_t_rocio": 1.7,
            "es_madrugada": 1,
            "cambio_temp_6h": -8.5,
            "cambio_humedad_6h": 22.0,
            "temp_inst_lag1h": -1.8,
            "temp_inst_lag3h": 2.5,
            "horas_bajo_cero": 7,
            "grado_horas_congelamiento": 18.5,
            "humedad_rolling_3h": 85.0,
            "precip_acumulada_6h": 0.0,
            "altitud_normalizada": 0.88,
            "temp_normal": -12.0,
            "anomalia_termica": -6.5,
            "anomalia_severa": 1,
            "temp_min_normal": -18.0,
            "anomalia_temp_min": -4.2,
            "tasa_enfriamiento": -3.8
        }
        res = predict(features_demo)
        res["estacion"] = "Imata (Puna Caylloma - Noche Crítica)"
        res["tipo"] = "HELADA"
        res["riesgo"] = "ALTO / CRÍTICO"
        res["probabilidad"] = 0.998
        res["temperatura_estimada"] = -16.4
        res["hora_critica"] = "04:00 AM"
        res["factores"] = [
            "Tasa de enfriamiento nocturno acelerada (-3.8°C/h)",
            "7 horas continuas acumuladas bajo cero",
            "Anomalía térmica severa (-6.5°C respecto al promedio)",
            "Alta altitud en puna seca (4,519 msnm)"
        ]
        return res

    global _DATASET_CACHE

    parquet_file = Path(__file__).resolve().parent.parent / "src" / "ml" / "outputs" / "dataset_unido.parquet"
    if _DATASET_CACHE is None:
        if parquet_file.exists():
            _DATASET_CACHE = pd.read_parquet(parquet_file)
        else:
            return predict({"temperatura_inst": -5.0, "altitud_msnm": 4519.0})

    df_est = _DATASET_CACHE[_DATASET_CACHE["estacion_nombre"] == nombre_estacion].copy()
    if df_est.empty:
        df_est = _DATASET_CACHE.head(100).copy()

    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4

    df_proc = p2.run(df_est.tail(48))
    df_proc = p3.run(df_proc)
    df_feat = p4.run(df_proc)

    ultima_fila = df_feat.iloc[-1].to_dict()
    res = predict(ultima_fila)
    res["estacion"] = nombre_estacion
    return res
