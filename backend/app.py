import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import router as api_router
from data_loader import data_loader_instance
from exceptions import (
    BaseAppException, 
    DatasetNotFound, 
    StationNotFound, 
    InvalidFeatureError, 
    ModelNotLoaded, 
    PredictionError
)

# Configuración básica de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Gestión del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de Startup: Cargar CSVs en memoria una sola vez
    logger.info("Iniciando aplicación: Cargando datasets estáticos...")
    try:
        data_loader_instance.load_datasets()
    except Exception as e:
        logger.error(f"Error crítico al arrancar la aplicación: {e}")
        # En un MVP dejamos que inicie para que los endpoints arrojen 500 y den contexto.
    
    yield
    
    # Lógica de Shutdown: Limpiar memoria
    logger.info("Apagando aplicación: Liberando recursos...")
    data_loader_instance.estaciones_df = None
    data_loader_instance.mediciones_df = None

# Instancia principal de FastAPI
app = FastAPI(
    title="API de Alerta Temprana - InnovaHack",
    description="Backend orquestador para predicción de Heladas y Friajes",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de Seguridad: CORS (Permite que el Frontend acceda sin bloqueos)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para MVP permitimos todo. En PROD se debe restringir a los dominios exactos.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de rutas (endpoints)
app.include_router(api_router)

# ---------------------------------------------------------
# Manejadores Globales de Excepciones (Exception Handlers)
# ---------------------------------------------------------

@app.exception_handler(StationNotFound)
async def station_not_found_handler(request: Request, exc: StationNotFound):
    return JSONResponse(status_code=404, content={"error": "Estación no encontrada", "detail": str(exc)})

@app.exception_handler(DatasetNotFound)
async def dataset_not_found_handler(request: Request, exc: DatasetNotFound):
    return JSONResponse(status_code=500, content={"error": "Fallo en los datos", "detail": str(exc)})

@app.exception_handler(InvalidFeatureError)
async def invalid_feature_handler(request: Request, exc: InvalidFeatureError):
    return JSONResponse(status_code=400, content={"error": "Vector de características inválido", "detail": str(exc)})

@app.exception_handler(ModelNotLoaded)
@app.exception_handler(PredictionError)
async def ml_error_handler(request: Request, exc: BaseAppException):
    return JSONResponse(status_code=500, content={"error": "Fallo en el Modelo ML", "detail": str(exc)})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error inesperado y no controlado: {exc}")
    return JSONResponse(status_code=500, content={"error": "Error Interno del Servidor", "detail": "Revisa los logs de la consola."})
