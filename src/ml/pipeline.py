"""
PIPELINE COMPLETO - Predicción de Heladas
==========================================
Orquestador que ejecuta los 10 pasos en secuencia:

  Paso 1  → Unir datasets
  Paso 2  → Seleccionar variables
  Paso 3  → Limpiar datos
  Paso 4  → Feature engineering
  Paso 5  → Construir target (0-4)
  Paso 6  → Dividir datos (80/20)
  Paso 7  → Entrenar XGBoost
  Paso 8  → Evaluar modelo
  Paso 9  → Interpretabilidad SHAP
  Paso 10 → Exportar modelo

Uso:
  python pipeline.py                        # modo estratificado (default)
  python pipeline.py --modo cronologico     # división temporal
  python pipeline.py --sin-shap             # omite SHAP (más rápido)
"""

import argparse
import sys
import time
from pathlib import Path

# Configuración de encoding para consola de Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Asegurar que el directorio ml está en el path
sys.path.insert(0, str(Path(__file__).parent))

import paso1_unir_datos          as p1
import paso2_seleccion_variables as p2
import paso3_limpieza            as p3
import paso4_feature_engineering as p4
import paso5_construir_target    as p5
import paso6_dividir_datos       as p6
import paso7_entrenar            as p7
import paso8_evaluar             as p8
import paso9_shap                as p9
import paso10_exportar_modelo    as p10


def run_pipeline(
    modo: str = "cronologico",
    tipo_target: str = "binario",
    ejecutar_shap: bool = True
) -> None:
    """Ejecuta el pipeline completo de principio a fin."""
    inicio = time.time()

    print("\n" + "█" * 62)
    print("  🏔️  PIPELINE PREDICCIÓN DE HELADAS – AREQUIPA")
    print(f"  Equipo 05 | INNOVA HACK 2026 | Modo Target: {tipo_target.upper()}")
    print("█" * 62)

    # ── PASO 1: Unir datos ─────────────────────────────────────
    df = p1.run()

    # ── PASO 2: Seleccionar variables ──────────────────────────
    df = p2.run(df)

    # ── PASO 3: Limpieza ───────────────────────────────────────
    df = p3.run(df)

    # ── PASO 4: Feature Engineering ────────────────────────────
    df = p4.run(df)

    # ── PASO 5: Construir Target ───────────────────────────────
    df = p5.run(df, tipo_target=tipo_target)

    # ── PASO 6: Dividir datos ──────────────────────────────────
    X_train, X_val, X_test, y_train, y_val, y_test = p6.run(df, modo=modo)

    # ── PASO 7: Entrenamiento ──────────────────────────────────
    model = p7.run(X_train, X_val, y_train, y_val)

    # ── PASO 8: Evaluación ─────────────────────────────────────
    metricas = p8.run(model, X_test, y_test)

    # ── PASO 9: SHAP (opcional) ────────────────────────────────
    if ejecutar_shap:
        p9.run(model, X_test)
    else:
        print("\n[PIPELINE] SHAP omitido (--sin-shap).")

    # ── PASO 10: Exportar modelo ───────────────────────────────
    p10.run(model, X_test, metricas)

    # ── RESUMEN FINAL ──────────────────────────────────────────
    elapsed = time.time() - inicio
    minutos, segundos = divmod(elapsed, 60)

    print("\n" + "█" * 62)
    print("  ✅ PIPELINE COMPLETADO")
    print(f"  ⏱  Tiempo total: {int(minutos)}m {segundos:.1f}s")
    print()
    print("  📊 Métricas finales:")
    print(f"     Accuracy        : {metricas['accuracy']:.4f}")
    print(f"     Recall Macro    : {metricas['recall_macro']:.4f}")
    print(f"     F1 Macro        : {metricas['f1_macro']:.4f}")
    print()
    print("  📁 Artefactos generados:")
    outputs = Path(__file__).parent / "outputs"
    print(f"     {outputs / 'modelo' / 'modelo_heladas.json'}")
    print(f"     {outputs / 'modelo' / 'metadata.json'}")
    print(f"     {outputs / 'matriz_confusion.png'}")
    print(f"     {outputs / 'importancia_features.png'}")
    print(f"     {outputs / 'distribucion_target.png'}")
    if ejecutar_shap:
        print(f"     {outputs / 'shap' / 'shap_summary_clase4.png'}")
        print(f"     {outputs / 'shap' / 'shap_bar_global.png'}")
    print("█" * 62 + "\n")


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline completo de predicción de heladas (XGBoost)"
    )
    parser.add_argument(
        "--modo",
        choices=["estratificado", "cronologico"],
        default="cronologico",
        help="Modo de división del dataset (default: cronologico)",
    )
    parser.add_argument(
        "--target",
        choices=["binario", "binario_extremo", "multiclase"],
        default="binario_extremo",
        help="Tipo de clasificación del target: binario, binario_extremo (eventos raros ~100) o multiclase",
    )
    parser.add_argument(
        "--sin-shap",
        action="store_true",
        help="Omite el paso de interpretabilidad SHAP (más rápido)",
    )
    args = parser.parse_args()

    run_pipeline(modo=args.modo, tipo_target=args.target, ejecutar_shap=not args.sin_shap)
