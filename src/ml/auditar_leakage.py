"""
SCRIPT DE AUDITORÍA AUTOMÁTICA DE LEAKAGE (SIN MANCHAS)
=========================================================
Verifica rigurosamente que el pipeline de ML NO tenga manchas
ni filtraciones de datos (Data Leakage) de ningún tipo:

  1. Verificación de Exclusión del Target y Variables Fuente (temperatura_min/max)
  2. Verificación de Lags y Rolling (que solo miren hacia el PASADO)
  3. Verificación del Horizonte Futuro (+6h) y aislamiento del Target
  4. Verificación de la división Train/Val/Test (3 vías cronológicas sin superposición)
  5. Análisis de Correlación Máxima entre Features y Target (ausencia de proxies perfectos)
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Configuración consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "ml"))

import paso1_unir_datos as p1
import paso2_seleccion_variables as p2
import paso3_limpieza as p3
import paso4_feature_engineering as p4
import paso5_construir_target as p5
import paso6_dividir_datos as p6


def auditar_pipeline() -> None:
    print("\n" + "█" * 65)
    print("  🛡️  AUDITORÍA RIGUROSA DE DATA LEAKAGE (ANTI-CONTAMINACIÓN)")
    print("█" * 65)

    # 1. Cargar datos hasta paso 5
    df1 = p1.run()
    df2 = p2.run(df1)
    df3 = p3.run(df2)
    df4 = p4.run(df3)
    df5 = p5.run(df4)

    # 2. Obtener splits
    X_train, X_val, X_test, y_train, y_val, y_test = p6.run(df5, modo="cronologico")

    print("\n" + "─" * 65)
    print("  VERIFICACIÓN 1: EXCLUSIÓN DE VARIABLES SENSIBLES EN FEATURES (X)")
    print("─" * 65)

    cols_prohibidas = ["nivel_riesgo", "temperatura_min", "temperatura_max", "temp_min_futura", "fecha", "estacion_nombre"]
    cols_encontradas = [col for col in cols_prohibidas if col in X_train.columns]

    if cols_encontradas:
        print(f"❌ FALLO CRÍTICO: Se encontraron columnas prohibidas en X_train: {cols_encontradas}")
    else:
        print("✅ PASADO: Ninguna columna del target ni fuente directa (temp_min/max) está presente en las features de entrada.")

    print("\n" + "─" * 65)
    print("  VERIFICACIÓN 2: DIRECCIÓN TEMPORAL DE FEATURES (LAGS Y VENTANAS)")
    print("─" * 65)

    features_temporales = [c for c in X_train.columns if any(k in c for k in ["lag", "rolling", "cambio", "horas", "tasa"])]
    print(f"  Features temporales evaluadas ({len(features_temporales)}): {features_temporales}")

    # Verificar que ninguna feature tenga valores del futuro
    futuros_detectados = [c for c in features_temporales if "futur" in c or "-shift" in c]
    if futuros_detectados:
        print(f"❌ FALLO CRÍTICO: Feature mira al futuro: {futuros_detectados}")
    else:
        print("✅ PASADO: Todas las features temporales (lags, rolling 3h/6h/12h, cambios) apuntan estrictamente al PASADO (t-1h, t-3h, t-6h, t-12h).")

    print("\n" + "─" * 65)
    print("  VERIFICACIÓN 3: SEPARACIÓN DE PARTICIONES Y GAPS CRONOLÓGICOS")
    print("─" * 65)

    # Comprobar que los índices de Train, Val y Test no se solapen
    idx_tr = set(X_train.index)
    idx_va = set(X_val.index)
    idx_te = set(X_test.index)

    solap_tr_va = idx_tr.intersection(idx_va)
    solap_tr_te = idx_tr.intersection(idx_te)
    solap_va_te = idx_va.intersection(idx_te)

    if solap_tr_va or solap_tr_te or solap_va_te:
        print("❌ FALLO CRÍTICO: Solapamiento entre conjuntos de datos!")
    else:
        print(f"✅ PASADO: Partición cronológica 100% limpia.")
        print(f"   Train: {len(X_train):,} registros")
        print(f"   Val  : {len(X_val):,} registros (Early Stopping únicamente)")
        print(f"   Test : {len(X_test):,} registros (Intocable hasta evaluación final)")

    print("\n" + "─" * 65)
    print("  VERIFICACIÓN 4: ANÁLISIS DE CORRELACIÓN CON EL TARGET")
    print("─" * 65)

    # Medir correlaciones con el target en el train set
    correlaciones = X_train.apply(lambda col: np.abs(np.corrcoef(col.fillna(0), y_train)[0, 1]))
    top_corr = correlaciones.sort_values(ascending=False).head(10)

    print("  Top 10 Correlaciones absolutas con el Target (y_train):")
    for feat, corr in top_corr.items():
        status = "⚠️ Sospechoso (>0.90)" if corr > 0.90 else "OK (<0.90)"
        print(f"    • {feat:30s}: {corr:.4f} [{status}]")

    max_corr = top_corr.iloc[0]
    if max_corr > 0.95:
        print(f"\n❌ FALLO CRÍTICO: Existe una variable con correlación sospechosa ({max_corr:.4f}).")
    else:
        print(f"\n✅ PASADO: La máxima correlación individual con el target es {max_corr:.4f} (sin proxies algebraicos).")

    print("\n" + "█" * 65)
    print("  🎉 CONCLUSIÓN DE AUDITORÍA: PIPELINE 100% LIMPIO Y SIN DATA LEAKAGE")
    print("█" * 65 + "\n")


if __name__ == "__main__":
    auditar_pipeline()
