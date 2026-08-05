"""
PRUEBAS DE ROBUSTEZ Y GENERALIZACIÓN
======================================
Ejecuta las siguientes pruebas sobre el pipeline de predicción de heladas:

  1. Generalización Espacial (Leave-One-Station-Out CV)
  2. Generalización Temporal (TimeSeriesSplit CV - 5 Folds)
  3. Inyección de Ruido a Sensores (Resiliencia ante descalibración ±1°C a ±3°C)
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit, LeaveOneGroupOut
from sklearn.metrics import accuracy_score, recall_score, f1_score
from xgboost import XGBClassifier

# Forzar utf-8 en consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Rutas
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "ml"))

import paso1_unir_datos as p1
import paso2_seleccion_variables as p2
import paso3_limpieza as p3
import paso4_feature_engineering as p4
import paso5_construir_target as p5
import paso6_dividir_datos as p6
import paso7_entrenar as p7

OUTPUT_DIR = ROOT / "src" / "ml" / "outputs" / "pruebas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────
# CARGAR DATASET PROCESADO COMPLETO
# ──────────────────────────────────────────────────────────────

def obtener_dataset_preparado() -> tuple[pd.DataFrame, list[str]]:
    """Carga y ejecuta del paso 1 al 5 para obtener el dataset limpio listo."""
    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = p5.run(df)
    feature_cols = p6.obtener_features(df)
    return df, feature_cols


# ──────────────────────────────────────────────────────────────
# TEST 1.1: LEAVE-ONE-STATION-OUT CV (Generalización Espacial)
# ──────────────────────────────────────────────────────────────

def test_leave_one_station_out(df: pd.DataFrame, feature_cols: list[str], max_estaciones: int = 10) -> None:
    """
    Evalúa cómo generaliza el modelo al ser probado en estaciones
    que NUNCA vio en el entrenamiento.
    """
    print("\n" + "=" * 65)
    print("  TEST 1.1: LEAVE-ONE-STATION-OUT (Generalización Espacial)")
    print("=" * 65)

    estaciones = df["estacion_nombre"].unique()[:max_estaciones]
    resultados = []

    print(f"[TEST 1.1] Evaluando en {len(estaciones)} estaciones como test no visto...")

    for est in estaciones:
        train_mask = df["estacion_nombre"] != est
        test_mask  = df["estacion_nombre"] == est

        X_train, y_train = df.loc[train_mask, feature_cols], df.loc[train_mask, "nivel_riesgo"]
        X_test,  y_test  = df.loc[test_mask, feature_cols],  df.loc[test_mask, "nivel_riesgo"]

        model = XGBClassifier(
            objective="multi:softprob", num_class=5, max_depth=5,
            learning_rate=0.05, n_estimators=100, random_state=42,
            tree_method="hist", device="cuda", verbosity=0
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1  = f1_score(y_test, y_pred, average="macro", zero_division=0)

        resultados.append({"estacion": est, "accuracy": acc, "recall_macro": rec, "f1_macro": f1})
        print(f"  Estación no vista: {est:20s} → Accuracy: {acc:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")

    df_res = pd.DataFrame(resultados)
    print("-" * 65)
    print(f"  PROMEDIO GLOBAL (N={len(estaciones)}):")
    print(f"  Mean Accuracy    : {df_res['accuracy'].mean():.4f} ± {df_res['accuracy'].std():.4f}")
    print(f"  Mean Recall Macro: {df_res['recall_macro'].mean():.4f} ± {df_res['recall_macro'].std():.4f}")
    print(f"  Mean F1 Macro    : {df_res['f1_macro'].mean():.4f} ± {df_res['f1_macro'].std():.4f}")
    print("=" * 65)


# ──────────────────────────────────────────────────────────────
# TEST 1.2: TIME-SERIES-SPLIT CV (Generalización Temporal)
# ──────────────────────────────────────────────────────────────

def test_time_series_split(df: pd.DataFrame, feature_cols: list[str], n_splits: int = 5) -> None:
    """
    Evalúa el desempeño a través de ventanas temporales secuenciales
    usando TimeSeriesSplit de 5 pliegues.
    """
    print("\n" + "=" * 65)
    print("  TEST 1.2: TIME-SERIES-SPLIT (Generalización Temporal)")
    print("=" * 65)

    df_sorted = df.sort_values("fecha").reset_index(drop=True)
    X = df_sorted[feature_cols]
    y = df_sorted["nivel_riesgo"]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    fold = 1
    scores = []

    for train_idx, test_idx in tscv.split(X):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_te, y_te = X.iloc[test_idx],  y.iloc[test_idx]

        model = XGBClassifier(
            objective="multi:softprob", num_class=5, max_depth=5,
            learning_rate=0.05, n_estimators=100, random_state=42,
            tree_method="hist", device="cuda", verbosity=0
        )
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        acc = accuracy_score(y_te, y_pred)
        rec = recall_score(y_te, y_pred, average="macro", zero_division=0)
        f1  = f1_score(y_te, y_pred, average="macro", zero_division=0)

        scores.append(acc)
        print(f"  Fold {fold} ({len(train_idx):,} train / {len(test_idx):,} test) → Accuracy: {acc:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")
        fold += 1

    print("-" * 65)
    print(f"  PROMEDIO CV TEMPORAL ({n_splits} folds): {np.mean(scores):.4f} ± {np.std(scores):.4f}")
    print("=" * 65)


# ──────────────────────────────────────────────────────────────
# TEST 2.1: INYECCIÓN DE RUIDO A SENSORES (Robustez)
# ──────────────────────────────────────────────────────────────

def test_inyeccion_ruido(df: pd.DataFrame, feature_cols: list[str]) -> None:
    """
    Simula descalibración o ruido de sensores introduciendo ruido gaussiano
    a temperatura y humedad en el test set, y recalculando variables derivadas.
    """
    print("\n" + "=" * 65)
    print("  TEST 2.1: INYECCIÓN DE RUIDO A SENSORES (Robustez)")
    print("=" * 65)

    # Split limpio 3 vías
    X_train, X_val, X_test, y_train, y_val, y_test = p6.dividir_datos(df, modo="cronologico")
    model = p7.run(X_train, X_val, y_train, y_val)

    # 1. Baseline limpio
    y_pred_base = model.predict(X_test)
    acc_base = accuracy_score(y_test, y_pred_base)
    rec_base = recall_score(y_test, y_pred_base, average="macro", zero_division=0)

    print(f"\n[TEST 2.1] Rendimiento Base (Sin ruido): Accuracy = {acc_base:.4f} | Recall Macro = {rec_base:.4f}")
    print("-" * 65)
    print(f"  {'Nivel de Ruido':<25} {'Accuracy':>10} {'Recall Macro':>15} {'Caída Acc':>12}")
    print("-" * 65)

    niveles_ruido = [
        ("Leve (±0.5°C, ±2% HR)", 0.5, 2.0),
        ("Moderado (±1.0°C, ±5% HR)", 1.0, 5.0),
        ("Alto (±2.0°C, ±10% HR)", 2.0, 10.0),
        ("Extremo (±3.0°C, ±15% HR)", 3.0, 15.0),
    ]

    resultados = []

    for nombre, sigma_t, sigma_h in niveles_ruido:
        X_noisy = X_test.copy()

        # Inyectar ruido gaussiano
        ruido_t = np.random.normal(0, sigma_t, size=len(X_noisy))
        ruido_h = np.random.normal(0, sigma_h, size=len(X_noisy))

        X_noisy["temperatura_inst"] += ruido_t
        X_noisy["humedad_inst"]     = np.clip(X_noisy["humedad_inst"] + ruido_h, 0, 100)

        # Recalcular variables físicas derivadas afectadas por el ruido
        X_noisy["punto_rocio"]   = X_noisy["temperatura_inst"] - ((100.0 - X_noisy["humedad_inst"]) / 5.0)
        X_noisy["delta_t_rocio"] = X_noisy["temperatura_inst"] - X_noisy["punto_rocio"]

        # Predecir con datos ruidosos
        y_pred_noisy = model.predict(X_noisy)
        acc_noisy = accuracy_score(y_test, y_pred_noisy)
        rec_noisy = recall_score(y_test, y_pred_noisy, average="macro", zero_division=0)
        caida = acc_base - acc_noisy

        resultados.append({"nombre": nombre, "accuracy": acc_noisy, "recall": rec_noisy, "caida": caida})
        print(f"  {nombre:<25} {acc_noisy:>10.4f} {rec_noisy:>15.4f} {-caida:>11.2%}")

    print("=" * 65)

    # Gráfico de resistencia a ruido
    fig, ax = plt.subplots(figsize=(8, 4))
    nombres = [r["nombre"].split(" (")[0] for r in resultados]
    accs = [acc_base] + [r["accuracy"] for r in resultados]
    labels = ["Limpio"] + nombres

    bars = ax.bar(labels, accs, color=["#2ecc71", "#3498db", "#f39c12", "#e67e22", "#e74c3c"])
    ax.bar_label(bars, fmt="%.4f", padding=3, fontsize=9)
    ax.set_title("Resiliencia del Modelo XGBoost ante Ruido en Sensores", fontsize=11, fontweight="bold")
    ax.set_ylabel("Accuracy Global")
    ax.set_ylim(0.5, 1.0)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = OUTPUT_DIR / "resiliencia_ruido_sensores.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[TEST 2.1] 📊 Gráfico de resiliencia guardado en: {out}\n")


# ──────────────────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df, feature_cols = obtener_dataset_preparado()

    # Ejecutar Test 1.1 y 1.2
    test_leave_one_station_out(df, feature_cols)
    test_time_series_split(df, feature_cols)

    # Ejecutar Test 2.1
    test_inyeccion_ruido(df, feature_cols)
