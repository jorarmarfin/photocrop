"""
Procesador de imágenes usando Pillow.
Maneja lectura, validación y manipulación básica de imágenes.
"""

from PIL import Image
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


class ImageProcessor:
    """Procesador de imágenes con Pillow."""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    def __init__(self):
        pass

    @staticmethod
    def is_valid_image_file(filepath: Path) -> bool:
        """Verifica si el archivo tiene una extensión de imagen válida."""
        return filepath.suffix.lower() in ImageProcessor.VALID_EXTENSIONS

    @staticmethod
    def load_image(filepath: Path) -> Optional[Image.Image]:
        """
        Carga una imagen desde el disco.

        Args:
            filepath: Ruta al archivo de imagen

        Returns:
            Objeto Image de PIL o None si hay error
        """
        try:
            img = Image.open(filepath)
            # Verificar que la imagen sea válida cargando sus datos
            img.verify()
            # Reabrir después de verify()
            img = Image.open(filepath)
            return img
        except Exception as e:
            return None

    @staticmethod
    def get_image_info(img: Image.Image) -> dict:
        """
        Obtiene información básica de la imagen.

        Args:
            img: Objeto Image de PIL

        Returns:
            Diccionario con width, height, format
        """
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format if img.format else "UNKNOWN"
        }

    @staticmethod
    def image_to_array(img: Image.Image) -> np.ndarray:
        """
        Convierte una imagen PIL a array numpy.

        Args:
            img: Objeto Image de PIL

        Returns:
            Array numpy en formato RGB
        """
        # Convertir a RGB si no lo está
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return np.array(img)

    @staticmethod
    def crop_image(img: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
        """
        Recorta una imagen según coordenadas.

        Args:
            img: Objeto Image de PIL
            box: Tupla (x, y, width, height)

        Returns:
            Imagen recortada
        """
        x, y, width, height = box
        # PIL crop usa (left, upper, right, lower)
        crop_box = (x, y, x + width, y + height)
        return img.crop(crop_box)

    @staticmethod
    def resize_image(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Redimensiona una imagen.

        Args:
            img: Objeto Image de PIL
            size: Tupla (width, height)

        Returns:
            Imagen redimensionada
        """
        return img.resize(size, Image.Resampling.LANCZOS)

    @staticmethod
    def save_image(img: Image.Image, filepath: Path, quality: int = 95) -> bool:
        """
        Guarda una imagen en el disco.

        Args:
            img: Objeto Image de PIL
            filepath: Ruta donde guardar
            quality: Calidad para JPEG (1-100)

        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Configurar opciones según formato
            save_kwargs = {}
            if filepath.suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True

            img.save(filepath, **save_kwargs)
            return True
        except Exception as e:
            return False

    @staticmethod
    def calculate_crop_box_with_margin(
        face_box: Tuple[int, int, int, int],
        img_width: int,
        img_height: int,
        target_ratio: float = 3/4,  # ratio estándar de foto tipo carnet
        margin_factor: float = 1.5
    ) -> Tuple[int, int, int, int]:
        """
        Calcula un box de recorte alrededor de un rostro con margen.

        Args:
            face_box: (x, y, width, height) del rostro
            img_width: Ancho de la imagen
            img_height: Alto de la imagen
            target_ratio: Relación width/height deseada
            margin_factor: Factor de margen (1.5 = 50% más espacio)

        Returns:
            Tupla (x, y, width, height) del área a recortar
        """
        face_x, face_y, face_w, face_h = face_box

        # Calcular centro del rostro
        center_x = face_x + face_w / 2
        center_y = face_y + face_h / 2

        # Calcular dimensiones con margen
        crop_height = face_h * margin_factor * 2  # Espacio arriba y abajo
        crop_width = crop_height * target_ratio

        # Centrar el recorte
        crop_x = max(0, int(center_x - crop_width / 2))
        crop_y = max(0, int(center_y - crop_height / 2.5))  # Rostro más hacia arriba

        # Ajustar si se sale de los límites
        if crop_x + crop_width > img_width:
            crop_x = img_width - crop_width
        if crop_y + crop_height > img_height:
            crop_y = img_height - crop_height

        # Asegurar que no sean negativos
        crop_x = max(0, crop_x)
        crop_y = max(0, crop_y)
        crop_width = min(crop_width, img_width - crop_x)
        crop_height = min(crop_height, img_height - crop_y)

        return (int(crop_x), int(crop_y), int(crop_width), int(crop_height))

