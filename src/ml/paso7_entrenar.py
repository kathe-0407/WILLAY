"""
PASO 7 - ENTRENAMIENTO XGBoost
================================
Entrena un XGBClassifier multiclase con los hiperparámetros base
recomendados y soporte para clases desbalanceadas.

Configuración del modelo:
  objective       = multi:softprob   → probabilidad para cada clase
  num_class       = 5                → niveles 0-4
  max_depth       = 6
  learning_rate   = 0.1
  n_estimators    = 300
  subsample       = 0.8
  colsample_bytree= 0.8
  eval_metric     = mlogloss
  early_stopping  = 30 rondas (sobre validation set interno)

Salida:
  • Modelo entrenado (XGBClassifier)
  • Curva de aprendizaje guardada en outputs/
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from xgboost import XGBClassifier


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NUM_CLASSES = 5   # niveles 0-4


# ──────────────────────────────────────────────────────────────
# MANEJO DE CLASES DESBALANCEADAS
# ──────────────────────────────────────────────────────────────

def calcular_pesos_clase(y_train: pd.Series) -> dict[int, float]:
    """
    Calcula pesos inversamente proporcionales a la frecuencia de cada clase.
    Asigna mayor peso a las clases minoritarias (niveles 3 y 4 = heladas graves).
    """
    conteos = y_train.value_counts().sort_index()
    total   = len(y_train)
    n_clases = len(conteos)

    pesos = {
        nivel: total / (n_clases * n)
        for nivel, n in conteos.items()
    }
    print("[PASO 7] Pesos de clase para balanceo:")
    for nivel, peso in pesos.items():
        print(f"         Nivel {nivel}: {peso:.4f} (n={conteos[nivel]:,})")
    return pesos


def crear_sample_weights(y_train: pd.Series) -> np.ndarray:
    """
    Devuelve un array de pesos por muestra para XGBoost
    (parámetro sample_weight en .fit()).
    """
    pesos_clase = calcular_pesos_clase(y_train)
    return y_train.map(pesos_clase).values


# ──────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL MODELO (CON SOPORTE GPU AUTO-DETECTADO)
# ──────────────────────────────────────────────────────────────

def detectar_dispositivo() -> str:
    """
    Intenta verificar si CUDA está disponible para XGBoost.
    Retorna 'cuda' si está disponible y funcional, de lo contrario 'cpu'.
    """
    try:
        # Prueba rápida de ajuste en CUDA
        dummy_model = XGBClassifier(tree_method="hist", device="cuda")
        dummy_model.fit(np.array([[0]]), np.array([0]))
        print("[PASO 7] 🚀 GPU (CUDA) detectada y operativa para XGBoost.")
        return "cuda"
    except Exception:
        print("[PASO 7] 💻 CUDA no disponible o no configurado en XGBoost. Usando CPU.")
        return "cpu"


def construir_modelo(num_classes: int = 2, params: dict | None = None) -> XGBClassifier:
    """
    Devuelve el XGBClassifier configurado.
    Auto-detecta si el problema es binario (num_classes == 2) o multiclase.
    """
    dispositivo = detectar_dispositivo()

    is_binary = num_classes == 2

    defaults = dict(
        objective          = "binary:logistic" if is_binary else "multi:softprob",
        max_depth          = 6,
        learning_rate      = 0.05,
        n_estimators       = 300,
        subsample          = 0.8,
        colsample_bytree   = 0.8,
        reg_alpha          = 0.1,         # Regularización L1
        reg_lambda         = 1.0,         # Regularización L2
        min_child_weight   = 3,
        eval_metric        = "logloss" if is_binary else "mlogloss",
        early_stopping_rounds = 30,
        use_label_encoder  = False,
        random_state       = 42,
        verbosity          = 1,
    )

    if not is_binary:
        defaults["num_class"] = num_classes

    # Configurar dispositivo detectado
    if dispositivo == "cuda":
        defaults["device"] = "cuda"
        defaults["tree_method"] = "hist"
    else:
        defaults["device"] = "cpu"
        defaults["n_jobs"] = -1  # Usar todos los núcleos si va por CPU

    if params:
        defaults.update(params)

    model = XGBClassifier(**defaults)
    print(f"[PASO 7] Modelo XGBClassifier ({'BINARIO' if is_binary else 'MULTICLASE'}) creado con parámetros:\n{defaults}\n")
    return model



# ──────────────────────────────────────────────────────────────
# ENTRENAMIENTO
# ──────────────────────────────────────────────────────────────

def entrenar(
    model: XGBClassifier,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    usar_pesos: bool = True,
) -> XGBClassifier:
    """
    Entrena el modelo con early stopping sobre el conjunto de validación.

    Parameters
    ----------
    model       : XGBClassifier configurado.
    X_train     : Features de entrenamiento.
    y_train     : Target de entrenamiento.
    X_val       : Features de validación (puede ser X_test).
    y_val       : Target de validación.
    usar_pesos  : Si True, aplica pesos de clase por muestra.
    """
    sw = crear_sample_weights(y_train) if usar_pesos else None

    print(f"[PASO 7] Iniciando entrenamiento...")
    print(f"         X_train: {X_train.shape} | X_val: {X_val.shape}")

    model.fit(
        X_train, y_train,
        sample_weight=sw,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=50,   # imprime cada 50 rondas
    )

    best_iter = model.best_iteration
    print(f"\n[PASO 7] ✅ Entrenamiento finalizado.")
    print(f"[PASO 7] Mejor iteración (early stopping): {best_iter}")
    return model


# ──────────────────────────────────────────────────────────────
# CURVA DE APRENDIZAJE
# ──────────────────────────────────────────────────────────────

def graficar_curva_aprendizaje(model: XGBClassifier) -> None:
    """Guarda la curva de logloss train vs. val."""
    resultados = model.evals_result()
    if not resultados:
        print("[PASO 7] Sin resultados de evaluación para graficar.")
        return

    # Auto-detectar la clave de la métrica ('logloss' o 'mlogloss')
    metric_key = "logloss" if "logloss" in resultados["validation_0"] else "mlogloss"
    train_loss = resultados["validation_0"][metric_key]
    val_loss   = resultados["validation_1"][metric_key]
    epocas     = range(1, len(train_loss) + 1)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(epocas, train_loss, label=f"Train {metric_key}", color="#3498db", linewidth=1.5)
    ax.plot(epocas, val_loss,   label=f"Val {metric_key}",   color="#e74c3c", linewidth=1.5)

    if model.best_iteration:
        ax.axvline(
            model.best_iteration + 1, color="gray",
            linestyle="--", linewidth=1, label=f"Best iter: {model.best_iteration + 1}"
        )

    ax.set_title(f"Curva de Aprendizaje XGBoost - {metric_key}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Iteración (árbol)")
    ax.set_ylabel(metric_key)
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = OUTPUT_DIR / "curva_aprendizaje.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[PASO 7] 📊 Curva de aprendizaje guardada en: {out}")


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 7
# ──────────────────────────────────────────────────────────────

def run(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    params: dict | None = None,
) -> XGBClassifier:
    """Ejecuta el Paso 7 completo y devuelve el modelo entrenado."""
    print("\n" + "=" * 60)
    print("  PASO 7: ENTRENAMIENTO XGBoost")
    print("=" * 60)

    num_classes = len(np.unique(y_train))
    model = construir_modelo(num_classes=num_classes, params=params)
    model = entrenar(model, X_train, y_train, X_val, y_val)
    graficar_curva_aprendizaje(model)

    print("\n[PASO 7] ✅ Listo.\n")
    return model


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4
    import paso5_construir_target as p5
    import paso6_dividir_datos as p6

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = p5.run(df)
    X_train, X_test, y_train, y_test = p6.run(df)
    model = run(X_train, X_test, y_train, y_test)
