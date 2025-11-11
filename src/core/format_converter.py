"""
Módulo para convertir imágenes al formato original.
Convierte imágenes de una carpeta a otra manteniendo el formato original.
"""

from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
import json


class FormatConverter:
    """
    Convierte imágenes al formato original basándose en metadatos
    o extensión del archivo de entrada.
    """

    def __init__(self, metadata_dir: Optional[Path] = None):
        """
        Inicializa el conversor de formatos.

        Args:
            metadata_dir: Directorio con metadatos JSON (opcional)
        """
        self.metadata_dir = metadata_dir

    def get_original_format(self, filename: str) -> str:
        """
        Obtiene el formato original de una imagen desde metadata.

        Args:
            filename: Nombre del archivo

        Returns:
            Extensión del formato original (ej: '.jpg', '.png')
        """
        if self.metadata_dir is None:
            # Sin metadata, intentar desde el nombre
            return Path(filename).suffix.lower()

        # Buscar archivo de metadata
        metadata_file = None
        for meta_path in self.metadata_dir.rglob(f"{Path(filename).stem}.json"):
            metadata_file = meta_path
            break

        if metadata_file and metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Obtener formato original
                original_format = metadata.get('format', 'JPEG')

                # Mapear formato PIL a extensión
                format_map = {
                    'JPEG': '.jpg',
                    'PNG': '.png',
                    'BMP': '.bmp',
                    'TIFF': '.tiff',
                    'GIF': '.gif'
                }

                return format_map.get(original_format, '.jpg')
            except:
                pass

        # Por defecto, usar extensión del archivo
        return Path(filename).suffix.lower() or '.jpg'

    def convert_image(
        self,
        input_path: Path,
        output_path: Path,
        target_format: Optional[str] = None,
        quality: int = 95
    ) -> bool:
        """
        Convierte una imagen al formato especificado.

        Args:
            input_path: Ruta de imagen de entrada
            output_path: Ruta de imagen de salida
            target_format: Formato destino (None = detectar de metadata)
            quality: Calidad JPEG (1-100)

        Returns:
            True si se convirtió correctamente
        """
        try:
            # Abrir imagen
            img = Image.open(input_path)

            # Determinar formato de salida
            if target_format is None:
                # Obtener formato original desde metadata
                target_format = self.get_original_format(input_path.name)

            # Normalizar extensión
            if not target_format.startswith('.'):
                target_format = f'.{target_format}'

            target_format = target_format.lower()

            # Ajustar nombre de salida con formato correcto
            output_path = output_path.with_suffix(target_format)

            # Convertir según formato
            if target_format in ['.jpg', '.jpeg']:
                # Convertir a RGB si es necesario (PNG con alpha -> JPG)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Crear fondo blanco
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                img.save(output_path, 'JPEG', quality=quality, optimize=True)

            elif target_format == '.png':
                img.save(output_path, 'PNG', optimize=True)

            elif target_format == '.bmp':
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, 'BMP')

            elif target_format in ['.tiff', '.tif']:
                img.save(output_path, 'TIFF')

            else:
                # Formato desconocido, usar PIL por defecto
                img.save(output_path)

            return True

        except Exception as e:
            print(f"Error al convertir {input_path.name}: {e}")
            return False

    def convert_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        quality: int = 95,
        extensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Convierte todas las imágenes de un directorio.

        Args:
            input_dir: Directorio de entrada
            output_dir: Directorio de salida
            quality: Calidad JPEG (1-100)
            extensions: Lista de extensiones a procesar

        Returns:
            Dict con estadísticas del proceso
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {
            'total': 0,
            'converted': 0,
            'failed': 0,
            'files': []
        }

        # Procesar cada archivo
        for ext in extensions:
            for img_path in input_dir.glob(f"*{ext}"):
                stats['total'] += 1

                # Mantener nombre original
                output_path = output_dir / img_path.name

                # Convertir
                success = self.convert_image(
                    input_path=img_path,
                    output_path=output_path,
                    target_format=None,  # Detectar desde metadata
                    quality=quality
                )

                if success:
                    stats['converted'] += 1
                    stats['files'].append(str(output_path))
                else:
                    stats['failed'] += 1

        return stats


def convert_to_original_format(
    input_dir: str,
    output_dir: str,
    metadata_dir: Optional[str] = "./metadata",
    quality: int = 95
) -> Dict:
    """
    Función helper para convertir imágenes al formato original.

    Args:
        input_dir: Directorio con imágenes procesadas
        output_dir: Directorio para guardar con formato original
        metadata_dir: Directorio con archivos de metadata
        quality: Calidad JPEG (1-100)

    Returns:
        Dict con estadísticas
    """
    converter = FormatConverter(
        metadata_dir=Path(metadata_dir) if metadata_dir else None
    )

    return converter.convert_batch(
        input_dir=Path(input_dir),
        output_dir=Path(output_dir),
        quality=quality
    )


def main():
    """Punto de entrada para uso por consola."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convertir imágenes al formato original"
    )
    parser.add_argument(
        'input_dir',
        help='Directorio con imágenes procesadas'
    )
    parser.add_argument(
        'output_dir',
        help='Directorio para guardar con formato original'
    )
    parser.add_argument(
        '--metadata-dir',
        default='./metadata',
        help='Directorio con metadatos (default: ./metadata)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=95,
        help='Calidad JPEG 1-100 (default: 95)'
    )

    args = parser.parse_args()

    print(f"Convirtiendo imágenes de: {args.input_dir}")
    print(f"Guardando en: {args.output_dir}")
    print(f"Usando metadatos de: {args.metadata_dir}")
    print()

    stats = convert_to_original_format(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        metadata_dir=args.metadata_dir,
        quality=args.quality
    )

    print(f"\n{'='*60}")
    print(f"RESUMEN DE CONVERSIÓN")
    print(f"{'='*60}")
    print(f"Total procesadas: {stats['total']}")
    print(f"Convertidas exitosamente: {stats['converted']}")
    print(f"Fallidas: {stats['failed']}")
    print(f"{'='*60}\n")

    return 0 if stats['failed'] == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

