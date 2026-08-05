"""
PASO 5 - CONSTRUCCIÓN DEL TARGET
==================================
Genera la variable objetivo 'nivel_riesgo' (0-4) basada en la
temperatura mínima horaria, usando umbrales meteorológicos ajustados
a la realidad climática de Arequipa / Andes peruanos.

Escala de riesgo:
  0 → Sin riesgo    : temperatura_min > 4°C
  1 → Bajo          : 2°C  < temperatura_min ≤ 4°C
  2 → Moderado      : 0°C  < temperatura_min ≤ 2°C
  3 → Alto          :-2°C  < temperatura_min ≤ 0°C
  4 → Crítico       : temperatura_min ≤ -2°C

La columna 'temperatura_min' debe existir en el DataFrame.
Si se desea usar temperatura_inst como fallback, se activa con
use_inst_as_fallback=True.

Entrada : DataFrame con feature engineering aplicado.
Salida  : DataFrame con columna 'nivel_riesgo' (int8, 0-4).
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # sin ventana gráfica (ejecución en servidor)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import matplotlib.pyplot as plt
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────
# UMBRALES DE RIESGO AGROMETEOROLÓGICO (Reajustados SENAMHI)
# ──────────────────────────────────────────────────────────────
#
#   Nivel 0 (Sin riesgo) : temp > 5.0°C
#   Nivel 1 (Bajo)       : 2.0°C < temp ≤ 5.0°C
#   Nivel 2 (Moderado)   : 0.0°C < temp ≤ 2.0°C  (Helada agrícola leve / escarcha)
#   Nivel 3 (Alto)       : -8.0°C < temp ≤ 0.0°C (Helada agrometeorológica moderada)
#   Nivel 4 (Crítico)    : temp ≤ -8.0°C O anomalía severa ≤ -6.0°C
#                          (Evento extremo e infrecuente)
# ──────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────
# ÍNDICE DE RIESGO MULTIFACTORIAL (Meteorológico Agrometeorológico)
# ──────────────────────────────────────────────────────────────
# Combina:
#   1. Intensidad de Temperatura Mínima Futura
#   2. Duración del Congelamiento (Horas acumuladas bajo 0°C)
#   3. Humedad Relativa (Condición para formación de escarcha/hielo)
#   4. Anomalía Climatológica (Rareza del evento en esa estación/mes)
# ──────────────────────────────────────────────────────────────


def calcular_riesgo_impacto(
    temp_min: float,
    duracion_h: float = 0.0,
    humedad: float = 50.0,
    anomalia: float = 0.0,
) -> int:
    """
    Calcula el nivel de riesgo de helada (0-4) mediante la matriz multifactorial
    de impacto meteorológico.

    0 → Sin riesgo (>5°C)
    1 → Vigilancia / Descenso de temperatura
    2 → Helada Ligera
    3 → Helada Moderada
    4 → Helada Severa / Crítica
    """
    if temp_min > 5.0 and anomalia > -3.0:
        return 0   # Sin riesgo agrometeorológico

    riesgo = 0

    # ── 1. Intensidad de Temperatura Mínima ──
    if temp_min <= -6.0:
        riesgo += 3
    elif temp_min <= -3.0:
        riesgo += 2
    elif temp_min <= 0.0:
        riesgo += 1

    # ── 2. Duración del Enfriamiento (Horas bajo 0°C) ──
    if duracion_h >= 6.0:
        riesgo += 2
    elif duracion_h >= 3.0:
        riesgo += 1

    # ── 3. Humedad (Factor Escarcha / Hielo) ──
    if humedad >= 80.0 and temp_min <= 0.0:
        riesgo += 1

    # ── 4. Rareza / Anomalía Climatológica ──
    if anomalia <= -4.0:
        riesgo += 1

    return min(max(riesgo, 0), 4)


def construir_target(
    df: pd.DataFrame,
    horizonte_horas: int = 6,
    tipo_target: str = "binario",
    use_inst_as_fallback: bool = True,
) -> pd.DataFrame:
    """
    Añade la columna 'nivel_riesgo' proyectada 'horizonte_horas' hacia el futuro.

    tipo_target:
      • "binario"    → 0: Sin Helada / Normal, 1: Alerta de Helada (Recomendado)
      • "multiclase" → 0: Sin riesgo, 1: Bajo, 2: Moderado, 3: Alto, 4: Crítico
    """
    df = df.copy()
    df = df.sort_values(["estacion_nombre", "fecha"]).reset_index(drop=True)

    if "temperatura_min" not in df.columns:
        raise ValueError("[PASO 5] ❌ La columna 'temperatura_min' no está en el DataFrame.")

    # Temperatura efectiva base
    temp_base = df["temperatura_min"]
    if use_inst_as_fallback and temp_base.isna().any() and "temperatura_inst" in df.columns:
        temp_base = temp_base.fillna(df["temperatura_inst"])

    # Proyección hacia el futuro (+horizonte_horas)
    df["temp_min_futura"] = (
        df.groupby("estacion_nombre", group_keys=False)[temp_base.name if hasattr(temp_base, 'name') else "temperatura_min"]
        .shift(-horizonte_horas)
    )

    # Duración futura (horas bajo cero proyectadas)
    col_duracion = "horas_bajo_cero" if "horas_bajo_cero" in df.columns else None
    if col_duracion:
        df["duracion_futura"] = (
            df.groupby("estacion_nombre", group_keys=False)[col_duracion]
            .shift(-horizonte_horas)
        )
    else:
        df["duracion_futura"] = 0.0

    # Humedad futura
    if "humedad_inst" in df.columns:
        df["humedad_futura"] = (
            df.groupby("estacion_nombre", group_keys=False)["humedad_inst"]
            .shift(-horizonte_horas)
        )
    else:
        df["humedad_futura"] = 50.0

    # Anomalía futura
    if "temp_min_normal" in df.columns:
        df["anomalia_futura"] = df["temp_min_futura"] - df["temp_min_normal"]
    else:
        df["anomalia_futura"] = 0.0

    # Eliminar filas sin futuro observado
    n_inicial = len(df)
    df = df.dropna(subset=["temp_min_futura"]).copy()
    df["duracion_futura"] = df["duracion_futura"].fillna(0.0)
    df["humedad_futura"]  = df["humedad_futura"].fillna(50.0)
    df["anomalia_futura"] = df["anomalia_futura"].fillna(0.0)

    print(f"[PASO 5] Horizonte de predicción: +{horizonte_horas} horas hacia el futuro.")
    print(f"[PASO 5] Modo Target: {tipo_target.upper()}")
    print(f"[PASO 5] Filas ajustadas por ventana futura: {n_inicial:,} → {len(df):,}")

    # Asignación del riesgo multifactorial
    riesgo_multiclase = df.apply(
        lambda r: calcular_riesgo_impacto(
            temp_min=r["temp_min_futura"],
            duracion_h=r["duracion_futura"],
            humedad=r["humedad_futura"],
            anomalia=r["anomalia_futura"]
        ),
        axis=1
    )

    if tipo_target == "binario_extremo":
        # Binario Ultra-Estricto (Helada Catastrófica / Extrema única):
        # Solamente alerta ante heladas severas extremas (Nivel 4 / Temp <= -24°C / Exposición crítica)
        # Esto reduce el total a ~100-130 alertas en el conjunto de prueba (eventos ultra raros).
        df["nivel_riesgo"] = (riesgo_multiclase == 4).astype("int8")
    elif tipo_target == "binario":
        # Binario Estándar: 0 = Normal / Frío Leve (0 y 1), 1 = Helada Agrícola (2, 3 y 4)
        df["nivel_riesgo"] = (riesgo_multiclase >= 2).astype("int8")
    else:
        df["nivel_riesgo"] = riesgo_multiclase.astype("int8")

    df = df.drop(columns=["temp_min_futura", "duracion_futura", "humedad_futura", "anomalia_futura"])

    return df


# ──────────────────────────────────────────────────────────────
# REPORTE DE DISTRIBUCIÓN DEL TARGET
# ──────────────────────────────────────────────────────────────

ETIQUETAS_MULTICLASE = {
    0: "Sin riesgo",
    1: "Bajo",
    2: "Moderado",
    3: "Alto",
    4: "Crítico",
}

ETIQUETAS_BINARIAS = {
    0: "Sin Helada",
    1: "Alerta de Helada",
}


def reportar_distribucion(df: pd.DataFrame) -> None:
    """Imprime y guarda gráfico de distribución del target."""
    dist = df["nivel_riesgo"].value_counts().sort_index()
    es_binario = len(dist) <= 2
    etiquetas_map = ETIQUETAS_BINARIAS if es_binario else ETIQUETAS_MULTICLASE

    print("\n[PASO 5] Distribución del target 'nivel_riesgo':")
    print("-" * 45)
    print(f"  {'Nivel':<10} {'Etiqueta':<20} {'N':>8}  {'%':>7}")
    print("-" * 45)
    for nivel, n in dist.items():
        etiqueta = etiquetas_map.get(nivel, f"Clase {nivel}")
        pct = n / len(df) * 100
        print(f"  {nivel:<10} {etiqueta:<20} {n:>8,}  {pct:>6.2f}%")
    print("-" * 45)

    # Gráfico de barras
    colores = ["#2ecc71", "#e74c3c"] if es_binario else ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(
        [etiquetas_map.get(i, str(i)) for i in sorted(dist.index)],
        [dist[i] for i in sorted(dist.index)],
        color=[colores[i] for i in sorted(dist.index)],
        edgecolor="white",
        linewidth=0.8,
    )
    ax.bar_label(bars, fmt="%d", fontsize=9, padding=3)
    ax.set_title("Distribución del Target: Alerta de Helada" if es_binario else "Distribución del Target: Nivel de Riesgo", fontsize=12, fontweight="bold")
    ax.set_xlabel("Categoría de Alerta" if es_binario else "Nivel de Riesgo")
    ax.set_ylabel("Cantidad de registros")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = OUTPUT_DIR / "distribucion_target.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[PASO 5] 📊 Gráfico guardado en: {out}")


# ──────────────────────────────────────────────────────────────
# PIPELINE COMPLETO DEL PASO 5
# ──────────────────────────────────────────────────────────────

def run(df_features: pd.DataFrame, tipo_target: str = "binario") -> pd.DataFrame:
    """Ejecuta el Paso 5 completo."""
    print("\n" + "=" * 60)
    print("  PASO 5: CONSTRUCCIÓN DEL TARGET")
    print("=" * 60)

    df = construir_target(df_features, tipo_target=tipo_target)
    reportar_distribucion(df)

    print(f"\n[PASO 5] ✅ Target 'nivel_riesgo' ({tipo_target}) creado. Shape: {df.shape}\n")
    return df


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import paso1_unir_datos as p1
    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4

    df = p1.run()
    df = p2.run(df)
    df = p3.run(df)
    df = p4.run(df)
    df = run(df)
    print(df[["estacion_nombre", "fecha", "temperatura_min", "nivel_riesgo"]].head(15))
