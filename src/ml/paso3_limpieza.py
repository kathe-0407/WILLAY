"""
PASO 3 - LIMPIEZA DE DATOS
===========================
Aplica las siguientes operaciones sobre el DataFrame seleccionado:

  1. Eliminar duplicados exactos.
  2. Tratar valores faltantes (NaN) con estrategia por tipo de columna.
  3. Revisar y filtrar outliers en variables meteorológicas.
  4. Confirmar que las fechas son válidas.

Entrada : DataFrame del Paso 2.
Salida  : DataFrame limpio.
"""

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────
# LÍMITES FÍSICOS RAZONABLES (Arequipa / Andes peruanos)
# ──────────────────────────────────────────────────────────────
LIMITES_FISICOS = {
    "temperatura_inst" : (-25.0,  40.0),   # °C
    "temperatura_max"  : (-25.0,  45.0),
    "temperatura_min"  : (-30.0,  40.0),
    "humedad_inst"     : (  0.0, 100.0),   # %
    "precipitacion_hora": ( 0.0, 100.0),   # mm/h
    "precipitacion_dia" : ( 0.0, 500.0),   # mm
    "velocidad_viento"  : ( 0.0,  60.0),   # m/s
    "direccion_viento"  : ( 0.0, 360.0),   # grados
}


# ──────────────────────────────────────────────────────────────
# 1. ELIMINAR DUPLICADOS
# ──────────────────────────────────────────────────────────────

def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas totalmente duplicadas y también duplicados
    (estacion_nombre, fecha) que serían errores de telemetría.
    """
    n_antes = len(df)

    # Duplicados exactos
    df = df.drop_duplicates()

    # Duplicados por clave temporal + estación
    df = df.drop_duplicates(subset=["estacion_nombre", "fecha"], keep="first")

    n_eliminados = n_antes - len(df)
    print(f"[PASO 3] Duplicados eliminados: {n_eliminados:,} ({n_eliminados/n_antes:.2%})")
    return df.reset_index(drop=True)


# ──────────────────────────────────────────────────────────────
# 2. TRATAR VALORES FALTANTES
# ──────────────────────────────────────────────────────────────

def tratar_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estrategia de imputación por tipo de variable:

    • Temperatura / Humedad / Precipitación:
        Forward-fill por estación (máximo 3 horas) y luego
        rellena con la mediana global de esa columna.

    • Variables geográficas (altitud, lat, lon):
        Son fijas por estación → se rellena con el valor
        de la misma estación en otros registros.

    • Viento (opcional): mediana global si no existe.
    """
    df = df.copy()

    # --- Informe de NaN antes ---
    nan_pct = df.isnull().mean() * 100
    cols_con_nan = nan_pct[nan_pct > 0]
    if not cols_con_nan.empty:
        print("[PASO 3] NaN (%) antes de imputación:")
        for col, pct in cols_con_nan.items():
            print(f"         {col:30s}: {pct:.2f}%")
    else:
        print("[PASO 3] Sin valores faltantes detectados.")

    # --- Forward-fill por estación (variables de serie temporal) ---
    cols_serie = [
        "temperatura_inst", "temperatura_max", "temperatura_min",
        "humedad_inst", "precipitacion_hora", "precipitacion_dia",
        "velocidad_viento", "direccion_viento",
    ]
    cols_serie = [c for c in cols_serie if c in df.columns]

    df = df.sort_values(["estacion_nombre", "fecha"])
    df[cols_serie] = (
        df.groupby("estacion_nombre", group_keys=False)[cols_serie]
        .apply(lambda g: g.ffill(limit=3))
    )

    # --- Relleno restante con mediana global ---
    for col in cols_serie:
        mediana = df[col].median()
        antes = df[col].isna().sum()
        df[col] = df[col].fillna(mediana)
        if antes:
            print(f"[PASO 3] {col}: {antes} NaN restantes → mediana ({mediana:.2f})")

    # --- Variables geográficas: propagar desde la misma estación ---
    cols_geo = ["altitud_msnm", "latitud", "longitud"]
    cols_geo = [c for c in cols_geo if c in df.columns]
    for col in cols_geo:
        df[col] = df.groupby("estacion_nombre")[col].transform(
            lambda g: g.fillna(g.median())
        )

    total_nan = df.isnull().sum().sum()
    print(f"[PASO 3] NaN totales después de imputación: {total_nan}")
    return df


# ──────────────────────────────────────────────────────────────
# 3. REVISAR OUTLIERS
# ──────────────────────────────────────────────────────────────

def filtrar_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica los límites físicos definidos en LIMITES_FISICOS.
    Valores fuera de rango se reemplazan por NaN y luego se
    imputan con la mediana de la columna.

    Esta función NO elimina filas: solo corrige valores imposibles.
    """
    df = df.copy()
    total_corregidos = 0

    for col, (minimo, maximo) in LIMITES_FISICOS.items():
        if col not in df.columns:
            continue
        mascara = (df[col] < minimo) | (df[col] > maximo)
        n = mascara.sum()
        if n > 0:
            mediana = df[col].median()
            df.loc[mascara, col] = np.nan
            df[col] = df[col].fillna(mediana)
            print(
                f"[PASO 3] Outliers en '{col}': {n} valores fuera de "
                f"[{minimo}, {maximo}] → reemplazados con mediana ({mediana:.2f})"
            )
            total_corregidos += n

    print(f"[PASO 3] Total outliers corregidos: {total_corregidos:,}")
    return df


# ──────────────────────────────────────────────────────────────
# 4. CONFIRMAR FECHAS VÁLIDAS
# ──────────────────────────────────────────────────────────────

def validar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas donde 'fecha' no pudo parsearse."""
    n_antes = len(df)
    df = df.dropna(subset=["fecha"])
    n_eliminadas = n_antes - len(df)
    if n_eliminadas:
        print(f"[PASO 3] Filas con fecha inválida eliminadas: {n_eliminadas}")
    else:
        print("[PASO 3] Todas las fechas son válidas.")
    return df


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 3
# ──────────────────────────────────────────────────────────────

def run(df_paso2: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el Paso 3 completo."""
    print("\n" + "=" * 60)
    print("  PASO 3: LIMPIEZA DE DATOS")
    print("=" * 60)

    df = validar_fechas(df_paso2)
    df = eliminar_duplicados(df)
    df = filtrar_outliers(df)
    df = tratar_faltantes(df)

    print(f"\n[PASO 3] Shape final limpio: {df.shape}")
    print("[PASO 3] ✅ Listo.\n")
    return df


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2

    df_unido = p1.run()
    df_sel   = p2.run(df_unido)
    df_limpio = run(df_sel)
    print(df_limpio.describe())
