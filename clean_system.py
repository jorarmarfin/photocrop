#!/usr/bin/env python3
"""
Script para limpiar el sistema PhotoCrop y resetear al estado inicial.
Elimina todas las carpetas de salida, metadatos y logs.
"""

import shutil
from pathlib import Path
import json
import sys


def clean_system(confirm: bool = True):
    """
    Limpia el sistema completamente.

    Args:
        confirm: Si True, pide confirmación antes de limpiar
    """
    print("\n" + "=" * 60)
    print("LIMPIEZA DEL SISTEMA PHOTOCROP")
    print("=" * 60)

    if confirm:
        print("\nEsta acción eliminará:")
        print("  • Todas las fotos procesadas (output, output_white, output_final)")
        print("  • Fotos en revisión manual y errores")
        print("  • Archivos temporales (working, prepared)")
        print("  • Metadatos generados")
        print("  • Índice de archivos procesados")
        print("  • Logs del sistema")
        print("\n⚠️  ADVERTENCIA: Esta acción NO se puede deshacer")
        print("\nLas carpetas de entrada (input_raw) NO serán eliminadas")

        response = input("\n¿Desea continuar? (escriba 'SI' para confirmar): ")
        if response != "SI":
            print("\n❌ Limpieza cancelada")
            return False

    print("\n" + "-" * 60)
    print("Iniciando limpieza...")
    print("-" * 60 + "\n")

    # Carpetas a limpiar completamente
    folders_to_clean = [
        './output',
        './output_white',
        './output_final',
        './working',
        './prepared',
        './manual_review',
        './errors'
    ]

    cleaned_count = 0

    # Limpiar carpetas
    for folder in folders_to_clean:
        folder_path = Path(folder)
        if folder_path.exists():
            file_count = 0
            for item in folder_path.rglob('*'):
                if item.is_file():
                    item.unlink()
                    file_count += 1

            # Eliminar subdirectorios vacíos
            for item in sorted(folder_path.rglob('*'), reverse=True):
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()

            print(f"✓ {folder:20s} - {file_count} archivo(s) eliminado(s)")
            cleaned_count += file_count
        else:
            print(f"⊘ {folder:20s} - No existe")

    print()

    # Limpiar metadatos (excepto archivos importantes)
    metadata_path = Path('./metadata')
    if metadata_path.exists():
        metadata_count = 0
        for item in metadata_path.rglob('*.json'):
            # Preservar archivos importantes
            if item.name not in ['sample.json', 'README.md']:
                item.unlink()
                metadata_count += 1

        # Eliminar subdirectorios vacíos en metadata
        for item in sorted(metadata_path.rglob('*'), reverse=True):
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()

        print(f"✓ Metadatos          - {metadata_count} archivo(s) eliminado(s)")
        cleaned_count += metadata_count

    # Resetear processed_index.json
    processed_index = Path('./metadata/processed_index.json')
    processed_index.parent.mkdir(parents=True, exist_ok=True)

    reset_data = {
        "processed_files": [],
        "last_updated": None,
        "total_processed": 0,
        "metadata_version": "1.0",
        "statistics": {
            "total_processed": 0,
            "successful": 0,
            "manual_review": 0,
            "errors": 0
        },
        "notes": "Este archivo mantiene un registro de todos los archivos que han sido procesados por el sistema. No eliminar manualmente."
    }

    with open(processed_index, 'w', encoding='utf-8') as f:
        json.dump(reset_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Índice procesados  - Reseteado correctamente")

    # Limpiar logs
    log_path = Path('./logs/pipeline.log')
    if log_path.exists():
        log_size = log_path.stat().st_size
        with open(log_path, 'w') as f:
            f.write('')
        print(f"✓ Logs del sistema   - {log_size} bytes eliminados")
    else:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch()
        print(f"✓ Logs del sistema   - Archivo creado")

    print("\n" + "=" * 60)
    print(f"✅ LIMPIEZA COMPLETADA")
    print("=" * 60)
    print(f"\nTotal de archivos eliminados: {cleaned_count}")
    print("\n🎯 El sistema está listo para comenzar desde cero")
    print("   Puedes copiar nuevas fotos en ./input_raw/ y procesarlas")
    print()

    return True


def show_current_state():
    """Muestra el estado actual del sistema."""
    print("\n" + "=" * 60)
    print("ESTADO ACTUAL DEL SISTEMA")
    print("=" * 60 + "\n")

    folders = {
        "input_raw": "Fotos originales",
        "output": "Fotos recortadas",
        "output_white": "Con fondo blanco",
        "output_final": "Formato original",
        "manual_review": "Revisión manual",
        "errors": "Errores",
        "working": "Temporales",
        "prepared": "Preparadas"
    }

    for folder_name, description in folders.items():
        folder_path = Path(f"./{folder_name}")
        if folder_path.exists():
            count = sum(1 for _ in folder_path.rglob('*') if _.is_file() and _.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'])
            print(f"  {description:20s}: {count:4d} imagen(es)")
        else:
            print(f"  {description:20s}: -")

    # Verificar processed_index
    processed_index = Path('./metadata/processed_index.json')
    if processed_index.exists():
        try:
            with open(processed_index, 'r') as f:
                data = json.load(f)
                total = data.get('total_processed', 0)
                print(f"\n  Total procesadas     : {total}")
        except:
            pass

    print()


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Limpia el sistema PhotoCrop y resetea al estado inicial"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Limpiar sin pedir confirmación'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostrar estado actual sin limpiar'
    )

    args = parser.parse_args()

    if args.status:
        show_current_state()
        return 0

    # Limpiar sistema
    success = clean_system(confirm=not args.force)

    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

