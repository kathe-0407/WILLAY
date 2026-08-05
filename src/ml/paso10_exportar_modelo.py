"""
PASO 10 - EXPORTAR MODELO
==========================
Serializa el modelo entrenado y los artefactos necesarios para
que el backend pueda hacer predicciones en producción.

Archivos exportados (en outputs/modelo/):
  • modelo_heladas.json      → modelo XGBoost nativo (portátil, rápido)
  • features.json            → lista de features en el orden correcto
  • umbrales_target.json     → umbrales usados para construir el target
  • metadata.json            → métricas de evaluación y fecha de entrenamiento

Función de predicción de producción:
  predecir(datos: dict) → {"nivel_riesgo": int, "probabilidad": float, "etiqueta": str}
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

from xgboost import XGBClassifier


OUTPUT_DIR = Path(__file__).parent / "outputs"
MODELO_DIR = OUTPUT_DIR / "modelo"
MODELO_DIR.mkdir(parents=True, exist_ok=True)

ETIQUETAS = {
    0: "Sin riesgo",
    1: "Bajo",
    2: "Moderado",
    3: "Alto",
    4: "Crítico",
}

RECOMENDACIONES = {
    0: "No se requieren acciones. Condiciones normales.",
    1: "Monitorear la temperatura mínima. Riesgo leve de helada.",
    2: "Alertar a productores agrícolas. Proteger cultivos sensibles.",
    3: "Activar protocolo de helada. Proteger ganado y cultivos.",
    4: "ALERTA CRÍTICA: Helada severa inminente. Evacuar ganado y activar todas las medidas de protección.",
}

UMBRALES_TARGET = {
    "descripcion": "Índice de Riesgo Agrometeorológico Multifactorial (Intensidad + Duración + Humedad + Anomalía)",
    "matriz_evaluacion": {
        "intensidad_termica": "Temp <= 5°C (Base), <= 0°C (+1), <= -3°C (+2), <= -6°C (+3)",
        "duracion_exposicion": ">= 3h bajo cero (+1), >= 6h bajo cero (+2)",
        "humedad_escarcha": "Humedad >= 80% con Temp <= 0°C (+1)",
        "anomalia_climatica": "Desviación <= -4.0°C respecto a la normal climatológica (+1)"
    },
    "escala_riesgo": {
        "0": "Sin riesgo (>5°C sin anomalía)",
        "1": "Vigilancia / Descenso de temperatura",
        "2": "Helada Ligera (Escarcha o congelamiento corto)",
        "3": "Helada Moderada (Exposición prolongada o temp < -3.0°C)",
        "4": "Helada Severa / Crítica (Exposición >6h, temp <= -6.0°C o anomalía severa)"
    }
}


# ──────────────────────────────────────────────────────────────
# EXPORTAR MODELO
# ──────────────────────────────────────────────────────────────

def exportar_modelo(
    model: XGBClassifier,
    feature_names: list[str],
    metricas: dict,
) -> dict[str, Path]:
    """
    Exporta todos los artefactos necesarios para producción.

    Returns
    -------
    dict con rutas de cada artefacto generado.
    """
    rutas = {}

    # 1. Modelo en formato JSON nativo de XGBoost
    path_modelo = MODELO_DIR / "modelo_heladas.json"
    model.save_model(str(path_modelo))
    print(f"[PASO 10] 💾 Modelo exportado : {path_modelo}")
    rutas["modelo"] = path_modelo

    # 2. Lista de features (orden importa para predicción)
    path_features = MODELO_DIR / "features.json"
    with open(path_features, "w", encoding="utf-8") as f:
        json.dump({"features": feature_names}, f, indent=2, ensure_ascii=False)
    print(f"[PASO 10] 💾 Features exportadas: {path_features}")
    rutas["features"] = path_features

    # 3. Umbrales del target
    path_umbrales = MODELO_DIR / "umbrales_target.json"
    with open(path_umbrales, "w", encoding="utf-8") as f:
        json.dump(UMBRALES_TARGET, f, indent=2, ensure_ascii=False)
    print(f"[PASO 10] 💾 Umbrales exportados: {path_umbrales}")
    rutas["umbrales"] = path_umbrales

    # 4. Metadata (métricas + fecha de entrenamiento)
    metadata = {
        "modelo"           : "XGBClassifier",
        "objetivo"         : "multi:softprob",
        "num_clases"       : 5,
        "clases"           : ETIQUETAS,
        "fecha_entrenamiento": datetime.now(timezone.utc).isoformat(),
        "metricas_test"    : {k: round(float(v), 4) for k, v in metricas.items()},
        "n_features"       : len(feature_names),
        "features"         : feature_names,
        "n_estimators_usados": int(model.best_iteration) + 1 if model.best_iteration else model.n_estimators,
    }
    path_meta = MODELO_DIR / "metadata.json"
    with open(path_meta, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"[PASO 10] 💾 Metadata exportada  : {path_meta}")
    rutas["metadata"] = path_meta

    return rutas


# ──────────────────────────────────────────────────────────────
# FUNCIÓN DE PREDICCIÓN EN PRODUCCIÓN
# ──────────────────────────────────────────────────────────────

def cargar_modelo(modelo_dir: Path = MODELO_DIR) -> tuple[XGBClassifier, list[str]]:
    """
    Carga el modelo y la lista de features desde disco.
    Para uso en el backend o en scripts de inferencia.
    """
    model = XGBClassifier()
    model.load_model(str(modelo_dir / "modelo_heladas.json"))

    with open(modelo_dir / "features.json", encoding="utf-8") as f:
        features = json.load(f)["features"]

    return model, features


def predecir(
    datos: dict,
    model: XGBClassifier | None = None,
    features: list[str] | None = None,
) -> dict:
    """
    Predice el nivel de riesgo de helada para un registro nuevo.

    Parameters
    ----------
    datos   : dict con los valores de cada feature.
              Ejemplo:
              {
                "temperatura_inst": -1.5,
                "humedad_inst": 82.0,
                "altitud_msnm": 4519,
                "hora": 4,
                ...
              }
    model   : Modelo cargado (si None, se carga desde disco).
    features: Lista de features (si None, se carga desde disco).

    Returns
    -------
    {
        "nivel_riesgo"  : 4,
        "probabilidad"  : 0.93,
        "etiqueta"      : "Crítico",
        "recomendacion" : "⚠️ ALERTA CRÍTICA: ...",
        "probabilidades": {0: 0.01, 1: 0.02, 2: 0.02, 3: 0.02, 4: 0.93}
    }
    """
    if model is None or features is None:
        model, features = cargar_modelo()

    # Construir el DataFrame de entrada con el orden correcto
    fila = {feat: datos.get(feat, 0.0) for feat in features}
    X_pred = pd.DataFrame([fila])

    # Predicción de probabilidades
    probs = model.predict_proba(X_pred)[0]
    n_clases = len(probs)
    nivel = int(np.argmax(probs))
    prob_max = float(probs[nivel])

    if n_clases <= 2:
        etiquetas_map = {0: "Sin Helada", 1: "Alerta de Helada"}
        recom_map = {
            0: "No se requieren acciones. Condiciones normales.",
            1: "⚠️ ALERTA ACTIVADA: Alta probabilidad de helada agrometeorológica en las próximas 6h.",
        }
    else:
        etiquetas_map = ETIQUETAS
        recom_map = RECOMENDACIONES

    return {
        "nivel_riesgo"   : nivel,
        "probabilidad"   : round(prob_max, 4),
        "etiqueta"       : etiquetas_map.get(nivel, f"Clase {nivel}"),
        "recomendacion"  : recom_map.get(nivel, "Seguir protocolos estandarizados."),
        "probabilidades" : {
            int(i): round(float(p), 4)
            for i, p in enumerate(probs)
        },
    }


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 10
# ──────────────────────────────────────────────────────────────

def run(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    metricas: dict,
) -> dict[str, Path]:
    """Ejecuta el Paso 10 completo."""
    print("\n" + "=" * 60)
    print("  PASO 10: EXPORTAR MODELO")
    print("=" * 60)

    feature_names = X_test.columns.tolist()
    rutas = exportar_modelo(model, feature_names, metricas)

    # Demo: predicción de ejemplo con el modelo recién exportado
    print("\n[PASO 10] 🔍 Demo de predicción (cargando modelo desde disco):")
    ejemplo = {feat: float(X_test[feat].iloc[0]) for feat in feature_names}
    resultado = predecir(ejemplo)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    print(f"\n[PASO 10] Artefactos exportados en: {MODELO_DIR}")
    print("[PASO 10] ✅ Listo. Pipeline completo.\n")
    return rutas


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4
    import paso5_construir_target as p5
    import paso6_dividir_datos as p6
    import paso7_entrenar as p7
    import paso8_evaluar as p8

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = p5.run(df)
    X_train, X_test, y_train, y_test = p6.run(df)
    model = p7.run(X_train, X_test, y_train, y_test)
    metricas = p8.run(model, X_test, y_test)
    rutas = run(model, X_test, metricas)
