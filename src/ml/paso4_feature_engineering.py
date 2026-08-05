"""
PASO 4 - FEATURE ENGINEERING
==============================
Genera nuevas variables predictoras a partir del DataFrame limpio.

Nuevas features:
  • temperatura_media      = (temp_max + temp_min) / 2
  • amplitud_termica       = temp_max - temp_min
  • cambio_temp_6h         = temp_inst(t) - temp_inst(t-6h)  por estación
  • cambio_humedad_6h      = humedad(t) - humedad(t-6h)       por estación
  • cambio_viento_6h       = velocidad_viento(t) - velocidad_viento(t-6h)
  • es_madrugada           = 1 si hora ∈ {2,3,4,5,6} else 0
  • temp_inst_lag1h        = temperatura_inst de la hora anterior
  • temp_inst_lag3h        = temperatura_inst de 3 horas antes
  • humedad_rolling_3h     = media móvil de humedad últimas 3 horas
  • precip_acumulada_6h    = suma precipitación últimas 6 horas
  • altitud_normalizada    = altitud_msnm / 5000  (escala 0-1 aprox.)

Entrada : DataFrame limpio del Paso 3.
Salida  : DataFrame enriquecido.
"""

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _shift_por_estacion(df: pd.DataFrame, col: str, periodos: int) -> pd.Series:
    """
    Calcula el lag 'periodos' horas atrás para 'col',
    agrupando por estación para no mezclar series.
    """
    return (
        df.groupby("estacion_nombre", group_keys=False)[col]
        .shift(periodos)
    )


def _rolling_por_estacion(
    df: pd.DataFrame, col: str, ventana: int, agg: str = "mean"
) -> pd.Series:
    """Rolling (media o suma) por estación, ventana en horas."""
    grouped = df.groupby("estacion_nombre", group_keys=False)[col]
    if agg == "mean":
        return grouped.transform(
            lambda g: g.rolling(ventana, min_periods=1).mean()
        )
    elif agg == "sum":
        return grouped.transform(
            lambda g: g.rolling(ventana, min_periods=1).sum()
        )
    raise ValueError(f"agg debe ser 'mean' o 'sum', recibido: {agg}")


# ──────────────────────────────────────────────────────────────
# FEATURES BÁSICOS
# ──────────────────────────────────────────────────────────────

def agregar_punto_rocio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el punto de rocío aproximado (Magnus-Tetens) y la depresión del punto de rocío.
    punto_rocio = T - (100 - HR) / 5
    delta_t_rocio = T - punto_rocio
    """
    df = df.copy()
    if "temperatura_inst" in df.columns and "humedad_inst" in df.columns:
        df["punto_rocio"] = df["temperatura_inst"] - ((100.0 - df["humedad_inst"]) / 5.0)
        df["delta_t_rocio"] = df["temperatura_inst"] - df["punto_rocio"]
        print("[PASO 4] ✔ punto_rocio, delta_t_rocio")
    return df


def agregar_es_madrugada(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bandera binaria: las heladas ocurren mayoritariamente entre 2 y 6 AM.
    """
    df = df.copy()
    df["es_madrugada"] = df["hora"].isin([2, 3, 4, 5, 6]).astype("int8")
    print("[PASO 4] ✔ es_madrugada")
    return df


# ──────────────────────────────────────────────────────────────
# FEATURES DE CAMBIO (DIFERENCIAS TEMPORALES)
# ──────────────────────────────────────────────────────────────

def agregar_cambios_temporales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula cambios respecto a 6 horas atrás para:
      - temperatura_inst
      - humedad_inst
      - velocidad_viento (si existe)
    """
    df = df.copy()
    df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)

    if "temperatura_inst" in df.columns:
        lag6 = _shift_por_estacion(df, "temperatura_inst", 6)
        df["cambio_temp_6h"] = df["temperatura_inst"] - lag6
        print("[PASO 4] ✔ cambio_temp_6h")

    if "humedad_inst" in df.columns:
        lag6 = _shift_por_estacion(df, "humedad_inst", 6)
        df["cambio_humedad_6h"] = df["humedad_inst"] - lag6
        print("[PASO 4] ✔ cambio_humedad_6h")

    if "velocidad_viento" in df.columns:
        lag6 = _shift_por_estacion(df, "velocidad_viento", 6)
        df["cambio_viento_6h"] = df["velocidad_viento"] - lag6
        print("[PASO 4] ✔ cambio_viento_6h")

    return df


# ──────────────────────────────────────────────────────────────
# FEATURES DE LAG
# ──────────────────────────────────────────────────────────────

def agregar_lags_temperatura(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lags de temperatura instantánea para capturar tendencia horaria.
    """
    df = df.copy()
    df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)

    if "temperatura_inst" in df.columns:
        df["temp_inst_lag1h"] = _shift_por_estacion(df, "temperatura_inst", 1)
        df["temp_inst_lag3h"] = _shift_por_estacion(df, "temperatura_inst", 3)
        print("[PASO 4] ✔ temp_inst_lag1h, temp_inst_lag3h")

    return df


def agregar_duracion_congelamiento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la duración del congelamiento en las últimas 12 horas:
      • horas_bajo_cero            : cantidad de horas con T < 0°C en las últimas 12h.
      • grado_horas_congelamiento  : acumulación térmica congelante sum(max(0, -T)) en 12h.
                                    Representa la dosis de daño por exposición prolongada al frío.
    """
    df = df.copy()
    df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)

    if "temperatura_inst" in df.columns:
        es_subzero = (df["temperatura_inst"] < 0.0).astype(float)
        dosis_fria = np.maximum(0.0, -df["temperatura_inst"])

        grouped_subzero = df.groupby("estacion_nombre", group_keys=False)
        df["horas_bajo_cero"] = (
            grouped_subzero["temperatura_inst"]
            .transform(lambda g: (g < 0.0).astype(float).rolling(12, min_periods=1).sum())
            .astype("float32")
        )

        df["grado_horas_congelamiento"] = (
            grouped_subzero["temperatura_inst"]
            .transform(lambda g: np.maximum(0.0, -g).rolling(12, min_periods=1).sum())
            .astype("float32")
        )
        print("[PASO 4] ✔ horas_bajo_cero, grado_horas_congelamiento")

    return df


def agregar_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Media móvil de humedad (3h) y suma de precipitación (6h).
    """
    df = df.copy()
    df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)

    if "humedad_inst" in df.columns:
        df["humedad_rolling_3h"] = _rolling_por_estacion(df, "humedad_inst", 3, "mean")
        print("[PASO 4] ✔ humedad_rolling_3h")

    if "precipitacion_hora" in df.columns:
        df["precip_acumulada_6h"] = _rolling_por_estacion(df, "precipitacion_hora", 6, "sum")
        print("[PASO 4] ✔ precip_acumulada_6h")

    return df


# ──────────────────────────────────────────────────────────────
# NORMALIZACIÓN GEOGRÁFICA
# ──────────────────────────────────────────────────────────────

def agregar_altitud_normalizada(df: pd.DataFrame) -> pd.DataFrame:
    """
    altitud_normalizada: escala [0, 1] aproximada (÷ 5000 msnm).
    Facilita la comparación entre estaciones de distinta altitud.
    """
    df = df.copy()
    if "altitud_msnm" in df.columns:
        df["altitud_normalizada"] = (df["altitud_msnm"] / 5000.0).astype("float32")
        print("[PASO 4] ✔ altitud_normalizada")
    return df


# ──────────────────────────────────────────────────────────────
# ANOMALÍA CLIMÁTICA (temperatura relativa a la "normal" local)
# ──────────────────────────────────────────────────────────────

def agregar_anomalia_climatica(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la climatología local (temperatura normal para esa estación,
    mes y hora) y la anomalía respecto a ella.

    En la sierra sur del Perú hay estaciones como Imata (4,519 msnm)
    donde -5°C a las 5 AM en julio es NORMAL.  La helada peligrosa
    ocurre cuando la temperatura baja POR DEBAJO de lo esperado.

    Nuevas features:
      • temp_normal       : media climatológica de temperatura_inst
                            para esa (estación, mes, hora).
      • anomalia_termica  : temp_inst – temp_normal.
                            Valores muy negativos = frío anómalo.
      • anomalia_severa   : flag binario → 1 si anomalia < -3°C.
      • temp_min_normal   : media climatológica de temperatura_min
                            para esa (estación, mes, hora).
      • anomalia_temp_min : temp_min – temp_min_normal.
    """
    df = df.copy()

    if "temperatura_inst" not in df.columns or "hora" not in df.columns:
        return df

    # ── Climatología de temperatura instantánea ──
    clima_inst = (
        df.groupby(["estacion_nombre", "mes", "hora"])["temperatura_inst"]
        .transform("mean")
    )
    df["temp_normal"]      = clima_inst.astype("float32")
    df["anomalia_termica"] = (df["temperatura_inst"] - df["temp_normal"]).astype("float32")
    df["anomalia_severa"]  = (df["anomalia_termica"] < -3.0).astype("int8")

    # ── Climatología de temperatura mínima ──
    if "temperatura_min" in df.columns:
        clima_min = (
            df.groupby(["estacion_nombre", "mes", "hora"])["temperatura_min"]
            .transform("mean")
        )
        df["temp_min_normal"]   = clima_min.astype("float32")
        df["anomalia_temp_min"] = (df["temperatura_min"] - df["temp_min_normal"]).astype("float32")

    n_severas = df["anomalia_severa"].sum()
    print(f"[PASO 4] ✔ temp_normal, anomalia_termica, anomalia_severa ({n_severas:,} horas anómalas)")
    if "anomalia_temp_min" in df.columns:
        print("[PASO 4] ✔ temp_min_normal, anomalia_temp_min")

    return df


# ──────────────────────────────────────────────────────────────
# TASA DE ENFRIAMIENTO NOCTURNO
# ──────────────────────────────────────────────────────────────

def agregar_tasa_enfriamiento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la velocidad a la que baja la temperatura por hora.

      tasa_enfriamiento = temp_inst(t) – temp_inst(t-1)  por estación

    Un valor muy negativo indica un descenso rápido (ej. -2.5°C/h),
    que es señal de helada radiativa en formación.
    """
    df = df.copy()
    if "temperatura_inst" in df.columns:
        df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)
        df["tasa_enfriamiento"] = (
            df["temperatura_inst"]
            - _shift_por_estacion(df, "temperatura_inst", 1)
        ).astype("float32")
        print("[PASO 4] ✔ tasa_enfriamiento")
    return df


# ──────────────────────────────────────────────────────────────
# RELLENO DE NaN GENERADOS POR LAGS / ROLLING
# ──────────────────────────────────────────────────────────────

def rellenar_nan_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Los primeros N registros por estación tendrán NaN en lags/rolling.
    Se rellenan con 0 (cambio = 0, lag = propio valor).
    """
    df = df.copy()
    cols_engineered = [
        "cambio_temp_6h", "cambio_humedad_6h", "cambio_viento_6h",
        "temp_inst_lag1h", "temp_inst_lag3h",
        "humedad_rolling_3h", "precip_acumulada_6h",
        "tasa_enfriamiento", "horas_bajo_cero", "grado_horas_congelamiento",
    ]
    for col in cols_engineered:
        if col in df.columns and df[col].isna().any():
            # Para lags de temperatura usamos la propia temperatura como fallback
            if "lag" in col and "temperatura_inst" in df.columns:
                df[col] = df[col].fillna(df["temperatura_inst"])
            else:
                df[col] = df[col].fillna(0.0)

    return df


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 4
# ──────────────────────────────────────────────────────────────

def run(df_limpio: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el Paso 4 completo."""
    print("\n" + "=" * 60)
    print("  PASO 4: FEATURE ENGINEERING")
    print("=" * 60)

    df = agregar_punto_rocio(df_limpio)
    df = agregar_es_madrugada(df)
    df = agregar_cambios_temporales(df)
    df = agregar_lags_temperatura(df)
    df = agregar_duracion_congelamiento(df)
    df = agregar_rolling_features(df)
    df = agregar_altitud_normalizada(df)
    df = agregar_anomalia_climatica(df)
    df = agregar_tasa_enfriamiento(df)
    df = rellenar_nan_features(df)

    nuevas = [
        c for c in df.columns
        if c not in df_limpio.columns
    ]
    print(f"\n[PASO 4] Nuevas features creadas ({len(nuevas)}): {nuevas}")
    print(f"[PASO 4] Shape final: {df.shape}")
    print("[PASO 4] ✅ Listo.\n")
    return df


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = run(df)
    print(df[["estacion_nombre", "fecha", "temperatura_inst",
              "anomalia_termica", "tasa_enfriamiento", "punto_rocio"]].head(10))
