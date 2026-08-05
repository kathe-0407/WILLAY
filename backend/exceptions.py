class BaseAppException(Exception):
    """Excepción base para la aplicación."""
    pass

class DatasetNotFound(BaseAppException):
    """Se lanza cuando no se encuentra un archivo CSV (estaciones o mediciones)."""
    pass

class StationNotFound(BaseAppException):
    """Se lanza cuando se solicita una estación que no existe en el dataset."""
    pass

class InvalidFeatureError(BaseAppException):
    """Se lanza cuando hay un problema al construir el vector de características."""
    pass

class ModelNotLoaded(BaseAppException):
    """Se lanza cuando el modelo de ML (joblib) no puede ser cargado o no existe."""
    pass

class PredictionError(BaseAppException):
    """Se lanza cuando el modelo falla al realizar la predicción."""
    pass
