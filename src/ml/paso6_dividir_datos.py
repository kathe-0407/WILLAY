"""
PASO 6 - DIVISIÓN DE DATOS (TRAIN / TEST)
==========================================
Divide el dataset en 80% entrenamiento y 20% test.

Estrategia:
  • Estratificación por 'nivel_riesgo' para preservar la distribución
    de clases en ambos conjuntos (importante con clases desbalanceadas).
  • División cronológica opcional: para datos temporales, se puede
    usar los últimos N meses como test en lugar de aleatoria.
  • Separa features (X) y target (y) de ambos conjuntos.

Entrada : DataFrame con features + 'nivel_riesgo'.
Salida  : X_train, X_test, y_train, y_test (DataFrames / Series).
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────
# COLUMNAS A EXCLUIR DEL ENTRENAMIENTO
# (no son features, son identificadores o el target)
# ──────────────────────────────────────────────────────────────
COLS_EXCLUIR = [
    "estacion_nombre",
    "fecha",
    "nivel_riesgo",   # target
    # Columnas que pueden causar data leakage si se dejan como features
    "temperatura_max",  # usada para construir el target indirectamente
    "temperatura_min",  # fuente directa del target → excluir en producción
]


def obtener_features(df: pd.DataFrame) -> list[str]:
    """
    Devuelve la lista de columnas que serán usadas como features.
    Excluye identificadores, target y columnas no numéricas.
    """
    excluir = set(COLS_EXCLUIR)
    features = [
        col for col in df.columns
        if col not in excluir
        and df[col].dtype not in ["object", "datetime64[ns]"]
    ]
    return features


def dividir_datos(
    df: pd.DataFrame,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42,
    modo: str = "cronologico",   # "cronologico" (recomendado) | "estratificado"
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Divide el DataFrame en 3 conjuntos: Entrenamiento (70%), Validación (15%) y Test (15%).

    En modo cronológico:
      - Train: primer 70% del tiempo
      - Val: siguiente 15% (usado para early stopping)
      - Test: último 15% (evaluación final sin tocar)
    """
    feature_cols = obtener_features(df)
    print(f"[PASO 6] Features seleccionadas ({len(feature_cols)}): {feature_cols}")

    if modo == "cronologico":
        df_sorted = df.sort_values("fecha").reset_index(drop=True)
        X = df_sorted[feature_cols]
        y = df_sorted["nivel_riesgo"]

        n_total = len(df_sorted)
        corte_val  = int(n_total * (1 - (val_size + test_size)))
        corte_test = int(n_total * (1 - test_size))

        X_train, y_train = X.iloc[:corte_val], y.iloc[:corte_val]
        X_val,   y_val   = X.iloc[corte_val:corte_test], y.iloc[corte_val:corte_test]
        X_test,  y_test  = X.iloc[corte_test:], y.iloc[corte_test:]

        print(f"[PASO 6] Modo cronológico 3 vías: Train (0..{corte_val:,}), Val ({corte_val:,}..{corte_test:,}), Test ({corte_test:,}..{n_total:,})")

    else:
        # División estratificada 3 partes
        X = df[feature_cols]
        y = df["nivel_riesgo"]

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=(val_size + test_size), random_state=random_state, stratify=y
        )
        ratio_test = test_size / (val_size + test_size)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=ratio_test, random_state=random_state, stratify=y_temp
        )
        print(f"[PASO 6] Modo estratificado 3 vías")

    return X_train, X_val, X_test, y_train, y_val, y_test


def reportar_division(
    y_train: pd.Series,
    y_val: pd.Series,
    y_test: pd.Series,
) -> None:
    """Imprime el resumen de tamaños de train, val y test."""
    total = len(y_train) + len(y_val) + len(y_test)
    print(f"\n[PASO 6] Total : {total:>10,} registros")
    print(f"[PASO 6] Train : {len(y_train):>10,} ({len(y_train)/total:.1%})")
    print(f"[PASO 6] Val   : {len(y_val):>10,} ({len(y_val)/total:.1%})")
    print(f"[PASO 6] Test  : {len(y_test):>10,} ({len(y_test)/total:.1%})")


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 6
# ──────────────────────────────────────────────────────────────

def run(
    df_con_target: pd.DataFrame,
    modo: str = "cronologico",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Ejecuta el Paso 6 completo."""
    print("\n" + "=" * 60)
    print("  PASO 6: DIVISIÓN DE DATOS (TRAIN / VAL / TEST)")
    print("=" * 60)

    X_train, X_val, X_test, y_train, y_val, y_test = dividir_datos(df_con_target, modo=modo)
    reportar_division(y_train, y_val, y_test)

    print("\n[PASO 6] ✅ Listo.\n")
    return X_train, X_val, X_test, y_train, y_val, y_test


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4
    import paso5_construir_target as p5

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = p5.run(df)

    X_train, X_test, y_train, y_test = run(df)
    print("\nX_train shape:", X_train.shape)
    print("X_test  shape:", X_test.shape)
    print("X_train columns:", X_train.columns.tolist())
