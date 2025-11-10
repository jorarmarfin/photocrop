"""
Punto de entrada principal del pipeline de procesamiento de fotos.
"""

from pipeline import PhotoProcessingPipeline


def main():
    """Ejecuta el pipeline de procesamiento de fotos."""
    print("=" * 80)
    print("PIPELINE DE NORMALIZACIÓN DE FOTOS DE POSTULANTES")
    print("=" * 80)
    print()

    try:
        pipeline = PhotoProcessingPipeline()
        pipeline.run()
        print("\n✓ Pipeline completado exitosamente")
    except Exception as e:
        print(f"\n✗ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

