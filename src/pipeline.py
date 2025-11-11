"""
Pipeline principal de procesamiento de fotos de postulantes.
Coordina todos los componentes del sistema.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.metadata_manager import MetadataManager
from src.core.face_detector import FaceDetector
from src.core.image_processor import ImageProcessor
from src.utils.logger import setup_logger
from src.utils.file_utils import (
    load_paths_config,
    list_images_in_directory,
    copy_file,
    ensure_directory,
    get_batch_id_from_path
)


class PhotoProcessingPipeline:
    """Pipeline principal de procesamiento de fotos."""

    def __init__(self, config_path: str = "./config/paths.json"):
        """Inicializa el pipeline."""
        self.logger = setup_logger()
        self.logger.info("Inicializando PhotoProcessingPipeline...")

        # Cargar configuración
        self.paths = load_paths_config(config_path)
        self.logger.info(f"Configuración cargada: {self.paths}")

        # Inicializar componentes
        self.metadata_manager = MetadataManager(self.paths["metadata"])
        self.face_detector = FaceDetector()
        self.image_processor = ImageProcessor()

        # Estadísticas de ejecución
        self.stats = {
            "total": 0,
            "processed": 0,
            "manual_review": 0,
            "errors": 0
        }

    def run(self, batch_id: str = None):
        """
        Ejecuta el pipeline completo.

        Args:
            batch_id: Identificador del lote (opcional, se autodetecta)
        """
        self.logger.info("=" * 80)
        self.logger.info("INICIO DEL PIPELINE DE PROCESAMIENTO")
        self.logger.info("=" * 80)

        # Escanear input_raw
        input_dir = Path(self.paths["input_raw"])
        images = list_images_in_directory(input_dir, self.image_processor.VALID_EXTENSIONS)

        if not images:
            self.logger.warning(f"No se encontraron imágenes en {input_dir}")
            return

        self.logger.info(f"Encontradas {len(images)} imágenes para procesar")
        self.stats["total"] = len(images)

        # Agrupar por batch
        batches = self._group_images_by_batch(images, input_dir)

        # Procesar cada batch
        for batch_id, batch_images in batches.items():
            self.logger.info(f"\nProcesando lote: {batch_id} ({len(batch_images)} imágenes)")
            self._process_batch(batch_id, batch_images)

        # Resumen final
        self._print_summary()

    def _group_images_by_batch(self, images: List[Path], input_base: Path) -> Dict[str, List[Path]]:
        """Agrupa imágenes por batch_id."""
        batches = {}
        for img_path in images:
            batch_id = get_batch_id_from_path(img_path, input_base)
            if batch_id not in batches:
                batches[batch_id] = []
            batches[batch_id].append(img_path)
        return batches

    def _process_batch(self, batch_id: str, images: List[Path]):
        """Procesa un lote completo de imágenes."""
        metadata_list = []
        batch_path = None

        for img_path in images:
            if batch_path is None:
                # Calcular batch_path solo una vez
                batch_path = str(img_path.parent.relative_to(Path(self.paths["input_raw"])))

            self.logger.info(f"\n{'=' * 60}")
            self.logger.info(f"Procesando: {img_path.name}")
            self.logger.info(f"{'=' * 60}")

            metadata = self._process_single_image(img_path, batch_id)
            if metadata:
                metadata_list.append(metadata)

        # Generar resumen del lote
        if metadata_list and batch_path:
            summary = self.metadata_manager.create_batch_summary(
                batch_id, metadata_list, f"./{self.paths['input_raw']}/{batch_path}"
            )
            summary_path = self.metadata_manager.save_batch_summary(summary)
            self.logger.info(f"\nResumen del lote guardado en: {summary_path}")

    def _process_single_image(self, img_path: Path, batch_id: str) -> Dict[str, Any]:
        """Procesa una única imagen."""

        try:
            # 1. VALIDACIÓN BÁSICA
            self.logger.info("1. Validación básica...")
            img = self.image_processor.load_image(img_path)

            if img is None:
                self.logger.error(f"Error al cargar imagen: archivo corrupto o inválido")
                return self._handle_error(
                    img_path, batch_id,
                    "PIL.UnidentifiedImageError: cannot identify image file - archivo corrupto o formato inválido"
                )

            # 2. EXTRAER DATOS BÁSICOS
            self.logger.info("2. Extrayendo información básica...")
            img_info = self.image_processor.get_image_info(img)

            # Crear metadata inicial
            metadata = self.metadata_manager.create_metadata(
                filename=img_path.name,
                input_path=str(img_path),
                batch_id=batch_id,
                width=img_info["width"],
                height=img_info["height"],
                img_format=img_info["format"]
            )

            self.logger.info(f"   Dimensiones: {img_info['width']}x{img_info['height']}")
            self.logger.info(f"   Formato: {img_info['format']}")
            self.logger.info(f"   Orientación: {metadata['orientation']}")

            # 3. ANÁLISIS FACIAL
            self.logger.info("3. Análisis facial con dlib...")
            img_array = self.image_processor.image_to_array(img)
            faces = self.face_detector.detect_faces(img_array)
            num_faces = len(faces)

            self.logger.info(f"   Rostros detectados: {num_faces}")

            # 4. PROCESAMIENTO SEGÚN RESULTADO
            if num_faces == 0:
                # Sin rostros - Manual review
                self.logger.warning("   ⚠️  No se detectó ningún rostro")
                metadata = self._handle_no_face(metadata, img_path, batch_id)

            elif num_faces == 1:
                # Un rostro - Procesar
                self.logger.info("   ✓ Un rostro detectado - procesando...")
                face_box = faces[0]
                metadata = self._handle_single_face(metadata, img, img_path, batch_id, face_box)

            else:
                # Múltiples rostros - Manual review
                self.logger.warning(f"   ⚠️  Se detectaron {num_faces} rostros")
                largest_face = self.face_detector.get_largest_face(faces)
                metadata = self._handle_multiple_faces(metadata, img_path, batch_id, num_faces, largest_face)

            # 5. GUARDAR METADATA
            metadata_path = self.metadata_manager.save_metadata(metadata, batch_id)
            self.logger.info(f"✓ Metadata guardado en: {metadata_path}")

            return metadata

        except Exception as e:
            self.logger.error(f"Error inesperado procesando {img_path.name}: {str(e)}")
            return self._handle_error(img_path, batch_id, f"Error inesperado: {str(e)}")

    def _handle_no_face(self, metadata: Dict[str, Any], img_path: Path, batch_id: str) -> Dict[str, Any]:
        """Maneja imágenes sin rostros detectados."""
        year = datetime.now().year
        dest_dir = Path(self.paths["manual_review"]) / str(year) / batch_id
        ensure_directory(dest_dir)
        dest_path = dest_dir / img_path.name

        copy_file(img_path, dest_path)

        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=False,
            num_faces=0,
            face_box=None,
            status="manual_review",
            current_path=str(dest_path),
            notes="No se detectó ningún rostro en la imagen",
            action="face_detection",
            details="No faces detected"
        )

        self.stats["manual_review"] += 1
        return metadata

    def _handle_single_face(
        self, metadata: Dict[str, Any], img, img_path: Path,
        batch_id: str, face_box: tuple
    ) -> Dict[str, Any]:
        """Maneja imágenes con un solo rostro."""
        year = datetime.now().year

        # Guardar en working/faces_detected
        working_dir = Path(self.paths["working"]) / "faces_detected" / str(year) / batch_id
        ensure_directory(working_dir)
        working_path = working_dir / img_path.name
        copy_file(img_path, working_path)

        # Preparar output path
        output_dir = Path(self.paths["prepared"]) / str(year) / batch_id
        output_path = output_dir / img_path.name

        # Actualizar metadata
        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=True,
            num_faces=1,
            face_box=list(face_box),
            status="processed",
            current_path=str(working_path),
            output_path=str(output_path),
            action="face_detection",
            details="1 face detected successfully"
        )

        self.logger.info(f"   Face box: {face_box}")
        self.stats["processed"] += 1
        return metadata

    def _handle_multiple_faces(
        self, metadata: Dict[str, Any], img_path: Path,
        batch_id: str, num_faces: int, largest_face: tuple
    ) -> Dict[str, Any]:
        """Maneja imágenes con múltiples rostros."""
        year = datetime.now().year
        dest_dir = Path(self.paths["manual_review"]) / str(year) / batch_id
        ensure_directory(dest_dir)
        dest_path = dest_dir / img_path.name

        copy_file(img_path, dest_path)

        metadata = self.metadata_manager.update_metadata(
            metadata,
            face_detected=True,
            num_faces=num_faces,
            face_box=list(largest_face) if largest_face else None,
            status="manual_review",
            current_path=str(dest_path),
            notes=f"Se detectaron múltiples rostros - requiere revisión manual para identificar al postulante",
            action="face_detection",
            details=f"{num_faces} faces detected, requires manual selection"
        )

        self.stats["manual_review"] += 1
        return metadata

    def _handle_error(self, img_path: Path, batch_id: str, error_message: str) -> Dict[str, Any]:
        """Maneja errores en el procesamiento."""
        year = datetime.now().year
        error_dir = Path(self.paths["errors"]) / str(year) / batch_id
        ensure_directory(error_dir)
        error_path = error_dir / img_path.name

        try:
            copy_file(img_path, error_path)
            current_path = str(error_path)
        except:
            current_path = str(img_path)

        metadata = self.metadata_manager.create_metadata(
            filename=img_path.name,
            input_path=str(img_path),
            batch_id=batch_id
        )

        metadata = self.metadata_manager.update_metadata(
            metadata,
            status="error",
            error_message=error_message,
            current_path=current_path,
            notes="Archivo movido a carpeta de errores para inspección manual",
            action="initial_scan",
            details="Failed to open image file"
        )

        self.metadata_manager.save_metadata(metadata, batch_id)
        self.stats["errors"] += 1
        return metadata

    def _print_summary(self):
        """Imprime resumen de la ejecución."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("RESUMEN DE EJECUCIÓN")
        self.logger.info("=" * 80)
        self.logger.info(f"Total de imágenes:        {self.stats['total']}")
        self.logger.info(f"  ✓ Procesadas:           {self.stats['processed']}")
        self.logger.info(f"  ⚠ Revisión manual:      {self.stats['manual_review']}")
        self.logger.info(f"  ✗ Errores:              {self.stats['errors']}")

        if self.stats['total'] > 0:
            success_rate = (self.stats['processed'] / self.stats['total']) * 100
            self.logger.info(f"\nTasa de éxito: {success_rate:.1f}%")

        self.logger.info("=" * 80)


def main():
    """Función principal de ejecución."""
    pipeline = PhotoProcessingPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()

