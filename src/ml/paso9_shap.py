"""
PASO 9 - INTERPRETABILIDAD CON SHAP
=====================================
Usa la librería SHAP para explicar las predicciones del modelo XGBoost.

Gráficos generados:
  1. Summary Plot (beeswarm): impacto global de cada feature.
  2. Bar Plot: importancia media |SHAP| por feature.
  3. Waterfall Plot de un ejemplo individual (nivel 4 = Crítico).
  4. Dependence Plot entre temperatura y nivel de riesgo.

SHAP con XGBoost es muy eficiente gracias al TreeExplainer.
No requiere muestreo: puede correr sobre todo el dataset de test.

Entrada : modelo entrenado + X_test.
Salida  : gráficos en outputs/shap/.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

import shap
from xgboost import XGBClassifier


OUTPUT_DIR = Path(__file__).parent / "outputs" / "shap"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ETIQUETAS = {0: "Sin riesgo", 1: "Bajo", 2: "Moderado", 3: "Alto", 4: "Crítico"}


# ──────────────────────────────────────────────────────────────
# CALCULAR SHAP VALUES
# ──────────────────────────────────────────────────────────────

def calcular_shap_values(
    model: XGBClassifier,
    X: pd.DataFrame,
) -> tuple[shap.TreeExplainer, np.ndarray]:
    """
    Calcula los valores SHAP usando TreeExplainer (eficiente con XGBoost).

    Returns
    -------
    explainer   : TreeExplainer
    shap_values : array de forma (n_samples, n_features, n_classes)
    """
    print("[PASO 9] Calculando SHAP values con TreeExplainer...")
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    print(f"[PASO 9] SHAP values shape: {np.array(shap_values).shape}")
    return explainer, shap_values


def _extraer_shap_clase(shap_values, clase: int) -> np.ndarray:
    """Extrae la matriz SHAP de forma (n_samples, n_features) para una clase específica."""
    if isinstance(shap_values, list):
        return shap_values[clase]
    arr = np.array(shap_values)
    if arr.ndim == 3:
        if arr.shape[0] == 5:        # (n_classes, n_samples, n_features)
            return arr[clase]
        elif arr.shape[2] == 5:      # (n_samples, n_features, n_classes)
            return arr[:, :, clase]
    return arr


# ──────────────────────────────────────────────────────────────
# GRÁFICO 1: SUMMARY PLOT (BEESWARM)
# ──────────────────────────────────────────────────────────────

def graficar_summary_plot(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    clase: int = 4,
) -> None:
    """
    Summary beeswarm para una clase específica.
    Por defecto clase=4 (Crítico) porque es la más importante para alertas.
    """
    shap_mat = _extraer_shap_clase(shap_values, clase)

    fig, ax = plt.subplots(figsize=(10, 7))
    shap.summary_plot(
        shap_mat,
        X,
        show=False,
        plot_type="dot",
        max_display=15,
    )
    plt.title(
        f"SHAP Summary Plot – Clase {clase} ({ETIQUETAS[clase]})",
        fontsize=13, fontweight="bold", pad=15
    )
    plt.tight_layout()
    out = OUTPUT_DIR / f"shap_summary_clase{clase}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PASO 9] 📊 Summary plot (clase {clase}) guardado en: {out}")


# ──────────────────────────────────────────────────────────────
# GRÁFICO 2: BAR PLOT (IMPORTANCIA MEDIA |SHAP|)
# ──────────────────────────────────────────────────────────────

def graficar_bar_plot(
    shap_values: np.ndarray,
    X: pd.DataFrame,
) -> None:
    """
    Importancia global media de cada feature como |SHAP| promediado
    sobre todas las clases y todas las muestras.
    """
    arr = np.array(shap_values)
    if isinstance(shap_values, list):
        importancia_global = np.mean([np.abs(s).mean(axis=0) for s in shap_values], axis=0)
    elif arr.ndim == 3 and arr.shape[2] == 5:
        importancia_global = np.abs(arr).mean(axis=(0, 2))
    elif arr.ndim == 3 and arr.shape[0] == 5:
        importancia_global = np.abs(arr).mean(axis=(0, 1))
    else:
        importancia_global = np.abs(arr).mean(axis=0)

    df_imp = (
        pd.DataFrame({"feature": X.columns, "importancia": importancia_global})
        .sort_values("importancia", ascending=False)
        .head(15)
        .sort_values("importancia", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(df_imp["feature"], df_imp["importancia"], color="#9b59b6", edgecolor="white")
    ax.bar_label(bars, fmt="%.4f", fontsize=8, padding=3)
    ax.set_title("SHAP – Importancia Global de Features (|SHAP| medio)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Valor medio |SHAP|")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = OUTPUT_DIR / "shap_bar_global.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[PASO 9] 📊 Bar plot global guardado en: {out}")


# ──────────────────────────────────────────────────────────────
# GRÁFICO 3: WATERFALL PLOT – EJEMPLO INDIVIDUAL
# ──────────────────────────────────────────────────────────────

def graficar_waterfall(
    explainer: shap.TreeExplainer,
    X: pd.DataFrame,
    y_pred: np.ndarray,
    clase_objetivo: int = 4,
) -> None:
    """
    Waterfall plot para el primer ejemplo predicho como 'clase_objetivo'.
    Muestra por qué el modelo tomó esa decisión específica.
    """
    indices_clase = np.where(y_pred == clase_objetivo)[0]
    if len(indices_clase) == 0:
        print(f"[PASO 9] No se encontraron predicciones de clase {clase_objetivo} para waterfall.")
        return

    idx = indices_clase[0]   # primer ejemplo de esa clase
    shap_exp = explainer(X.iloc[[idx]])

    # shap_exp tiene forma (1, n_features, n_classes) para multiclase
    # seleccionamos la clase objetivo
    if hasattr(shap_exp, "values") and len(shap_exp.values.shape) == 3:
        exp_clase = shap.Explanation(
            values      = shap_exp.values[0, :, clase_objetivo],
            base_values = shap_exp.base_values[0, clase_objetivo],
            data        = shap_exp.data[0],
            feature_names = X.columns.tolist(),
        )
    else:
        exp_clase = shap_exp[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    shap.waterfall_plot(exp_clase, show=False, max_display=12)
    plt.title(
        f"SHAP Waterfall – Ejemplo predicho como Clase {clase_objetivo} ({ETIQUETAS[clase_objetivo]})",
        fontsize=11, fontweight="bold"
    )
    plt.tight_layout()

    out = OUTPUT_DIR / f"shap_waterfall_clase{clase_objetivo}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PASO 9] 📊 Waterfall plot guardado en: {out}")


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 9
# ──────────────────────────────────────────────────────────────

def run(
    model: XGBClassifier,
    X_test: pd.DataFrame,
) -> None:
    """Ejecuta el Paso 9 completo."""
    print("\n" + "=" * 60)
    print("  PASO 9: INTERPRETABILIDAD CON SHAP")
    print("=" * 60)

    explainer, shap_values = calcular_shap_values(model, X_test)

    graficar_summary_plot(shap_values, X_test, clase=4)   # Crítico
    graficar_summary_plot(shap_values, X_test, clase=3)   # Alto
    graficar_bar_plot(shap_values, X_test)

    y_pred = model.predict(X_test)
    graficar_waterfall(explainer, X_test, y_pred, clase_objetivo=4)

    print(
        "\n[PASO 9] Interpretación SHAP completa.\n"
        "         Los gráficos explican:\n"
        "           • Qué variables impulsan el riesgo crítico (clase 4)\n"
        "           • Por qué un ejemplo específico fue clasificado así\n"
    )
    print("[PASO 9] ✅ Listo.\n")


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
    run(model, X_test)
