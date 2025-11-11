"""
Script de prueba para verificar el pipeline sin necesidad de dlib instalado.
Simula la detección de rostros para testing.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.metadata_manager import MetadataManager
from src.core.image_processor import ImageProcessor
from src.utils.logger import setup_logger
from src.utils.file_utils import load_paths_config


def test_metadata_manager():
    """Prueba el gestor de metadatos."""
    print("\n" + "="*60)
    print("TEST: MetadataManager")
    print("="*60)

    manager = MetadataManager("./metadata")

    # Crear metadata
    metadata = manager.create_metadata(
        filename="test_image.jpg",
        input_path="./input_raw/2025/test/test_image.jpg",
        batch_id="test_batch",
        width=1920,
        height=2560,
        img_format="JPG"
    )

    print("✓ Metadata creado:")
    print(f"  - Filename: {metadata['filename']}")
    print(f"  - Status: {metadata['status']}")
    print(f"  - Orientation: {metadata['orientation']}")

    # Actualizar metadata
    metadata = manager.update_metadata(
        metadata,
        status="processed",
        face_detected=True,
        num_faces=1,
        action="test",
        details="Test completed"
    )

    print("✓ Metadata actualizado:")
    print(f"  - Status: {metadata['status']}")
    print(f"  - Face detected: {metadata['face_detected']}")

    return True


def test_image_processor():
    """Prueba el procesador de imágenes."""
    print("\n" + "="*60)
    print("TEST: ImageProcessor")
    print("="*60)

    processor = ImageProcessor()

    # Verificar extensiones válidas
    print(f"✓ Extensiones válidas: {processor.VALID_EXTENSIONS}")

    # Test de cálculo de orientación
    test_file = Path("test.jpg")
    print(f"✓ Validación de archivo: {processor.is_valid_image_file(test_file)}")

    return True


def test_logger():
    """Prueba el sistema de logging."""
    print("\n" + "="*60)
    print("TEST: Logger")
    print("="*60)

    logger = setup_logger()
    logger.info("✓ Logger inicializado correctamente")
    logger.debug("✓ Mensaje de debug")
    logger.warning("✓ Mensaje de warning")

    return True


def test_paths_config():
    """Prueba la carga de configuración."""
    print("\n" + "="*60)
    print("TEST: Configuración de Rutas")
    print("="*60)

    paths = load_paths_config()

    print("✓ Rutas configuradas:")
    for key, value in paths.items():
        print(f"  - {key}: {value}")

    return True


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*80)
    print("SUITE DE PRUEBAS - PhotoCrop Pipeline")
    print("="*80)

    tests = [
        ("Configuración de Rutas", test_paths_config),
        ("Logger", test_logger),
        ("ImageProcessor", test_image_processor),
        ("MetadataManager", test_metadata_manager),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name}: PASS")
            else:
                failed += 1
                print(f"\n✗ {test_name}: FAIL")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print(f"Total: {passed + failed}")
    print(f"✓ Pasadas: {passed}")
    print(f"✗ Fallidas: {failed}")
    print("="*80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())

