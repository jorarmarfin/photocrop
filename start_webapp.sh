#!/bin/bash
# Script para iniciar el Dashboard Web de PhotoCrop

set -e

echo "=============================================="
echo "PhotoCrop Web Dashboard"
echo "=============================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Activar entorno virtual
if [ ! -d ".venv" ]; then
    echo "Error: Entorno virtual no encontrado"
    echo "Crear con: python3 -m venv .venv"
    exit 1
fi

echo "Activando entorno virtual..."
source .venv/bin/activate

# Verificar que FastAPI está instalado
if ! python -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "FastAPI no está instalado. Instalando dependencias..."
    pip install fastapi uvicorn[standard] jinja2 python-multipart
fi

# Función para limpiar el sistema
function clean_system() {
    echo ""
    echo "=============================================="
    echo "LIMPIEZA DEL SISTEMA"
    echo "=============================================="
    echo ""
    echo "Esta acción eliminará:"
    echo "  • Todas las carpetas de salida (output, output_white, output_final)"
    echo "  • Carpetas de errores y revisión manual"
    echo "  • Metadatos generados"
    echo "  • Índice de archivos procesados"
    echo "  • Logs del sistema"
    echo ""
    echo "⚠️  ADVERTENCIA: Esta acción NO se puede deshacer"
    echo ""
    read -p "¿Desea continuar? (escriba 'SI' para confirmar): " confirm

    if [ "$confirm" != "SI" ]; then
        echo "Limpieza cancelada"
        return
    fi

    echo ""
    echo "Limpiando sistema..."

    python3 << 'EOF'
import shutil
from pathlib import Path

# Carpetas a limpiar
folders_to_clean = [
    './output',
    './output_white',
    './output_final',
    './working',
    './prepared',
    './manual_review',
    './errors'
]

# Limpiar carpetas
for folder in folders_to_clean:
    folder_path = Path(folder)
    if folder_path.exists():
        for item in folder_path.rglob('*'):
            if item.is_file():
                item.unlink()
        print(f"✓ {folder} limpiado")
    else:
        print(f"⊘ {folder} no existe")

# Limpiar metadatos (excepto sample.json y README.md)
metadata_path = Path('./metadata')
if metadata_path.exists():
    for item in metadata_path.rglob('*.json'):
        if item.name not in ['sample.json', 'processed_index.json']:
            item.unlink()
    print(f"✓ Metadatos limpiados")

# Resetear processed_index.json
processed_index = Path('./metadata/processed_index.json')
if processed_index.exists():
    import json
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
    with open(processed_index, 'w') as f:
        json.dump(reset_data, f, indent=2)
    print(f"✓ Índice de procesados reseteado")

# Limpiar logs
log_path = Path('./logs/pipeline.log')
if log_path.exists():
    with open(log_path, 'w') as f:
        f.write('')
    print(f"✓ Logs limpiados")

print("\n✅ Sistema limpiado correctamente")
print("El sistema está listo para comenzar desde cero")
EOF

    echo ""
    read -p "Presiona Enter para continuar..."
}

# Menú de opciones
echo ""
echo "Opciones disponibles:"
echo "  1) Iniciar Dashboard Web"
echo "  2) Limpiar sistema (resetear todo)"
echo "  3) Salir"
echo ""
read -p "Seleccione una opción [1-3]: " option

case $option in
    2)
        clean_system
        exit 0
        ;;
    3)
        echo "Saliendo..."
        exit 0
        ;;
    1|*)
        # Continuar con inicio del servidor
        ;;
esac

echo ""
echo "=============================================="
echo "Iniciando servidor web..."
echo "=============================================="
echo ""
echo "Dashboard disponible en:"
echo "  🌐 http://localhost:8000"
echo "  🌐 http://127.0.0.1:8000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Cambiar al directorio del proyecto
PROJECT_DIR="/home/lmayta/PycharmProjects/PhotoCrop"
cd "$PROJECT_DIR"

# Agregar directorio actual al PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Iniciar servidor
uvicorn src.webapp.app:app --host 0.0.0.0 --port 8000 --reload

