"""
Detector de rostros utilizando dlib.
"""

import dlib
from typing import List, Tuple, Optional
import numpy as np


class FaceDetector:
    """Detector de rostros usando dlib."""

    def __init__(self):
        """Inicializa el detector de rostros de dlib."""
        self.detector = dlib.get_frontal_face_detector()

    def detect_faces(self, image_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta rostros en una imagen.

        Args:
            image_array: Array numpy de la imagen (RGB)

        Returns:
            Lista de tuplas (x, y, width, height) para cada rostro detectado
        """
        # Convertir a escala de grises si es necesario
        if len(image_array.shape) == 3:
            # dlib espera RGB
            gray = image_array
        else:
            gray = image_array

        # Detectar rostros
        faces = self.detector(gray, 1)

        # Convertir a formato [x, y, width, height]
        face_boxes = []
        for face in faces:
            x = face.left()
            y = face.top()
            width = face.right() - face.left()
            height = face.bottom() - face.top()
            face_boxes.append((x, y, width, height))

        return face_boxes

    def get_largest_face(self, faces: List[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
        """
        Obtiene el rostro más grande de una lista.

        Args:
            faces: Lista de tuplas (x, y, width, height)

        Returns:
            Tupla (x, y, width, height) del rostro más grande o None
        """
        if not faces:
            return None

        # Calcular área de cada rostro
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        return largest_face

    def get_central_face(self, faces: List[Tuple[int, int, int, int]], image_width: int, image_height: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Obtiene el rostro más cercano al centro de la imagen.

        Args:
            faces: Lista de tuplas (x, y, width, height)
            image_width: Ancho de la imagen
            image_height: Alto de la imagen

        Returns:
            Tupla (x, y, width, height) del rostro más central o None
        """
        if not faces:
            return None

        center_x = image_width / 2
        center_y = image_height / 2

        # Calcular distancia al centro para cada rostro
        def distance_to_center(face):
            face_center_x = face[0] + face[2] / 2
            face_center_y = face[1] + face[3] / 2
            return ((face_center_x - center_x) ** 2 + (face_center_y - center_y) ** 2) ** 0.5

        central_face = min(faces, key=distance_to_center)
        return central_face

