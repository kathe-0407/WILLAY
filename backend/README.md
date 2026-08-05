# Backend - Sistema Inteligente de Alerta Temprana

API REST (MVP) construida con FastAPI para predecir Heladas y Friajes basándose en datos del SENAMHI. Este módulo orquesta la carga de datos meteorológicos, la transformación de características (Feature Engineering) y la conexión de forma desacoplada con el modelo de Machine Learning.

## Requisitos Previos

- Python 3.10 o superior.
- Estructura esperada de datos dentro de esta carpeta `backend/`:
  - `estaciones.csv` (Datos del SENAMHI)
  - `mediciones.csv` (Datos del SENAMHI)
- Para que la IA real funcione, la carpeta vecina `../ml/` debe existir y contener la función `predict.py`. Si no existe, el servidor utilizará una predicción simulada (Mock) para no bloquear el desarrollo del Frontend.

## Instalación

1. Abre tu terminal y asegúrate de estar dentro del directorio `backend/`.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución del Servidor

Inicia la aplicación utilizando Uvicorn:

```bash
uvicorn app:app --reload
```
La API estará disponible localmente en `http://localhost:8000`.

## Documentación Interactiva

FastAPI genera documentación automática donde puedes probar los endpoints sin necesidad de Postman. Una vez encendido el servidor, visita:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Endpoints Principales

### 1. Predecir Evento
- **URL:** `POST /predict`
- **Body JSON de Entrada:**
  ```json
  {
      "estacion": "Imata",
      "fecha": "2026-07-15T00:00:00"
  }
  ```
  *(Nota: La fecha es opcional, si no se envía se busca la medición más reciente).*
- **Respuesta Exitosa (Contrato):**
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

### 2. Obtener Recomendaciones
- **URL:** `GET /recommendation/{tipo}` (Ej: `/recommendation/HELADA`)
- **Respuesta Exitosa:**
  ```json
  {
      "titulo": "Acciones recomendadas",
      "acciones": [
          "Cubrir cultivos y proteger sistemas de riego",
          "Resguardar ganado en cobertizos",
          "Informar a la comunidad local",
          "Preparar suministros de emergencia"
      ]
  }
  ```

### 3. Health Check
- **URL:** `GET /health`
- **Respuesta Exitosa:** `{"status": "ok"}`

---

## Estructura de Archivos

Diseñado bajo principios de Single Responsibility:

- `app.py`: Punto de entrada (Configura FastAPI, CORS, y el manejo de excepciones de dominio).
- `routes.py`: Orquestador de peticiones HTTP.
- `schemas.py`: Modelos Pydantic que garantizan de forma estricta los contratos JSON.
- `data_loader.py`: Singleton que carga CSVs usando Pandas y los expone desde la memoria RAM.
- `feature_engineering.py`: Transforma los CSV crudos en el diccionario (vector) que exige la IA.
- `predict_service.py`: Puente de conexión seguro con el script del Integrante 1.
- `recommendation_service.py`: Base estática para los planes de contingencia por clima.
- `exceptions.py`: Errores controlados (`StationNotFound`, etc.) para devolver respuestas HTTP claras.
