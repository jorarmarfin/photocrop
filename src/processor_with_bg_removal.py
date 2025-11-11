"""
Procesador con eliminación de fondo integrada.
Extiende DeterministicPhotoProcessor para incluir remoción de fondo.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deterministic_processor import DeterministicPhotoProcessor
from core.background_remover import BackgroundRemover
from utils.file_utils import ensure_directory
from PIL import Image
import shutil


class PhotoProcessorWithBgRemoval(DeterministicPhotoProcessor):
    """
    Procesador de fotos con eliminación de fondo integrada.
    Extiende el procesador determinista para incluir remoción de fondo con IA.
    """

    def __init__(
        self,
        config_path: str = "./config/paths.json",
        enable_bg_removal: bool = True,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    ):
        """
        Inicializa el procesador con eliminación de fondo.

        Args:
            config_path: Ruta al archivo de configuración
            enable_bg_removal: Activar eliminación de fondo
            background_color: Color RGBA del fondo (default: blanco)
        """
        # Inicializar procesador base
        super().__init__(config_path)

        # Configuración de eliminación de fondo
        self.enable_bg_removal = enable_bg_removal
        self.background_color = background_color

        # Inicializar removedor de fondo
        if self.enable_bg_removal:
            try:
                self.background_remover = BackgroundRemover()
                self.logger.info("✓ BackgroundRemover inicializado")
            except ImportError:
                self.logger.warning("⚠ rembg no disponible, desactivando remoción de fondo")
                self.enable_bg_removal = False

        # Crear carpetas adicionales
        self.paths["working_cropped"] = "./working/faces_cropped"
        self.paths["prepared"] = "./prepared"
        ensure_directory(self.paths["working_cropped"])
        ensure_directory(self.paths["prepared"])

    def _process_successful_crop(
        self,
        img_path: Path,
        img: Image.Image,
        metadata: dict,
        batch_id: str,
        crop_box: list
    ):
        """
        Procesamiento exitoso con eliminación de fondo integrada.

        Flujo:
        1. Aplicar recorte
        2. Guardar en working/faces_cropped
        3. Remover fondo (si está activado)
        4. Guardar en prepared
        5. Copiar a output
        6. Actualizar metadata
        """
        self.logger.info("  ✓ Aplicando recorte...")

        # 1. APLICAR RECORTE
        cropped_img = img.crop(crop_box)

        # 2. GUARDAR EN WORKING
        working_dir = Path(self.paths["working_cropped"])
        working_dir.mkdir(parents=True, exist_ok=True)
        working_path = working_dir / img_path.name

        if img_path.suffix.lower() in ['.jpg', '.jpeg']:
            cropped_img.save(working_path, 'JPEG', quality=95)
        else:
            cropped_img.save(working_path)

        self.logger.info(f"  ✓ Guardado en working: {working_path}")

        # 3. ELIMINACIÓN DE FONDO (SI ESTÁ ACTIVADA)
        if self.enable_bg_removal:
            self.logger.info("  🎨 Removiendo fondo con IA...")

            prepared_dir = Path(self.paths["prepared"])
            prepared_dir.mkdir(parents=True, exist_ok=True)
            prepared_path = prepared_dir / img_path.name

            success = self.background_remover.remove_background(
                input_path=working_path,
                output_path=prepared_path,
                background_color=self.background_color
            )

            if success:
                self.logger.info(f"  ✓ Fondo removido: {prepared_path}")
                metadata["background_removed"] = True
                metadata["background_color"] = self._color_to_name(self.background_color)
                metadata["background_removal_model"] = "u2net"
                metadata["prepared_path"] = str(prepared_path)

                # Usar imagen con fondo removido
                final_source = prepared_path
            else:
                self.logger.warning("  ⚠ Error al remover fondo, usando imagen original")
                metadata["background_removed"] = False
                metadata["background_removal_error"] = "Fallo en procesamiento"
                final_source = working_path
        else:
            # No remover fondo, usar imagen recortada directamente
            metadata["background_removed"] = False
            metadata["background_color"] = None
            final_source = working_path

        # 4. COPIAR A OUTPUT FINAL
        output_dir = Path(self.paths["output"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / img_path.name

        shutil.copy2(final_source, output_path)

        # 5. ACTUALIZAR METADATA
        metadata = self.metadata_manager.update_metadata(
            metadata,
            current_path=str(output_path),
            output_path=str(output_path),
            status="processed",
            action="face_detected_and_cropped",
            details="Recorte aplicado exitosamente" + (
                " con eliminación de fondo" if metadata.get("background_removed") else ""
            )
        )

        # 6. GUARDAR Y REGISTRAR
        self.metadata_manager.save_metadata(metadata, batch_id)
        self.processed_index.add_processed(img_path.name, "processed")
        self.processed_index.save()
        self.stats["processed"] += 1

        self.logger.info(f"  ✓ Imagen procesada exitosamente → {output_path}")

    def _color_to_name(self, color: Tuple[int, int, int, int]) -> str:
        """Convierte color RGBA a nombre descriptivo."""
        if color == (255, 255, 255, 255):
            return "white"
        elif color == (240, 240, 240, 255):
            return "gray"
        elif color == (235, 235, 235, 255):
            return "institutional"
        else:
            return f"rgb({color[0]},{color[1]},{color[2]})"


def main():
    """Punto de entrada con eliminación de fondo."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Procesador de fotos con eliminación de fondo"
    )
    parser.add_argument(
        '--batch-id',
        default='admission_2025_01',
        help='Identificador del lote'
    )
    parser.add_argument(
        '--no-bg-removal',
        action='store_true',
        help='Desactivar eliminación de fondo'
    )
    parser.add_argument(
        '--bg-color',
        default='white',
        choices=['white', 'gray', 'institutional'],
        help='Color de fondo (default: white)'
    )
    parser.add_argument(
        '--auto-clean',
        action='store_true',
        help='Eliminar archivos procesados de input_raw'
    )

    args = parser.parse_args()

    # Mapear colores
    color_map = {
        'white': (255, 255, 255, 255),
        'gray': (240, 240, 240, 255),
        'institutional': (235, 235, 235, 255)
    }

    # Inicializar procesador
    processor = PhotoProcessorWithBgRemoval(
        enable_bg_removal=not args.no_bg_removal,
        background_color=color_map[args.bg_color]
    )

    # Ejecutar
    stats = processor.run(
        batch_id=args.batch_id,
        auto_clean=args.auto_clean
    )

    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN CON ELIMINACIÓN DE FONDO")
    print("=" * 80)
    print(f"Eliminación de fondo: {'✓ Activada' if not args.no_bg_removal else '✗ Desactivada'}")
    if not args.no_bg_removal:
        print(f"Color de fondo: {args.bg_color}")
    print(f"Total procesadas: {stats['processed']}")
    print("=" * 80)

    return stats


if __name__ == "__main__":
    main()

