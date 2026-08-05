# Flujo de Trabajo y Funcionamiento del Backend

Este documento resume qué hace el backend de Alerta Temprana y cómo funciona técnicamente "por debajo del capó".

---

## PARTE 1: ¿Qué procesa, busca y devuelve? (Resumen Ejecutivo)

### 🔍 1. ¿Qué es lo que BUSCA?
Cuando el Frontend hace una petición, el Backend:
- **Busca la estación:** Busca en los CSVs (previamente cargados en la memoria RAM) los datos geográficos de una estación específica (ej: "Imata", "Juliaca").
- **Busca la medición:** Rastrea la lectura climática más reciente o de la fecha solicitada.
- **Busca la contingencia:** Busca en su motor de reglas estáticas (`recommendation_service.py`) qué acciones de protección aplican para esa alerta.

### ⚙️ 2. ¿Qué es lo que PROCESA?
- **Limpieza (Feature Engineering):** Extrae solo lo que sirve (mes, hora) y unifica la data para crear el "vector de características" matemático.
- **Delegación de IA:** Se conecta con la carpeta `ml/` (del Integrante 1) y ejecuta la función `predict()`.
- **Ensamblaje:** Empareja el resultado matemático de la IA con las recomendaciones preventivas humanas que ya posee.

### 📤 3. ¿Qué es lo que DEVUELVE?
Devuelve al Frontend un objeto **JSON** listo para ser pintado en un Dashboard, conteniendo:
1. El tipo de evento detectado ("HELADA" o "FRIAJE").
2. El nivel de riesgo ("ALTO", "MEDIO", "BAJO").
3. La probabilidad matemática (ej: 0.93) y la temperatura estimada.
4. Las acciones recomendadas (ej: "Cubrir cultivos").
5. Los factores que provocaron la alerta.

---

## PARTE 2: Funcionamiento Técnico (Paso a Paso)

Si miramos el motor técnico (la cadena de montaje), el backend funciona exactamente en esta secuencia de 5 pasos en milisegundos:

### 1. El Encendido (La Preparación)
Cuando se ejecuta `uvicorn app:app`, se dispara un evento llamado *Lifespan*. En ese instante, `data_loader.py` lee los pesados archivos CSV del disco duro y los **guarda en la Memoria RAM**. Esto garantiza que las consultas futuras sean instantáneas. Tras esto, el servidor se queda en espera en el puerto 8000.

### 2. El Disparo (La Petición)
El Frontend (React) o el usuario envía un paquete de datos a través de internet (un JSON) hacia la ruta de entrada `POST /predict`.

### 3. El Guardia de Seguridad (Validación)
El archivo `schemas.py` (usando Pydantic) intercepta el paquete en la puerta. Revisa rigurosamente que los datos sean válidos (ej: que no envíen letras en lugar de fechas). Si el JSON es erróneo, lo rechaza instantáneamente con un Error 422; si es correcto, lo deja pasar.

### 4. La Cadena de Montaje (El Orquestador)
Adentro de la aplicación, el archivo `routes.py` toma el control y orquesta a los demás:
1. Pide a `data_loader` los datos alojados en la RAM.
2. Pide a `feature_engineering` que limpie la data y construya el vector matemático.
3. Llama a `predict_service` para inyectar el vector en el modelo del Integrante 1 (`ml/predict.py`).

### 5. El Empaquetado (La Salida)
El modelo de Inteligencia Artificial (XGBoost) devuelve su cálculo predictivo. `routes.py` recibe ese cálculo, busca las recomendaciones médicas/agrícolas aplicables, arma un nuevo paquete JSON completamente limpio y se lo dispara de regreso al Frontend.
