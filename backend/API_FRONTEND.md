# Contratos de API para Frontend

Esta documentación es exclusiva para el Integrante 3 (Frontend). Define exactamente las rutas, parámetros y respuestas JSON que el Backend de Alerta Temprana expone para ser consumidos por el dashboard (React).

## URL Base
Todas las peticiones deben dirigirse al puerto donde corra FastAPI (por defecto localmente):
`http://localhost:8000`

---

## 1. Predicción de Heladas y Friajes

Este endpoint recibe la estación seleccionada por el usuario en el dashboard y devuelve la alerta, el nivel de riesgo y los factores determinantes.

- **Método:** `POST`
- **Ruta:** `/predict`
- **Headers:** `Content-Type: application/json`

### Request Body
```json
{
    "estacion": "Imata",
    "fecha": "2026-07-15T00:00:00" 
}
```
> **Nota de implementación:** El campo `fecha` es completamente opcional. Si el usuario en el Dashboard solo selecciona la estación en un menú desplegable, puedes enviar solo `"estacion": "Imata"` y el backend utilizará la última lectura en tiempo real.

### Response Body (200 OK)
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

## 2. Recomendaciones de Acción

Este endpoint devuelve un listado de acciones preventivas sugeridas según la alerta arrojada por la predicción. Resulta ideal para inyectarlo en un componente de "Recomendaciones" en el UI.

- **Método:** `GET`
- **Ruta:** `/recommendation/{tipo}`
*(Sustituir `{tipo}` con HELADA o FRIAJE)*

### Ejemplo de Llamada
`GET /recommendation/HELADA`

### Response Body (200 OK)
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

---

## 3. Estado del Servidor (Health Check)

Útil para comprobar si el backend está encendido, tal vez para mostrar una pantalla de carga o un indicador verde/rojo en el frontend.

- **Método:** `GET`
- **Ruta:** `/health`

### Response Body (200 OK)
```json
{
    "status": "ok"
}
```

---

## Manejo de Errores (Códigos HTTP)
El frontend debe estar preparado para capturar los siguientes códigos HTTP estandarizados devueltos por el backend:

- **200 OK:** La operación fue exitosa.
- **400 Bad Request:** Problemas procesando los datos meteorológicos (ej. una fila en el CSV de sensores está rota).
- **404 Not Found:** La estación que el frontend envió no se encontró en los registros (ej. enviar `"estacion": "Lima"`).
- **422 Unprocessable Entity:** El JSON enviado está mal formado (ej. enviaste `"estaciones"` en plural en vez de `"estacion"`).
- **500 Internal Server Error:** Falla crítica (ej. la IA falló o los CSV no están cargados en memoria).
