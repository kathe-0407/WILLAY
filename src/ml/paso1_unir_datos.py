"""
PASO 1 - UNIR DATASETS
======================
Une estaciones.csv y mediciones_hora.csv mediante el identificador
de estacion (estacion_nombre) para producir un único DataFrame base.

Columnas de estaciones.csv:
  estacion_nombre, tipo, latitud, longitud, altitud_msnm,
  provincia, distrito, zona_climatica

Columnas de mediciones_hora.csv:
  estacion_nombre, fecha, temperatura_inst, temperatura_max,
  temperatura_min, humedad_inst, precipitacion_hora, precipitacion_dia,
  nivel_inst_m, nivel_med_m, bateria_v
"""

import sys
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ──────────────────────────────────────────────────────────────
# RUTAS
# ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]          # raiz del proyecto
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "src" / "ml" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cargar_estaciones(path: Path = DATA_DIR / "estaciones.csv") -> pd.DataFrame:
    """Carga el catálogo de estaciones meteorológicas."""
    df = pd.read_csv(path, encoding="utf-8")
    print(f"[PASO 1] Estaciones cargadas: {len(df)} filas | Columnas: {df.columns.tolist()}")
    return df


def cargar_mediciones(path: Path = DATA_DIR / "mediciones_hora.csv") -> pd.DataFrame:
    """Carga las mediciones horarias del período anual."""
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    print(f"[PASO 1] Mediciones cargadas : {len(df):,} filas | Columnas: {df.columns.tolist()}")
    return df


def unir_datasets(
    df_estaciones: pd.DataFrame,
    df_mediciones: pd.DataFrame,
) -> pd.DataFrame:
    """
    Une ambos DataFrames por 'estacion_nombre' (left join sobre mediciones).
    
    Retorna el DataFrame combinado con todas las variables geográficas
    y meteorológicas en una sola tabla.
    """
    df = df_mediciones.merge(
        df_estaciones,
        on="estacion_nombre",
        how="left",
        validate="many_to_one",   # muchas mediciones por estación
    )

    # Reporte de unión
    estaciones_sin_match = df["latitud"].isna().sum()
    if estaciones_sin_match > 0:
        print(
            f"[PASO 1] ⚠️  {estaciones_sin_match} mediciones sin estación asociada "
            f"({estaciones_sin_match / len(df):.2%})"
        )
    else:
        print("[PASO 1] ✅ Todos los registros tienen estación asociada.")

    print(f"[PASO 1] DataFrame final: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    return df


def guardar_dataset_unido(df: pd.DataFrame) -> Path:
    """Persiste el dataset unido como Parquet para eficiencia."""
    out = OUTPUT_DIR / "dataset_unido.parquet"
    df.to_parquet(out, index=False, compression="snappy")
    print(f"[PASO 1] 💾 Guardado en: {out}")
    return out


def run() -> pd.DataFrame:
    """Ejecuta el paso completo y devuelve el DataFrame."""
    print("\n" + "=" * 60)
    print("  PASO 1: UNIÓN DE DATASETS")
    print("=" * 60)

    df_estaciones = cargar_estaciones()
    df_mediciones = cargar_mediciones()
    df = unir_datasets(df_estaciones, df_mediciones)
    guardar_dataset_unido(df)

    print(f"\n[PASO 1] Estaciones presentes en el dataset: {df['estacion_nombre'].nunique()}")
    print(f"[PASO 1] Rango temporal: {df['fecha'].min()}  →  {df['fecha'].max()}")
    print("[PASO 1] ✅ Listo.\n")
    return df


if __name__ == "__main__":
    df = run()
    print(df.head())
