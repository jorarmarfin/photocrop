#!/usr/bin/env python3
"""
Script de prueba para el procesador determinista.
Verifica el funcionamiento del flujo completo sin procesar imágenes reales.
"""

import json
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))


def test_configuration():
    """Verifica que la configuración esté correcta."""
    print("=" * 80)
    print("TEST 1: Verificación de Configuración")
    print("=" * 80)

    config_path = Path("./config/paths.json")

    if not config_path.exists():
        print("❌ ERROR: No existe config/paths.json")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    required_paths = [
        "input_raw", "output", "metadata", "errors",
        "manual_review", "logs", "working", "prepared", "processed_index"
    ]

    paths = config.get("paths", {})
    missing = []

    for path_key in required_paths:
        if path_key not in paths:
            missing.append(path_key)
        else:
            print(f"✓ {path_key}: {paths[path_key]}")

    if missing:
        print(f"\n❌ ERROR: Faltan rutas: {', '.join(missing)}")
        return False

    print("\n✅ Configuración correcta")
    return True


def test_processed_index():
    """Verifica que processed_index.json exista y sea válido."""
    print("\n" + "=" * 80)
    print("TEST 2: Verificación de Processed Index")
    print("=" * 80)

    index_path = Path("./metadata/processed_index.json")

    if not index_path.exists():
        print("❌ ERROR: No existe metadata/processed_index.json")
        return False

    with open(index_path, 'r') as f:
        index_data = json.load(f)

    required_fields = ["processed_files", "metadata_version", "statistics"]
    missing = []

    for field in required_fields:
        if field not in index_data:
            missing.append(field)
        else:
            print(f"✓ {field}: {index_data[field]}")

    if missing:
        print(f"\n❌ ERROR: Faltan campos: {', '.join(missing)}")
        return False

    print("\n✅ Processed Index válido")
    return True


def test_directories():
    """Verifica que existan las carpetas necesarias."""
    print("\n" + "=" * 80)
    print("TEST 3: Verificación de Directorios")
    print("=" * 80)

    required_dirs = [
        "./input_raw",
        "./output",
        "./metadata",
        "./errors",
        "./manual_review",
        "./logs",
        "./working",
        "./prepared"
    ]

    all_exist = True

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path} existe")
        else:
            print(f"❌ {dir_path} NO EXISTE")
            all_exist = False

    if all_exist:
        print("\n✅ Todos los directorios existen")
    else:
        print("\n⚠️  Algunos directorios no existen (se crearán automáticamente)")

    return True


def test_gitignore():
    """Verifica que .gitignore proteja datos sensibles."""
    print("\n" + "=" * 80)
    print("TEST 4: Verificación de .gitignore")
    print("=" * 80)

    gitignore_path = Path("./.gitignore")

    if not gitignore_path.exists():
        print("❌ ERROR: No existe .gitignore")
        return False

    with open(gitignore_path, 'r') as f:
        content = f.read()

    protected_paths = [
        "input_raw/",
        "output/",
        "metadata/",
        "errors/",
        "manual_review/"
    ]

    all_protected = True

    for path in protected_paths:
        if path in content:
            print(f"✓ {path} está protegido")
        else:
            print(f"❌ {path} NO está protegido")
            all_protected = False

    if all_protected:
        print("\n✅ .gitignore correctamente configurado")
    else:
        print("\n❌ .gitignore necesita correcciones")

    return all_protected


def test_documentation():
    """Verifica que exista la documentación del flujo."""
    print("\n" + "=" * 80)
    print("TEST 5: Verificación de Documentación")
    print("=" * 80)

    docs = [
        "./docs/FLUJO_PROCESAMIENTO.md",
        "./docs/README_FLUJO.md",
        "./README.md"
    ]

    all_exist = True

    for doc_path in docs:
        path = Path(doc_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✓ {doc_path} existe ({size} bytes)")
        else:
            print(f"❌ {doc_path} NO EXISTE")
            all_exist = False

    if all_exist:
        print("\n✅ Documentación completa")
    else:
        print("\n⚠️  Falta documentación")

    return True


def test_processor_import():
    """Verifica que se puedan importar los módulos."""
    print("\n" + "=" * 80)
    print("TEST 6: Verificación de Importaciones")
    print("=" * 80)

    try:
        # Agregar src al path para importaciones
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from deterministic_processor import (
            DeterministicPhotoProcessor,
            ProcessedIndexManager,
            CropDecisionEngine
        )
        print("✓ DeterministicPhotoProcessor importado")
        print("✓ ProcessedIndexManager importado")
        print("✓ CropDecisionEngine importado")

        print("\n✅ Todos los módulos se importan correctamente")
        return True

    except ImportError as e:
        print(f"❌ ERROR al importar: {e}")
        print(f"   sys.path: {sys.path[:3]}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DEL SISTEMA PHOTOCROP")
    print("=" * 80)

    tests = [
        ("Configuración", test_configuration),
        ("Processed Index", test_processed_index),
        ("Directorios", test_directories),
        (".gitignore", test_gitignore),
        ("Documentación", test_documentation),
        ("Importaciones", test_processor_import)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR en test {test_name}: {e}")
            results.append((test_name, False))

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResultado: {passed}/{total} tests pasados")

    if passed == total:
        print("\n🎉 ¡Sistema verificado correctamente!")
        print("Puedes comenzar a copiar fotos en ./input_raw/ y ejecutar:")
        print("  python src/deterministic_processor.py")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar errores arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

