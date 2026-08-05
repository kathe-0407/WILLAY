"""
SISTEMA DE GESTIÓN DE ALERTAS Y DEBOUNCING (ANTI-SPAM) DE HELADAS
===================================================================
Este script simula un motor de notificaciones agrometeorológico de producción
basado en los umbrales oficiales SENAMHI y la máquina de estados de alerta.

Problema que resuelve:
  Las heladas duran varios días o muchas horas continuas. Si el modelo predice
  'Helada Alto/Crítico' cada hora, enviar notificaciones continuas a los agricultores
  causaría 'Alert Fatigue' (spam).

Lógica del Motor de Alerta (Máquina de Estados por Estación):
  1. ALERTA_NUEVA      : Dispara notificación Push/SMS cuando inicia un episodio (Riesgo >= 2).
  2. SEGUIMIENTO      : Durante las horas siguientes del mismo episodio, el sistema registra
                         el estado en BD pero SILENCIA las notificaciones (ventana cooldown 12h-24h).
  3. ESCALAMIENTO      : Si la helada empeora a Crítica (Nivel 4), ROMPE la ventana e informa emergencia.
  4. ALERTA_FINALIZADA : Cuando las temperaturas retornan a normales (>4°C) por más de 3h,
                         envía la desactivación del evento.
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Configuración encoding Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "ml"))

from paso10_exportar_modelo import cargar_modelo, predecir


# ──────────────────────────────────────────────────────────────
# MÁQUINA DE ESTADOS DE ALERTA POR ESTACIÓN
# ──────────────────────────────────────────────────────────────

class GestorAlertasEstacion:
    """
    Controla el estado de alerta por PERIODOS MULTIDÍA / OLAS DE FRÍO para una estación.
    Tolera el calentamiento solar diurno sin cerrar la ola de frío prematuramente.
    Solo cierra la ola cuando pasan al menos 24 horas continuas (un ciclo completo) sin helada.
    """

    def __init__(self, nombre_estacion: str, horas_sin_helada_para_cierre: int = 24):
        self.estacion = nombre_estacion
        self.horas_cierre = horas_sin_helada_para_cierre  # Requiere 24h continuas normales para dar por terminada la ola de frío

        # Estado interno de la Ola de Frío
        self.alerta_activa = False
        self.inicio_ola = None
        self.temp_minima_ola = 99.0
        self.noches_heladas = 0
        self.horas_recuperacion = 0
        self.en_noche_congelamiento = False
        self.historial_notificaciones = []

    def procesar_lectura(self, fecha: datetime, nivel_predicho: int, probabilidad: float, temp_actual: float) -> dict | None:
        """
        Procesa la telemetría horaria. Identifica el inicio de una Ola de Frío Multidía y mantiene
        el estado activo durante los calentamientos diurnos hasta que pase un ciclo completo (24h) sin helada.
        """
        notificacion = None
        es_helada = (nivel_predicho >= 1)

        # ── EVENTO 1: INICIO DE PERIODO / OLA DE HELADAS (MULTIDÍA) ──
        if es_helada and not self.alerta_activa:
            self.alerta_activa = True
            self.inicio_ola = fecha
            self.temp_minima_ola = temp_actual
            self.noches_heladas = 1
            self.horas_recuperacion = 0
            self.en_noche_congelamiento = True

            notificacion = {
                "tipo_evento": "🟢 INICIO DE OLA DE FRÍO (PERIODO DE HELADAS MULTIDÍA)",
                "estacion": self.estacion,
                "fecha_hora": str(fecha),
                "nivel_riesgo": nivel_predicho,
                "probabilidad": probabilidad,
                "temperatura_inst": temp_actual,
                "mensaje": f"⚠️ ATENCIÓN OLA DE FRÍO: Se inicia un PERIODO DE HELADAS RECURRENTES en {self.estacion} para los próximos días.",
                "accion_requerida": "Activar protocolos de mitigación agrícola y protección continua de ganado."
            }

        # ── DURANTE LA OLA DE FRÍO (HORAS BAJO CERO / NOCHE) ──
        elif es_helada and self.alerta_activa:
            self.temp_minima_ola = min(self.temp_minima_ola, temp_actual)
            self.horas_recuperacion = 0

            # Contar nueva noche de la ola si venía de horas diurnas
            if not self.en_noche_congelamiento:
                self.noches_heladas += 1
                self.en_noche_congelamiento = True

            # Notificación SILENCIADA (Mantiene el estado sin enviar SMS/Push innecesarios)
            notificacion = None

        # ── CALENTAMIENTO DIURNO DENTRO DE LA OLA O TRANSICIÓN A NORMALIDAD ──
        elif not es_helada and self.alerta_activa:
            self.horas_recuperacion += 1
            self.temp_minima_ola = min(self.temp_minima_ola, temp_actual)
            if self.en_noche_congelamiento and self.horas_recuperacion >= 4:
                self.en_noche_congelamiento = False  # Pasó el pico nocturno del día

            # ── EVENTO 2: FINALIZACIÓN DE LA OLA DE FRÍO (Tras 24h continuas sin helada) ──
            if self.horas_recuperacion >= self.horas_cierre:
                duracion_dias = round((fecha - self.inicio_ola).total_seconds() / 86400.0, 1)

                notificacion = {
                    "tipo_evento": "🛑 FINALIZACIÓN DE OLA DE FRÍO",
                    "estacion": self.estacion,
                    "fecha_hora": str(fecha),
                    "inicio_ola": str(self.inicio_ola),
                    "duracion_dias": duracion_dias,
                    "noches_heladas_registradas": self.noches_heladas,
                    "temp_minima_absoluta": round(self.temp_minima_ola, 1),
                    "mensaje": f"✅ FIN DE OLA DE FRÍO: El periodo de heladas en {self.estacion} ha concluido. Duración: {duracion_dias} días ({self.noches_heladas} noches heladas) | Temp Mínima absoluta: {self.temp_minima_ola:.1f}°C.",
                    "accion_requerida": "Evaluar estado de cultivos, desmovilizar coberturas de emergencia y retornar a operaciones normales."
                }

                # Reset de estado
                self.alerta_activa = False
                self.inicio_ola = None
                self.noches_heladas = 0
                self.horas_recuperacion = 0
                self.en_noche_congelamiento = False

        if notificacion:
            self.historial_notificaciones.append(notificacion)

        return notificacion


# ──────────────────────────────────────────────────────────────
# SIMULACIÓN DEL MOTOR DE ALERTAS EN TIEMPO REAL
# ──────────────────────────────────────────────────────────────

def simular_sistema_alertas(limite_registros: int = 5000) -> None:
    print("  🚨 MOTOR DE GESTIÓN DE ALERTAS DE HELADA (CON DEBOUNCING / ANTI-SPAM)")
    print("  SENAMHI / Equipo 05 - Arequipa")


    # 1. Cargar modelo exportado
    model, features = cargar_modelo()
    print("[ALERTAS] ✅ Modelo XGBoost cargado desde disco.")

    # 2. Cargar datos de prueba recientes
    data_path = ROOT / "src" / "ml" / "outputs" / "dataset_unido.parquet"
    if not data_path.exists():
        print(f"[ALERTAS] ❌ Archivo de datos no encontrado en: {data_path}")
        return

    df = pd.read_parquet(data_path)
    df = df.sort_values(["fecha", "estacion_nombre"]).reset_index(drop=True)

    import paso2_seleccion_variables as p2
    import paso3_limpieza as p3
    import paso4_feature_engineering as p4

    estaciones_demo = ["Chivay", "Arequipa - Cayma", "Pampacolca", "Imata"]
    estaciones_disponibles = df["estacion_nombre"].unique()
    estaciones_simular = [e for e in estaciones_demo if e in estaciones_disponibles]

    if not estaciones_simular:
        estaciones_simular = list(estaciones_disponibles[:3])

    todas_notificaciones = []

    print(f"[ALERTAS] 📍 Simulando flujo de Olas de Frío en {len(estaciones_simular)} estaciones...\n")

    for estacion in estaciones_simular:
        df_estacion = df[df["estacion_nombre"] == estacion].head(limite_registros).copy()
        if len(df_estacion) == 0:
            continue

        df_estacion = p2.run(df_estacion)
        df_estacion = p3.run(df_estacion)
        df_features = p4.run(df_estacion)

        cols_X = [c for c in features if c in df_features.columns]
        X_pred_all = df_features[cols_X].fillna(0.0)

        probs_all = model.predict_proba(X_pred_all)
        preds_all = np.argmax(probs_all, axis=1)

        # Usar ventana de 14h continuas normales para cerrar una ola de frío
        gestor = GestorAlertasEstacion(nombre_estacion=estacion, horas_sin_helada_para_cierre=14)

        notis_estacion = []
        for i in range(len(df_features)):
            fecha = pd.to_datetime(df_features["fecha"].iloc[i])
            pred_nivel = int(preds_all[i])
            prob = float(probs_all[i, pred_nivel])
            t_inst = float(df_features["temperatura_inst"].iloc[i])

            noti = gestor.procesar_lectura(fecha, pred_nivel, prob, t_inst)
            if noti:
                notis_estacion.append(noti)

        todas_notificaciones.extend(notis_estacion)

        print(f"  📍 Estación '{estacion}': {len(notis_estacion)} notificaciones emitidas para {(preds_all >= 1).sum()}h de frío.")

    print("\n" + "=" * 65)
    print("  📊 RESUMEN GENERAL DE OLAS DE FRÍO MULTIDÍA")
    print("=" * 65)
    print(f"  • Total Notificaciones Emitidas (Solo Inicio/Fin): {len(todas_notificaciones)}")
    print("=" * 65 + "\n")

    print("  📩 EJEMPLO DE NOTIFICACIONES DE OLA DE FRÍO ENVIADAS (SMS / APP):")
    print("  " + "─" * 60)
    for noti in todas_notificaciones[:8]:
        print(f"  [{noti['fecha_hora']}] {noti['tipo_evento']} ({noti['estacion']})")
        print(f"    Mensaje: {noti['mensaje']}")
        print(f"    Acción : {noti['accion_requerida']}")
        print("  " + "─" * 60)

    out_path = ROOT / "src" / "ml" / "outputs" / "log_alertas_notificadas.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(todas_notificaciones, f, indent=2, ensure_ascii=False)

    print(f"\n[ALERTAS] 💾 Log de notificaciones exportado a: {out_path}\n")


if __name__ == "__main__":
    simular_sistema_alertas()
