"""
Módulo de eliminación de fondo usando IA (rembg).
Procesa imágenes para remover el fondo y aplicar color sólido.
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False


class BackgroundRemover:
    """
    Elimina el fondo de imágenes usando IA (modelo U2-Net).
    Funciona 100% offline después de descargar el modelo inicial.
    """

    def __init__(self):
        """Inicializa el removedor de fondo."""
        if not REMBG_AVAILABLE:
            raise ImportError(
                "rembg no está instalado. Instalar con: pip install rembg"
            )
        self.model_loaded = True

    def remove_background(
        self,
        input_path: Path,
        output_path: Path,
        background_color: Optional[Tuple[int, int, int, int]] = None
    ) -> bool:
        """
        Remueve el fondo de una imagen.

        Args:
            input_path: Ruta de la imagen de entrada
            output_path: Ruta de la imagen de salida
            background_color: Color RGBA del fondo (None = transparente)
                             Ejemplos: (255, 255, 255, 255) = blanco
                                      (240, 240, 240, 255) = gris claro

        Returns:
            True si se procesó correctamente, False en caso contrario
        """
        try:
            # Leer imagen de entrada
            with open(input_path, 'rb') as f:
                input_data = f.read()

            # Remover fondo (retorna PNG con transparencia)
            output_data = remove(input_data)

            # Convertir a PIL Image
            img = Image.open(io.BytesIO(output_data))

            # Si se especifica color de fondo, aplicarlo
            if background_color is not None:
                # Crear nueva imagen con fondo de color
                background = Image.new('RGBA', img.size, background_color)
                # Pegar imagen con transparencia sobre el fondo
                background.paste(img, (0, 0), img)
                img = background.convert('RGB')  # Convertir a RGB para JPG

            # Guardar resultado
            if background_color is not None:
                # Guardar como JPG si tiene fondo sólido
                img.save(output_path, 'JPEG', quality=95)
            else:
                # Guardar como PNG si tiene transparencia
                img.save(output_path, 'PNG')

            return True

        except Exception as e:
            print(f"Error al remover fondo: {e}")
            return False

    def process_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        background_color: Optional[Tuple[int, int, int, int]] = None,
        extensions: list = None
    ) -> dict:
        """
        Procesa múltiples imágenes en lote.

        Args:
            input_dir: Directorio con imágenes de entrada
            output_dir: Directorio para guardar resultados
            background_color: Color de fondo a aplicar
            extensions: Lista de extensiones válidas

        Returns:
            Dict con estadísticas del procesamiento
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png']

        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'files': []
        }

        for ext in extensions:
            for img_path in input_dir.glob(f"*{ext}"):
                stats['total'] += 1

                # Determinar nombre de salida
                if background_color is not None:
                    output_name = img_path.stem + '_nobg.jpg'
                else:
                    output_name = img_path.stem + '_nobg.png'

                output_path = output_dir / output_name

                # Procesar
                success = self.remove_background(
                    img_path,
                    output_path,
                    background_color
                )

                if success:
                    stats['success'] += 1
                    stats['files'].append(str(output_path))
                else:
                    stats['failed'] += 1

        return stats


def remove_background_from_image(
    input_path: str,
    output_path: str,
    background_color: str = "transparent"
) -> bool:
    """
    Función helper para remover fondo de una imagen.

    Args:
        input_path: Ruta de imagen de entrada
        output_path: Ruta de imagen de salida
        background_color: Color de fondo ("transparent", "white", "gray", o RGB)

    Returns:
        True si se procesó correctamente
    """
    # Mapear colores comunes
    color_map = {
        "transparent": None,
        "white": (255, 255, 255, 255),
        "gray": (240, 240, 240, 255),
        "light_gray": (245, 245, 245, 255),
        "institutional": (235, 235, 235, 255)
    }

    bg_color = color_map.get(background_color.lower())

    # Si es un color RGB en formato string, parsearlo
    if bg_color is None and background_color.startswith("("):
        try:
            bg_color = eval(background_color)
        except:
            bg_color = color_map["white"]

    remover = BackgroundRemover()
    return remover.remove_background(
        Path(input_path),
        Path(output_path),
        bg_color
    )


# Función de consola
def main():
    """Punto de entrada para uso por consola."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Remover fondo de imágenes usando IA"
    )
    parser.add_argument(
        'input',
        help='Archivo o directorio de entrada'
    )
    parser.add_argument(
        'output',
        help='Archivo o directorio de salida'
    )
    parser.add_argument(
        '--color',
        default='white',
        help='Color de fondo: transparent, white, gray (default: white)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Procesar directorio completo'
    )

    args = parser.parse_args()

    if not REMBG_AVAILABLE:
        print("Error: rembg no está instalado")
        print("Instalar con: pip install rembg")
        sys.exit(1)

    remover = BackgroundRemover()

    if args.batch:
        # Procesamiento por lotes
        stats = remover.process_batch(
            Path(args.input),
            Path(args.output),
            None if args.color == 'transparent' else (255, 255, 255, 255)
        )
        print(f"Procesadas: {stats['success']}/{stats['total']}")
    else:
        # Procesamiento individual
        success = remove_background_from_image(
            args.input,
            args.output,
            args.color
        )
        print("OK" if success else "ERROR")
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

