# Sistema Inteligente de Alerta Temprana para Heladas y Friajes

## Objetivo

Desarrollar un MVP para el InnovaHack que permita transformar datos meteorológicos en alertas tempranas para la toma de decisiones.

El sistema debe ser capaz de:

- Predecir eventos de helada y friaje.
- Comunicar el riesgo de forma clara.
- Generar alertas fáciles de interpretar.
- Proporcionar recomendaciones para reducir el impacto del evento.

El objetivo es construir un MVP funcional, no un sistema de producción.

---

# Filosofía del proyecto

La IA NO es el producto.

El producto es un sistema de apoyo a la toma de decisiones.

La inteligencia artificial únicamente genera la predicción; el verdadero valor consiste en transformar esa predicción en información útil para el usuario.

Flujo del sistema:

```
Datos SENAMHI
        │
        ▼
Feature Engineering
        │
        ▼
Modelo XGBoost
        │
        ▼
Predicción
        │
        ▼
Clasificación del riesgo
        │
        ▼
Generación de alerta
        │
        ▼
Recomendaciones
```

---

# Objetivos del MVP

## Funcionalidades principales

- Predicción de heladas.
- Predicción de friajes.
- Mostrar nivel de riesgo.
- Mostrar probabilidad de ocurrencia.
- Mostrar explicación de la predicción.
- Mostrar recomendaciones.

## Funcionalidades fuera del alcance

No forman parte del MVP:

- Login
- Autenticación
- Docker
- Kubernetes
- Microservicios
- Base de datos
- SMS reales
- WhatsApp
- Notificaciones Push

---

# Arquitectura

```
                Frontend (React)
                        │
                 HTTP / REST API
                        │
                Backend (FastAPI)
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
 Datos SENAMHI                  Modelo XGBoost
(estaciones.csv)               (model.joblib)
(mediciones.csv)
         │
         ▼
 Feature Engineering
```

---

# Organización del equipo

Somos un equipo de tres personas.

Cada integrante debe trabajar de manera independiente.

Las responsabilidades deben mantenerse desacopladas.

---

# Integrante 1 — Machine Learning

## Responsabilidad

Construir el modelo de predicción.

## Tareas

- Analizar el dataset.
- Limpiar datos.
- Seleccionar variables.
- Realizar Feature Engineering.
- Entrenar XGBoost.
- Validar el modelo.
- Exportar el modelo.

## Entregables

```
model.joblib
predict.py
```

El archivo `predict.py` debe exponer una función:

```python
predict(features)
```

donde `features` corresponde al vector de características construido por el backend.

Debe retornar:

```json
{
    "tipo": "HELADA",
    "riesgo": "ALTO",
    "probabilidad": 0.93,
    "temperatura_estimada": -4.1,
    "factores": [
        "Temperatura mínima muy baja",
        "Altitud elevada"
    ]
}
```

El backend NO debe conocer cómo funciona internamente el modelo.

---

# Integrante 2 — Backend

## Responsabilidad

Construir toda la API REST y preparar la información para el modelo.

## Tareas

- Cargar el modelo.
- Leer los datasets del SENAMHI.
- Construir el vector de características.
- Ejecutar la predicción.
- Generar recomendaciones.
- Exponer endpoints REST.

El backend es el único responsable de acceder a los datos meteorológicos.

Framework:

```
FastAPI
```

---

# Integrante 3 — Frontend

## Responsabilidad

Construir toda la interfaz de usuario.

## Tareas

- Consumir la API.
- Mostrar la predicción.
- Mostrar nivel de riesgo.
- Mostrar recomendaciones.
- Mostrar alertas.
- Diseñar el dashboard.

El frontend NO conoce detalles del modelo ni de los datasets.

Framework:

```
React
```

---

# Flujo de datos

```
Usuario

↓

Selecciona estación

↓

Frontend

↓

POST /predict

↓

Backend

↓

Carga datos SENAMHI

↓

Feature Engineering

↓

Modelo XGBoost

↓

Resultado

↓

Frontend

↓

Visualización
```

---

# Contrato IA ↔ Backend

El backend debe construir exactamente el conjunto de variables que el modelo espera.

Ejemplo:

```
temperatura_inst
temperatura_max
temperatura_min
humedad_inst
precipitacion_hora
precipitacion_dia
altitud
latitud
longitud
hora
mes
```

El modelo recibe únicamente estas variables.

---

# Contrato Backend ↔ Frontend

Estos contratos deben permanecer estables durante el desarrollo.

## POST /predict

Entrada

```json
{
    "estacion": "Imata",
    "fecha": "2026-07-15T00:00:00"
}
```

La fecha es opcional.

Si no se envía, el backend utilizará la medición más reciente.

---

Respuesta

```json
{
    "estacion": "Imata",
    "tipo": "HELADA",
    "riesgo": "ALTO",
    "probabilidad": 0.93,
    "temperatura_estimada": -4.2,
    "hora_critica": "04:00",
    "factores": [
        "Temperatura mínima muy baja",
        "Altitud elevada"
    ]
}
```

---

## GET /recommendation/{tipo}

Ejemplo

```
GET /recommendation/HELADA
```

Respuesta

```json
{
    "titulo": "Acciones recomendadas",
    "acciones": [
        "Cubrir cultivos",
        "Resguardar ganado",
        "Informar a la comunidad"
    ]
}
```

---

## GET /health

Respuesta

```json
{
    "status": "ok"
}
```

---

# Prioridades del proyecto

## Esencial para el MVP

- Modelo de predicción.
- API REST.
- Dashboard.
- Mostrar riesgo.
- Mostrar probabilidad.
- Mostrar alerta.

---

## Alta prioridad

- Recomendaciones.
- Explicación de la predicción.
- Indicadores visuales de riesgo.

---

## Media prioridad

- Mapa de estaciones.
- Historial de predicciones.

---

## Baja prioridad

- Exportar reportes.
- Configuración de usuario.

---

## Fuera del alcance

- Login.
- Base de datos.
- SMS reales.
- WhatsApp.
- Docker.
- Kubernetes.

---

# Estructura del repositorio

```
project/

│

├── backend/
│   ├── app.py
│   ├── routes.py
│   ├── predict_service.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── recommendation_service.py
│   ├── model.joblib
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── services/
│       └── api.ts
│
├── ml/
│   ├── train.py
│   ├── predict.py
│   ├── notebooks/
│   ├── dataset/
│   └── model.joblib
│
└── README.md
```

---

# Objetivos 

debe:

1. Diseñar la arquitectura completa.
2. Generar un plan de trabajo paralelo para tres desarrolladores.
3. Mantener el desacoplamiento entre IA, Backend y Frontend.
4. Respetar los contratos definidos.
5. Proponer una estructura limpia del repositorio.
6. Detectar posibles riesgos de integración.
7. Priorizar terminar un MVP completamente funcional antes de agregar funcionalidades adicionales.
8. Proponer tareas que puedan desarrollarse simultáneamente.
9. Evitar dependencias innecesarias entre los integrantes.

La prioridad absoluta es obtener un MVP estable, demostrable y fácil de presentar durante el hackatón.