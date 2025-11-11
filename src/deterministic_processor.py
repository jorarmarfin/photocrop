"""
Implementación del flujo completo de procesamiento según especificación.
Este módulo implementa el flujo determinista definido en docs/FLUJO_PROCESAMIENTO.md
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from PIL import Image
import numpy as np

from src.core.metadata_manager import MetadataManager
from src.core.face_detector import FaceDetector
from src.core.image_processor import ImageProcessor
from src.utils.logger import setup_logger
from src.utils.file_utils import load_paths_config, ensure_directory


class ProcessedIndexManager:
    """Gestiona el archivo processed_index.json"""

    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.data = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Carga el índice de procesados desde disco."""
        if not self.index_path.exists():
            return {
                "processed_files": [],
                "last_updated": None,
                "total_processed": 0,
                "metadata_version": "1.0",
                "statistics": {
                    "total_processed": 0,
                    "successful": 0,
                    "manual_review": 0,
                    "errors": 0
                }
            }

        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def is_processed(self, filename: str) -> bool:
        """Verifica si un archivo ya fue procesado."""
        return filename in self.data["processed_files"]

    def add_processed(self, filename: str, status: str):
        """Agrega un archivo al índice de procesados."""
        if filename not in self.data["processed_files"]:
            self.data["processed_files"].append(filename)
            self.data["total_processed"] += 1
            self.data["statistics"]["total_processed"] += 1

            # Incrementar estadística específica
            if status == "processed":
                self.data["statistics"]["successful"] += 1
            elif status == "manual_review":
                self.data["statistics"]["manual_review"] += 1
            elif status == "error":
                self.data["statistics"]["errors"] += 1

    def save(self):
        """Guarda el índice actualizado."""
        self.data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)


class CropDecisionEngine:
    """Motor de decisión de recorte según especificación."""

    @staticmethod
    def calculate_crop_decision(
        width: int,
        height: int,
        face_box: List[int],
        orientation: str
    ) -> Dict[str, Any]:
        """
        Calcula si una imagen puede ser recortada correctamente.
        Incluye espacio adicional arriba para el cabello.

        Args:
            width: Ancho de la imagen
            height: Alto de la imagen
            face_box: [x, y, w, h] del rostro detectado
            orientation: portrait/landscape/square

        Returns:
            Dict con status ("OK" o "MANUAL_REVIEW"), crop_box y reason
        """
        x, y, w, h = face_box
        face_center_x = x + w / 2
        face_center_y = y + h / 2

        # Estimar posición del cabello (arriba del rostro)
        # El rostro detectado por dlib va desde la frente hasta el mentón
        # Agregamos 80% extra arriba para el cabello + margen superior generoso
        hair_margin = h * 0.8  # Aumentado de 0.6 a 0.8 para más espacio
        estimated_top = y - hair_margin

        # Calcular crop_box para formato pasaporte (3:4)
        target_aspect = 3 / 4

        # Dimensiones ideales basadas en el rostro
        # Factor 2.5 da mejor espacio lateral (aumentado de 2.4)
        ideal_crop_width = w * 2.5
        ideal_crop_height = ideal_crop_width / target_aspect

        # Intentar centrado horizontal perfecto
        crop_x = face_center_x - ideal_crop_width / 2

        # Posición vertical: comenzar desde el estimado del cabello
        # Dejamos un margen más generoso (20px) arriba del cabello estimado
        crop_y = estimated_top - 20  # Aumentado de 10 a 20 para más "respiro"

        # AJUSTES POR LÍMITES DE IMAGEN
        # Si el recorte es más grande que la imagen, ajustar proporcionalmente
        if ideal_crop_width > width:
            ideal_crop_width = width
            ideal_crop_height = ideal_crop_width / target_aspect

        if ideal_crop_height > height:
            ideal_crop_height = height
            ideal_crop_width = ideal_crop_height * target_aspect

        crop_width = ideal_crop_width
        crop_height = ideal_crop_height

        # Ajustar horizontalmente si se sale
        if crop_x < 0:
            crop_x = 0
        if crop_x + crop_width > width:
            crop_x = width - crop_width

        # Ajustar verticalmente si se sale
        if crop_y < 0:
            crop_y = 0
        if crop_y + crop_height > height:
            crop_y = height - crop_height

        # Verificar que el rostro quede dentro del crop
        face_right = x + w
        face_bottom = y + h
        crop_right = crop_x + crop_width
        crop_bottom = crop_y + crop_height

        # Si el rostro no cabe completamente en el crop, enviar a manual
        if x < crop_x or face_right > crop_right or y < crop_y or face_bottom > crop_bottom:
            return {
                "status": "MANUAL_REVIEW",
                "crop_box": None,
                "reason": "El rostro no cabe completamente en el recorte calculado"
            }

        # Verificación final de límites
        if crop_x < 0 or crop_y < 0 or crop_x + crop_width > width or crop_y + crop_height > height:
            return {
                "status": "MANUAL_REVIEW",
                "crop_box": None,
                "reason": "Las dimensiones del recorte exceden los límites de la imagen"
            }

        crop_box = [
            int(crop_x),
            int(crop_y),
            int(crop_x + crop_width),
            int(crop_y + crop_height)
        ]

        return {
            "status": "OK",
            "crop_box": crop_box,
            "reason": None
        }


class DeterministicPhotoProcessor:
    """
    Procesador de fotos con flujo determinista.
    Implementa el flujo completo según especificación en docs/FLUJO_PROCESAMIENTO.md
    """

    VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    MIN_FILE_SIZE = 1024  # 1KB mínimo

    def __init__(self, config_path: str = "./config/paths.json"):
        """Inicializa el procesador."""
        # 1. INICIALIZACIÓN
        self.logger = setup_logger()
        self.logger.info("=" * 80)
        self.logger.info("INICIO DE PROCESADOR DETERMINISTA")
        self.logger.info("=" * 80)

        # Cargar configuración
        self.paths = load_paths_config(config_path)
        self.logger.info(f"Configuración cargada desde: {config_path}")

        # Verificar carpetas necesarias
        self._ensure_directories()

        # Inicializar componentes
        self.metadata_manager = MetadataManager(self.paths["metadata"])
        self.face_detector = FaceDetector()
        self.image_processor = ImageProcessor()
        self.processed_index = ProcessedIndexManager(self.paths["processed_index"])
        self.crop_engine = CropDecisionEngine()

        # Estadísticas
        self.stats = {
            "total": 0,
            "skipped": 0,
            "processed": 0,
            "manual_review": 0,
            "errors": 0
        }

        self.logger.info("Inicialización completada")

    def _ensure_directories(self):
        """Verifica existencia de carpetas necesarias."""
        required_dirs = [
            "input_raw", "output", "metadata", "errors",
            "manual_review", "logs", "working", "prepared"
        ]
        for dir_key in required_dirs:
            if dir_key in self.paths:
                ensure_directory(self.paths[dir_key])

    def run(self, batch_id: Optional[str] = None, auto_clean: bool = False):
        """
        Ejecuta el flujo completo de procesamiento.

        Args:
            batch_id: Identificador del lote (opcional)
            auto_clean: Si True, elimina archivos procesados exitosamente de input_raw
        """
        # 2. ESCANEO DE ENTRADA
        self.logger.info("\n" + "=" * 80)
        self.logger.info("2. ESCANEO DE ENTRADA")
        self.logger.info("=" * 80)

        input_dir = Path(self.paths["input_raw"])
        all_files = self._scan_input_directory(input_dir)

        if not all_files:
            self.logger.warning(f"No se encontraron imágenes en {input_dir}")
            return self.stats

        self.logger.info(f"Total de archivos encontrados: {len(all_files)}")

        # 3. FILTRADO DE ARCHIVOS NUEVOS
        self.logger.info("\n" + "=" * 80)
        self.logger.info("3. FILTRADO DE ARCHIVOS NUEVOS")
        self.logger.info("=" * 80)

        new_files = self._filter_new_files(all_files)

        if not new_files:
            self.logger.info("No hay archivos nuevos para procesar")
            return self.stats

        self.logger.info(f"Archivos nuevos a procesar: {len(new_files)}")

        # 4. PROCESAMIENTO DE ARCHIVOS NUEVOS
        self.logger.info("\n" + "=" * 80)
        self.logger.info("4. PROCESAMIENTO DE ARCHIVOS NUEVOS")
        self.logger.info("=" * 80)

        for img_path in new_files:
            self._process_single_file(img_path, batch_id)

        # 6. LIMPIEZA OPCIONAL
        if auto_clean:
            self._cleanup_processed_files(input_dir)

        # 7. RESUMEN FINAL
        self._print_summary()

        return self.stats

    def _scan_input_directory(self, input_dir: Path) -> List[Path]:
        """
        Escanea el directorio de entrada y retorna lista de archivos válidos.

        Returns:
            Lista de Path con archivos válidos
        """
        all_files = []

        # Listar solo archivos en el nivel raíz (sin subdirectorios)
        for item in input_dir.iterdir():
            if not item.is_file():
                continue

            # Excluir archivos ocultos
            if item.name.startswith('.'):
                continue

            # Filtrar por extensión
            if item.suffix.lower() not in self.VALID_EXTENSIONS:
                continue

            # Verificar tamaño mínimo
            if item.stat().st_size < self.MIN_FILE_SIZE:
                self.logger.warning(f"Archivo muy pequeño, ignorando: {item.name}")
                continue

            all_files.append(item)

        return all_files

    def _filter_new_files(self, all_files: List[Path]) -> List[Path]:
        """
        Filtra archivos que ya fueron procesados.

        Returns:
            Lista de archivos nuevos (no procesados)
        """
        new_files = []

        for file_path in all_files:
            self.stats["total"] += 1

            if self.processed_index.is_processed(file_path.name):
                self.logger.info(f"✓ Ya procesado, saltando: {file_path.name}")
                self.stats["skipped"] += 1
                continue

            new_files.append(file_path)

        return new_files

    def _process_single_file(self, img_path: Path, batch_id: Optional[str]):
        """
        Procesa un único archivo según el flujo especificado.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"Procesando: {img_path.name}")
        self.logger.info("=" * 60)

        # Determinar batch_id
        if batch_id is None:
            batch_id = self._extract_batch_id(img_path)

        try:
            # 4.1 VALIDACIÓN BÁSICA
            metadata = self._validate_and_create_metadata(img_path, batch_id)
            if metadata is None:
                return  # Error manejado en la función

            # 4.3 DETECCIÓN FACIAL
            detection_result = self._detect_faces(img_path, metadata)

            if detection_result is None:
                return  # Error manejado

            num_faces, faces, img = detection_result

            # 4.4 y 4.5 PROCESAMIENTO SEGÚN RESULTADO
            if num_faces == 0:
                self._handle_no_face(img_path, metadata, batch_id)
            elif num_faces == 1:
                face_box = self._face_to_box(faces[0])
                self._handle_single_face(img_path, img, metadata, batch_id, face_box)
            else:
                largest_face = self.face_detector.get_largest_face(faces)
                face_box = self._face_to_box(largest_face)
                self._handle_multiple_faces(img_path, metadata, batch_id, num_faces, face_box)

        except Exception as e:
            self.logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            self._handle_error(img_path, batch_id, f"Error inesperado: {str(e)}")

    def _validate_and_create_metadata(
        self,
        img_path: Path,
        batch_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        4.1 VALIDACIÓN BÁSICA y 4.2 CREACIÓN DE METADATO INICIAL
        """
        self.logger.info("4.1 Validación básica...")

        try:
            # Intentar abrir imagen
            img = Image.open(img_path)
            width, height = img.size
            img_format = img.format

            if width == 0 or height == 0:
                raise ValueError("Dimensiones inválidas")

            self.logger.info(f"  Dimensiones: {width}x{height}")
            self.logger.info(f"  Formato: {img_format}")

            # 4.2 CREACIÓN DE METADATO INICIAL
            self.logger.info("4.2 Creando metadato inicial...")
            metadata = self.metadata_manager.create_metadata(
                filename=img_path.name,
                input_path=str(img_path),
                batch_id=batch_id,
                width=width,
                height=height,
                img_format=img_format
            )

            self.logger.info(f"  Orientación: {metadata['orientation']}")

            # Guardar metadato inicial
            self.metadata_manager.save_metadata(metadata, batch_id)

            return metadata

        except Exception as e:
            error_msg = f"PIL error: {str(e)}"
            self.logger.error(f"Error al cargar imagen: {error_msg}")
            self._handle_error(img_path, batch_id, error_msg)
            return None

    def _detect_faces(
        self,
        img_path: Path,
        metadata: Dict[str, Any]
    ) -> Optional[Tuple[int, List, Image.Image]]:
        """
        4.3 DETECCIÓN FACIAL
        """
        self.logger.info("4.3 Detección facial con dlib...")

        try:
            img = Image.open(img_path)
            img_array = np.array(img.convert('RGB'))
            faces = self.face_detector.detect_faces(img_array)
            num_faces = len(faces)

            self.logger.info(f"  Rostros detectados: {num_faces}")

            return num_faces, faces, img

        except Exception as e:
            error_msg = f"dlib error: {str(e)}"
            self.logger.error(f"Error en detección facial: {error_msg}")
            self._handle_error(img_path, metadata["batch_id"], error_msg)
            return None

    def _face_to_box(self, face) -> List[int]:
        """Convierte face de dlib a [x, y, w, h]"""
        # face ya viene como tupla (x, y, width, height) del FaceDetector
        if isinstance(face, tuple):
            return list(face)
        # Si es objeto dlib (fallback)
        return [face.left(), face.top(), face.width(), face.height()]

    def _handle_no_face(self, img_path: Path, metadata: Dict[str, Any], batch_id: str):
        """4.5.2 Manejo de imagen sin rostros"""
        self.logger.warning("  ⚠️  No se detectó ningún rostro")

        # Actualizar metadata
        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=False,
            num_faces=0,
            face_box=None,
            status="manual_review",
            action="sent_to_manual_review",
            details="No se detectó rostro en la imagen",
            notes="No se detectó rostro en la imagen"
        )

        # Mover a manual_review
        year = datetime.now().year
        dest_dir = Path(self.paths["manual_review"]) / str(year) / batch_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / img_path.name

        shutil.copy2(img_path, dest_path)

        metadata["current_path"] = str(dest_path)

        # Guardar metadata y registrar
        self.metadata_manager.save_metadata(metadata, batch_id)
        self.processed_index.add_processed(img_path.name, "manual_review")
        self.processed_index.save()
        self.stats["manual_review"] += 1

        self.logger.warning(f"  ⚠️  Imagen enviada a revisión manual → {dest_path}")

    def _handle_single_face(
        self,
        img_path: Path,
        img: Image.Image,
        metadata: Dict[str, Any],
        batch_id: str,
        face_box: List[int]
    ):
        """Manejo de imagen con un solo rostro"""
        self.logger.info("  ✓ Un rostro detectado")

        # Actualizar metadata con info facial
        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=True,
            num_faces=1,
            face_box=face_box
        )

        # 4.4 DECISIÓN DE RECORTE
        crop_decision = self.crop_engine.calculate_crop_decision(
            metadata["width"],
            metadata["height"],
            face_box,
            metadata["orientation"]
        )

        if crop_decision["status"] == "OK":
            # 4.5.1 PROCESAMIENTO EXITOSO
            self._process_successful_crop(img_path, img, metadata, batch_id, crop_decision["crop_box"])
        else:
            # 4.5.2 MANUAL REVIEW
            metadata["notes"] = crop_decision["reason"]
            self._send_to_manual_review(img_path, metadata, batch_id, crop_decision["reason"])

    def _handle_multiple_faces(
        self,
        img_path: Path,
        metadata: Dict[str, Any],
        batch_id: str,
        num_faces: int,
        largest_face_box: List[int]
    ):
        """Manejo de imagen con múltiples rostros"""
        self.logger.warning(f"  ⚠️  Detectados {num_faces} rostros")

        # Actualizar metadata
        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=True,
            num_faces=num_faces,
            face_box=largest_face_box,
            notes=f"Múltiples rostros detectados ({num_faces})"
        )

        # Enviar a manual review
        self._send_to_manual_review(
            img_path,
            metadata,
            batch_id,
            f"Múltiples rostros detectados ({num_faces})"
        )

    def _process_successful_crop(
        self,
        img_path: Path,
        img: Image.Image,
        metadata: Dict[str, Any],
        batch_id: str,
        crop_box: List[int]
    ):
        """4.5.1 Procesamiento exitoso con recorte"""
        self.logger.info("  ✓ Aplicando recorte...")

        # Aplicar recorte
        cropped_img = img.crop(crop_box)

        # Guardar en output
        output_dir = Path(self.paths["output"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / img_path.name

        # Guardar con alta calidad
        if img_path.suffix.lower() in ['.jpg', '.jpeg']:
            cropped_img.save(output_path, 'JPEG', quality=95)
        else:
            cropped_img.save(output_path)

        # Actualizar metadata
        metadata = self.metadata_manager.update_metadata(
            metadata,
            current_path=str(output_path),
            output_path=str(output_path),
            status="processed",
            action="face_detected_and_cropped",
            details="Recorte aplicado exitosamente"
        )

        # Guardar y registrar
        self.metadata_manager.save_metadata(metadata, batch_id)
        self.processed_index.add_processed(img_path.name, "processed")
        self.processed_index.save()
        self.stats["processed"] += 1

        self.logger.info(f"  ✓ Imagen procesada exitosamente → {output_path}")

    def _send_to_manual_review(
        self,
        img_path: Path,
        metadata: Dict[str, Any],
        batch_id: str,
        reason: str
    ):
        """Envía imagen a revisión manual"""
        year = datetime.now().year
        dest_dir = Path(self.paths["manual_review"]) / str(year) / batch_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / img_path.name

        shutil.copy2(img_path, dest_path)

        # Actualizar metadata
        metadata = self.metadata_manager.update_metadata(
            metadata,
            current_path=str(dest_path),
            status="manual_review",
            action="sent_to_manual_review",
            details=reason
        )

        # Guardar y registrar
        self.metadata_manager.save_metadata(metadata, batch_id)
        self.processed_index.add_processed(img_path.name, "manual_review")
        self.processed_index.save()
        self.stats["manual_review"] += 1

        self.logger.warning(f"  ⚠️  Imagen enviada a revisión manual → {dest_path}")

    def _handle_error(self, img_path: Path, batch_id: str, error_message: str):
        """4.6 Manejo de errores"""
        self.logger.error("  ✗ Error en procesamiento")

        # Mover a errors
        year = datetime.now().year
        error_dir = Path(self.paths["errors"]) / str(year) / batch_id
        error_dir.mkdir(parents=True, exist_ok=True)
        error_path = error_dir / img_path.name

        try:
            shutil.copy2(img_path, error_path)
        except Exception as e:
            self.logger.error(f"No se pudo mover archivo a errors: {e}")

        # Crear metadata de error
        metadata = self.metadata_manager.create_metadata(
            filename=img_path.name,
            input_path=str(img_path),
            batch_id=batch_id
        )

        metadata = self.metadata_manager.update_metadata(
            metadata,
            current_path=str(error_path),
            status="error",
            error_message=error_message,
            action="error_detected",
            details=error_message
        )

        # Guardar y registrar
        self.metadata_manager.save_metadata(metadata, batch_id)
        self.processed_index.add_processed(img_path.name, "error")
        self.processed_index.save()
        self.stats["errors"] += 1

        self.logger.error(f"  ✗ Imagen con error → {error_path}")

    def _extract_batch_id(self, img_path: Path) -> str:
        """Extrae o genera un batch_id desde la ruta del archivo"""
        # Por defecto usar fecha actual
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _cleanup_processed_files(self, input_dir: Path):
        """6. LIMPIEZA OPCIONAL de archivos procesados exitosamente"""
        self.logger.info("\n6. LIMPIEZA DE ARCHIVOS PROCESADOS")

        for file_path in input_dir.iterdir():
            if file_path.is_file() and self.processed_index.is_processed(file_path.name):
                try:
                    file_path.unlink()
                    self.logger.info(f"  Limpiado: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"  No se pudo eliminar {file_path.name}: {e}")

    def _print_summary(self):
        """7. RESUMEN FINAL"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("7. RESUMEN DE PROCESAMIENTO")
        self.logger.info("=" * 80)
        self.logger.info(f"Total encontrados: {self.stats['total']}")
        self.logger.info(f"Saltados (ya procesados): {self.stats['skipped']}")
        self.logger.info("Nuevos procesados:")
        self.logger.info(f"  ✓ Exitosos: {self.stats['processed']}")
        self.logger.info(f"  ⚠️  Revisión manual: {self.stats['manual_review']}")
        self.logger.info(f"  ✗ Errores: {self.stats['errors']}")
        self.logger.info("=" * 80)


def main():
    """Punto de entrada principal"""
    processor = DeterministicPhotoProcessor()
    stats = processor.run(batch_id="admission_2025_01", auto_clean=False)
    return stats


if __name__ == "__main__":
    main()

