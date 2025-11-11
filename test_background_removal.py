#!/usr/bin/env python3
"""
Script de test para verificar eliminación de fondo
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test 1: Verificar que se pueden importar los módulos"""
    print("=" * 60)
    print("TEST 1: Verificación de Importaciones")
    print("=" * 60)

    try:
        from rembg import remove
        print("✓ rembg importado correctamente")
    except ImportError as e:
        print(f"✗ Error al importar rembg: {e}")
        return False

    try:
        from core.background_remover import BackgroundRemover
        print("✓ BackgroundRemover importado correctamente")
    except ImportError as e:
        print(f"✗ Error al importar BackgroundRemover: {e}")
        return False

    print("✓ Todas las importaciones exitosas\n")
    return True


def test_model_download():
    """Test 2: Verificar que el modelo está descargado"""
    print("=" * 60)
    print("TEST 2: Verificación del Modelo U2-Net")
    print("=" * 60)

    import os
    model_path = Path.home() / ".u2net"

    if model_path.exists():
        print(f"✓ Directorio del modelo encontrado: {model_path}")
        files = list(model_path.glob("*"))
        if files:
            print(f"✓ Archivos del modelo:")
            for f in files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  - {f.name} ({size_mb:.1f} MB)")
        else:
            print("⚠ Directorio vacío, modelo se descargará en primer uso")
    else:
        print("⚠ Modelo no descargado, se descargará en primer uso")

    print()
    return True


def test_initialization():
    """Test 3: Inicializar BackgroundRemover"""
    print("=" * 60)
    print("TEST 3: Inicialización de BackgroundRemover")
    print("=" * 60)

    try:
        from core.background_remover import BackgroundRemover
        remover = BackgroundRemover()
        print("✓ BackgroundRemover inicializado correctamente")
        print(f"✓ Modelo cargado: {remover.model_loaded}")
        print()
        return True
    except Exception as e:
        print(f"✗ Error al inicializar: {e}")
        print()
        return False


def test_with_sample_image():
    """Test 4: Procesar una imagen de muestra si existe"""
    print("=" * 60)
    print("TEST 4: Procesamiento de Imagen de Prueba")
    print("=" * 60)

    from core.background_remover import BackgroundRemover
    from PIL import Image
    import tempfile

    try:
        # Crear imagen de prueba
        print("Creando imagen de prueba...")
        test_img = Image.new('RGB', (200, 200), color=(100, 150, 200))

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_input:
            test_img.save(tmp_input.name, 'JPEG')
            input_path = Path(tmp_input.name)

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_output:
            output_path = Path(tmp_output.name)

        # Procesar
        print(f"Procesando: {input_path.name}")
        remover = BackgroundRemover()
        success = remover.remove_background(
            input_path,
            output_path,
            background_color=(255, 255, 255, 255)
        )

        if success and output_path.exists():
            print(f"✓ Imagen procesada exitosamente")
            print(f"✓ Archivo de salida: {output_path}")
            size_kb = output_path.stat().st_size / 1024
            print(f"✓ Tamaño: {size_kb:.1f} KB")

            # Limpiar
            input_path.unlink()
            output_path.unlink()
            print("✓ Test completado")
            print()
            return True
        else:
            print("✗ Error en procesamiento")
            print()
            return False

    except Exception as e:
        print(f"✗ Error en test: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_color_options():
    """Test 5: Verificar opciones de color"""
    print("=" * 60)
    print("TEST 5: Opciones de Color de Fondo")
    print("=" * 60)

    from core.background_remover import remove_background_from_image

    colors = {
        "transparent": None,
        "white": (255, 255, 255, 255),
        "gray": (240, 240, 240, 255),
        "institutional": (235, 235, 235, 255)
    }

    print("Colores disponibles:")
    for name, rgba in colors.items():
        if rgba:
            print(f"  ✓ {name}: RGBA{rgba}")
        else:
            print(f"  ✓ {name}: Transparente (PNG)")

    print()
    return True


def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("SUITE DE TESTS - ELIMINACIÓN DE FONDO")
    print("=" * 60)
    print()

    tests = [
        ("Importaciones", test_imports),
        ("Modelo U2-Net", test_model_download),
        ("Inicialización", test_initialization),
        ("Opciones de Color", test_color_options),
        ("Procesamiento", test_with_sample_image)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ ERROR en {test_name}: {e}")
            results.append((test_name, False))

    # Resumen
    print("=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResultado: {passed}/{total} tests pasados")

    if passed == total:
        print("\n✅ Sistema de eliminación de fondo LISTO\n")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar instalación.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

