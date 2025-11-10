"""
Utilidades para gestión de archivos y rutas.
"""

import shutil
import json
from pathlib import Path
from typing import List, Dict, Any


def load_config(config_path: str = "./config/settings.yml") -> Dict[str, Any]:
    """
    Carga la configuración desde archivo YAML o JSON.

    Args:
        config_path: Ruta al archivo de configuración

    Returns:
        Diccionario con la configuración
    """
    config_file = Path(config_path)

    if config_file.suffix == '.json':
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif config_file.suffix in ['.yml', '.yaml']:
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            # Si no hay yaml, retornar config por defecto
            return {
                "standard_size": {"width": 300, "height": 400},
                "face_threshold": 0.5
            }
    else:
        return {}


def load_paths_config(config_path: str = "./config/paths.json") -> Dict[str, str]:
    """
    Carga configuración de rutas.

    Args:
        config_path: Ruta al archivo de configuración de paths

    Returns:
        Diccionario con las rutas configuradas
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("paths", {})
    except FileNotFoundError:
        # Retornar rutas por defecto
        return {
            "input_raw": "./input_raw",
            "metadata": "./metadata",
            "logs": "./logs",
            "errors": "./errors",
            "working": "./working",
            "prepared": "./prepared",
            "manual_review": "./manual_review"
        }


def list_images_in_directory(directory: Path, extensions: set = None) -> List[Path]:
    """
    Lista todas las imágenes en un directorio.

    Args:
        directory: Directorio a escanear
        extensions: Set de extensiones válidas

    Returns:
        Lista de rutas a archivos de imagen
    """
    if extensions is None:
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    images = []
    if directory.exists():
        for ext in extensions:
            images.extend(directory.rglob(f"*{ext}"))
            images.extend(directory.rglob(f"*{ext.upper()}"))

    return sorted(images)


def move_file(source: Path, destination: Path, create_dirs: bool = True) -> bool:
    """
    Mueve un archivo de un lugar a otro.

    Args:
        source: Ruta origen
        destination: Ruta destino
        create_dirs: Si crear directorios necesarios

    Returns:
        True si se movió correctamente
    """
    try:
        if create_dirs:
            destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        return True
    except Exception as e:
        return False


def copy_file(source: Path, destination: Path, create_dirs: bool = True) -> bool:
    """
    Copia un archivo de un lugar a otro.

    Args:
        source: Ruta origen
        destination: Ruta destino
        create_dirs: Si crear directorios necesarios

    Returns:
        True si se copió correctamente
    """
    try:
        if create_dirs:
            destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(destination))
        return True
    except Exception as e:
        return False


def ensure_directory(directory) -> None:
    """
    Asegura que un directorio existe, creándolo si es necesario.

    Args:
        directory: Ruta del directorio (Path o str)
    """
    if isinstance(directory, str):
        directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)


def get_batch_id_from_path(filepath: Path, input_base: Path) -> str:
    """
    Extrae el batch_id de la estructura de carpetas.

    Args:
        filepath: Ruta completa al archivo
        input_base: Ruta base de input_raw

    Returns:
        String con el batch_id (ej: "admission_01")
    """
    try:
        relative = filepath.relative_to(input_base)
        parts = relative.parts
        if len(parts) >= 2:
            # Estructura: year/batch/file.jpg
            year = parts[0]
            batch = parts[1]
            return f"{batch}"
        else:
            return "default_batch"
    except ValueError:
        return "default_batch"

