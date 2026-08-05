"""
PASO 8 - EVALUACIÓN DEL MODELO
================================
Evalúa el modelo entrenado con las métricas apropiadas para
clasificación multiclase desbalanceada:

  • Accuracy global
  • Recall Macro  (prioridad: detectar heladas reales → minimizar FN)
  • Recall Weighted
  • F1 Score Macro y Weighted
  • Classification Report completo (por clase)
  • Matriz de Confusión (gráfico)
  • Importancia de Features (Top 15)

Entrada : modelo entrenado + X_test, y_test.
Salida  : dict con métricas + gráficos en outputs/.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from xgboost import XGBClassifier


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ETIQUETAS_MULTICLASE = {0: "Sin riesgo", 1: "Bajo", 2: "Moderado", 3: "Alto", 4: "Crítico"}
ETIQUETAS_BINARIAS   = {0: "Sin Helada", 1: "Alerta de Helada"}


# ──────────────────────────────────────────────────────────────
# MÉTRICAS ESCALARES
# ──────────────────────────────────────────────────────────────

def calcular_metricas(
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> dict:
    """Calcula y devuelve un diccionario con las métricas clave."""
    metricas = {
        "accuracy"        : accuracy_score(y_true, y_pred),
        "recall_macro"    : recall_score(y_true, y_pred, average="macro",    zero_division=0),
        "recall_weighted" : recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "f1_macro"        : f1_score(y_true, y_pred, average="macro",        zero_division=0),
        "f1_weighted"     : f1_score(y_true, y_pred, average="weighted",     zero_division=0),
    }
    return metricas


def imprimir_metricas(metricas: dict) -> None:
    """Imprime el resumen de métricas en consola."""
    print("\n[PASO 8] ── Métricas de Evaluación XGBoost ───────────────")
    print(f"  Accuracy        : {metricas['accuracy']:.4f}")
    print(f"  Recall Macro    : {metricas['recall_macro']:.4f}  ← minimiza FN (heladas no detectadas)")
    print(f"  Recall Weighted : {metricas['recall_weighted']:.4f}")
    print(f"  F1 Macro        : {metricas['f1_macro']:.4f}")
    print(f"  F1 Weighted     : {metricas['f1_weighted']:.4f}")
    print("[PASO 8] ─────────────────────────────────────────────────\n")


def evaluar_baselines(X_test: pd.DataFrame, y_test: pd.Series) -> None:
    """Evalúa un modelo baseline ingenuo basado en la temperatura actual."""
    if "temperatura_inst" in X_test.columns:
        clases_presentes = sorted(y_test.unique())
        if len(clases_presentes) <= 2:
            # Baseline binario: Temp <= 2°C → Alerta (1), else 0
            y_base = (X_test["temperatura_inst"] <= 2.0).astype(int)
        else:
            def _riesgo_abs(t):
                if t > 5.0: return 0
                elif t > 2.0: return 1
                elif t > 0.0: return 2
                elif t > -3.0: return 3
                else: return 4
            y_base = X_test["temperatura_inst"].apply(_riesgo_abs)

        acc_base = accuracy_score(y_test, y_base)
        rec_base = recall_score(y_test, y_base, average="macro", zero_division=0)
        f1_base = f1_score(y_test, y_base, average="macro", zero_division=0)
        print("[PASO 8] ── Comparativa con Baseline (Regla Simple Temp Inst) ──")
        print(f"  Baseline Accuracy    : {acc_base:.4f}")
        print(f"  Baseline Recall Macro: {rec_base:.4f}")
        print(f"  Baseline F1 Macro    : {f1_base:.4f}")
        print("─────────────────────────────────────────────────────────────\n")


# ──────────────────────────────────────────────────────────────
# CLASSIFICATION REPORT
# ──────────────────────────────────────────────────────────────

def _obtener_etiquetas(y_true: pd.Series) -> tuple[list[int], list[str]]:
    clases_presentes = sorted(y_true.unique())
    mapa = ETIQUETAS_BINARIAS if len(clases_presentes) <= 2 else ETIQUETAS_MULTICLASE
    etiquetas = [mapa.get(i, f"Clase {i}") for i in clases_presentes]
    return clases_presentes, etiquetas


def imprimir_classification_report(
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> None:
    """Imprime el reporte detallado por clase."""
    clases_presentes, etiquetas = _obtener_etiquetas(y_true)

    print("[PASO 8] ── Classification Report ───────────────────────")
    print(
        classification_report(
            y_true, y_pred,
            labels=clases_presentes,
            target_names=etiquetas,
            zero_division=0,
        )
    )


# ──────────────────────────────────────────────────────────────
# MATRIZ DE CONFUSIÓN
# ──────────────────────────────────────────────────────────────

def graficar_matriz_confusion(
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> None:
    """Guarda una matriz de confusión normalizada como heatmap."""
    clases_presentes, etiquetas = _obtener_etiquetas(y_true)

    cm = confusion_matrix(y_true, y_pred, labels=clases_presentes, normalize="true")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=etiquetas,
        yticklabels=etiquetas,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title(
        "Matriz de Confusión (Normalizada)\nModelo XGBoost - Riesgo de Helada",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlabel("Predicción", fontsize=11)
    ax.set_ylabel("Real", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    out = OUTPUT_DIR / "matriz_confusion.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[PASO 8] 📊 Matriz de confusión guardada en: {out}")


# ──────────────────────────────────────────────────────────────
# IMPORTANCIA DE FEATURES
# ──────────────────────────────────────────────────────────────

def graficar_importancia_features(
    model: XGBClassifier,
    feature_names: list[str],
    top_n: int = 15,
) -> None:
    """Gráfico de barras con las Top N features por importancia (gain)."""
    importancias = model.feature_importances_
    df_imp = (
        pd.DataFrame({"feature": feature_names, "importancia": importancias})
        .sort_values("importancia", ascending=False)
        .head(top_n)
        .sort_values("importancia", ascending=True)   # para barh
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(
        df_imp["feature"], df_imp["importancia"],
        color="#3498db", edgecolor="white", linewidth=0.5
    )
    ax.bar_label(bars, fmt="%.4f", fontsize=8, padding=3)
    ax.set_title(
        f"Top {top_n} Features más Importantes (XGBoost gain)",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlabel("Importancia (gain normalizado)")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = OUTPUT_DIR / "importancia_features.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[PASO 8] 📊 Importancia de features guardada en: {out}")

    # Imprimir ranking en consola
    print("\n[PASO 8] ── Top Features ───────────────────────────────")
    for _, row in df_imp.sort_values("importancia", ascending=False).iterrows():
        print(f"  {row['feature']:30s}: {row['importancia']:.5f}")
    print()


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 8
# ──────────────────────────────────────────────────────────────

def run(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Ejecuta el Paso 8 completo y devuelve las métricas."""
    print("\n" + "=" * 60)
    print("  PASO 8: EVALUACIÓN DEL MODELO")
    print("=" * 60)

    y_pred = model.predict(X_test)

    metricas = calcular_metricas(y_test, y_pred)
    imprimir_metricas(metricas)
    evaluar_baselines(X_test, y_test)
    imprimir_classification_report(y_test, y_pred)
    graficar_matriz_confusion(y_test, y_pred)
    graficar_importancia_features(model, X_test.columns.tolist())

    print("[PASO 8] ✅ Listo.\n")
    return metricas


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

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = p5.run(df)
    X_train, X_test, y_train, y_test = p6.run(df)
    model = p7.run(X_train, X_test, y_train, y_test)
    metricas = run(model, X_test, y_test)
