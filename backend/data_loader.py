import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

from exceptions import DatasetNotFound, StationNotFound

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.estaciones_df: Optional[pd.DataFrame] = None
        self.mediciones_df: Optional[pd.DataFrame] = None
        # Los archivos vivirán en el mismo directorio (backend/)
        self.base_dir = Path(__file__).parent

    def load_datasets(self):
        """Carga los CSV en memoria una única vez (Patrón Singleton)."""
        estaciones_path = self.base_dir / "estaciones.csv"
        mediciones_path = self.base_dir / "mediciones.csv"

        if not estaciones_path.exists() or not mediciones_path.exists():
            logger.error("No se encontraron los archivos CSV en el directorio del backend.")
            raise DatasetNotFound("No se encontraron los archivos CSV (estaciones.csv o mediciones.csv).")

        logger.info("Cargando datasets en memoria...")
        self.estaciones_df = pd.read_csv(estaciones_path)
        self.mediciones_df = pd.read_csv(mediciones_path)
        
        # Asegurarnos de que las fechas sean objetos datetime de pandas para búsquedas correctas
        if 'fecha' in self.mediciones_df.columns:
            self.mediciones_df['fecha'] = pd.to_datetime(self.mediciones_df['fecha'])

        logger.info("Datasets cargados exitosamente.")

    def get_estacion(self, nombre: str) -> pd.Series:
        """Busca una estación por nombre y devuelve sus datos."""
        if self.estaciones_df is None:
            raise DatasetNotFound("Los datasets no han sido cargados (estaciones).")
            
        estacion = self.estaciones_df[self.estaciones_df['estacion'] == nombre]
        if estacion.empty:
            raise StationNotFound(f"La estación '{nombre}' no existe en el registro.")
            
        return estacion.iloc[0]

    def get_medicion(self, estacion_nombre: str, fecha_buscada: Optional[datetime] = None) -> pd.Series:
        """
        Devuelve la medición de una estación. 
        Si hay fecha, devuelve la exacta o la más cercana anterior.
        Si no hay fecha, devuelve la más reciente.
        """
        if self.mediciones_df is None:
            raise DatasetNotFound("Los datasets no han sido cargados (mediciones).")
            
        mediciones = self.mediciones_df[self.mediciones_df['estacion'] == estacion_nombre]
        if mediciones.empty:
            raise StationNotFound(f"No hay mediciones para la estación '{estacion_nombre}'.")

        # Filtramos por fecha si nos envían una
        if fecha_buscada:
            mediciones = mediciones[mediciones['fecha'] <= pd.to_datetime(fecha_buscada)]
            if mediciones.empty:
                raise StationNotFound(f"No hay mediciones válidas para '{estacion_nombre}' antes de esa fecha.")

        # Ordenar de la más nueva a la más antigua y obtener la primera
        mediciones = mediciones.sort_values(by='fecha', ascending=False)
        return mediciones.iloc[0]

# Instancia global para ser importada por toda la aplicación
data_loader_instance = DataLoader()
