"""
Utilidades para logging del pipeline.
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logger(log_dir: str = "./logs", log_name: str = "pipeline.log") -> logging.Logger:
    """
    Configura y retorna un logger para el pipeline.

    Args:
        log_dir: Directorio donde guardar los logs
        log_name: Nombre del archivo de log

    Returns:
        Objeto Logger configurado
    """
    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Crear logger
    logger = logging.getLogger("PhotoCropPipeline")
    logger.setLevel(logging.DEBUG)

    # Evitar duplicación de handlers
    if logger.handlers:
        return logger

    # Handler para archivo
    log_file = log_path / log_name
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

