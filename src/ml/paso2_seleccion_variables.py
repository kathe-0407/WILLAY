"""
PASO 2 - SELECCIÓN DE VARIABLES
================================
A partir del DataFrame unido selecciona únicamente las variables
relevantes para el modelo:

  • Meteorológicas : temperatura (inst/max/min), humedad,
                    precipitación hora/día, velocidad y dirección
                    del viento (si existen en el CSV).
  • Geográficas    : altitud, latitud, longitud.
  • Temporales     : hora, mes, día del año, estación del año.

Entrada : DataFrame con todas las columnas del JOIN.
Salida  : DataFrame reducido listo para limpieza.
"""

import pandas as pd
import numpy as np


# ──────────────────────────────────────────────────────────────
# MAPEO DE COLUMNAS DISPONIBLES EN EL CSV
# ──────────────────────────────────────────────────────────────
COLS_METEOROLOGICAS = [
    "temperatura_inst",   # temperatura instantánea (°C)
    "temperatura_max",    # temperatura máxima (°C)
    "temperatura_min",    # temperatura mínima (°C)
    "humedad_inst",       # humedad relativa (%)
    "precipitacion_hora", # precipitación en la hora (mm)
    "precipitacion_dia",  # precipitación acumulada en el día (mm)
    # Las dos siguientes pueden no existir en el CSV; se manejan abajo
    "velocidad_viento",   # m/s  (columna opcional)
    "direccion_viento",   # grados (columna opcional)
]

COLS_GEOGRAFICAS = [
    "altitud_msnm",
    "latitud",
    "longitud",
]

COLS_CLAVE = [
    "estacion_nombre",
    "fecha",
]


# ──────────────────────────────────────────────────────────────
# FUNCIONES
# ──────────────────────────────────────────────────────────────

def seleccionar_columnas_disponibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra solo las columnas que existen en el DataFrame.
    Las columnas opcionales (velocidad/dirección viento) se
    incluyen solo si están presentes.
    """
    todas = COLS_CLAVE + COLS_METEOROLOGICAS + COLS_GEOGRAFICAS
    disponibles = [c for c in todas if c in df.columns]
    faltantes   = [c for c in todas if c not in df.columns]

    if faltantes:
        print(f"[PASO 2] ⚠️  Columnas opcionales no encontradas (se omiten): {faltantes}")

    df_sel = df[disponibles].copy()
    print(f"[PASO 2] Columnas seleccionadas ({len(disponibles)}): {disponibles}")
    return df_sel


def generar_variables_temporales(df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir de la columna 'fecha' genera:
      - hora          : 0-23
      - mes           : 1-12
      - dia_anio      : 1-365/366
      - estacion_anio : 0=Verano, 1=Otoño, 2=Invierno, 3=Primavera
                        (criterio hemisferio sur)
    """
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    df["hora"]     = df["fecha"].dt.hour
    df["mes"]      = df["fecha"].dt.month
    df["dia_anio"] = df["fecha"].dt.day_of_year

    # Hemisferio Sur (Arequipa, Perú)
    #   Verano  : Dic-Feb  → 0
    #   Otoño   : Mar-May  → 1
    #   Invierno: Jun-Ago  → 2
    #   Primavera: Sep-Nov → 3
    def _estacion(mes: int) -> int:
        if mes in (12, 1, 2):
            return 0   # Verano
        elif mes in (3, 4, 5):
            return 1   # Otoño
        elif mes in (6, 7, 8):
            return 2   # Invierno
        else:
            return 3   # Primavera

    df["estacion_anio"] = df["mes"].apply(_estacion)

    print(
        "[PASO 2] Variables temporales generadas: "
        "hora, mes, dia_anio, estacion_anio"
    )
    return df


def convertir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columnas numéricas al tipo float32 para reducir
    el uso de memoria.
    """
    df = df.copy()
    num_cols = df.select_dtypes(include=["object"]).columns.tolist()
    # Intenta convertir columnas de texto que deberían ser numéricas
    cols_excluir = {"estacion_nombre", "fecha"}
    for col in num_cols:
        if col not in cols_excluir:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    float_cols = df.select_dtypes(include=["float64"]).columns
    df[float_cols] = df[float_cols].astype("float32")

    print("[PASO 2] Tipos de dato ajustados (float32 para numéricas).")
    return df


def run(df_unido: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el Paso 2 completo."""
    print("\n" + "=" * 60)
    print("  PASO 2: SELECCIÓN DE VARIABLES")
    print("=" * 60)

    df = seleccionar_columnas_disponibles(df_unido)
    df = generar_variables_temporales(df)
    df = convertir_tipos(df)

    print(f"\n[PASO 2] Shape resultante: {df.shape}")
    print("[PASO 2] ✅ Listo.\n")
    return df


if __name__ == "__main__":
    import paso1_unir_datos as p1
    df_unido = p1.run()
    df = run(df_unido)
    print(df.dtypes)
    print(df.head())
