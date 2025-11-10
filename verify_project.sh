#!/bin/bash
# Script de verificación del proyecto PhotoCrop

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       PhotoCrop - Verificación del Proyecto               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - FALTANTE"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ - FALTANTE"
        return 1
    fi
}

echo "📁 Verificando estructura de carpetas..."
echo ""
check_dir "src/core"
check_dir "src/utils"
check_dir "config"
check_dir "docs"
check_dir "metadata/2025/admission_01"
check_dir "input_raw/2025/admission_01"
check_dir "logs"
check_dir "working/faces_detected"
check_dir "prepared"
check_dir "manual_review"
check_dir "errors"

echo ""
echo "📄 Verificando archivos de código..."
echo ""
check_file "src/main.py"
check_file "src/pipeline.py"
check_file "src/test_pipeline.py"
check_file "src/core/metadata_manager.py"
check_file "src/core/face_detector.py"
check_file "src/core/image_processor.py"
check_file "src/utils/logger.py"
check_file "src/utils/file_utils.py"

echo ""
echo "⚙️  Verificando configuración..."
echo ""
check_file "config/paths.json"
check_file "config/settings.yml"
check_file "requirements.txt"
check_file "setup.sh"
check_file ".gitignore"

echo ""
echo "📚 Verificando documentación..."
echo ""
check_file "README.md"
check_file "docs/QUICKSTART.md"
check_file "docs/metadata_flow.md"
check_file "docs/ENTREGABLES_METADATA.md"
check_file "PROJECT_COMPLETE.md"

echo ""
echo "📊 Verificando ejemplos de metadatos..."
echo ""
check_file "metadata/2025/admission_01/IMG_0001.json"
check_file "metadata/2025/admission_01/IMG_0002.json"
check_file "metadata/2025/admission_01/IMG_0003.json"
check_file "metadata/2025/admission_01/IMG_0004.json"
check_file "metadata/2025/admission_01/batch_summary.json"

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Verificar Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python 3 no encontrado"
fi

# Verificar venv
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual: .venv/ existe"
else
    echo -e "${YELLOW}⚠${NC} Entorno virtual: .venv/ no existe (ejecuta ./setup.sh)"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. Instalar dependencias:"
echo "   ${YELLOW}./setup.sh${NC}"
echo ""
echo "2. Probar el sistema (sin dlib):"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo "   ${YELLOW}cd src && python test_pipeline.py${NC}"
echo ""
echo "3. Instalar dlib (Ubuntu/Debian):"
echo "   ${YELLOW}sudo apt-get install build-essential cmake libopenblas-dev${NC}"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo "   ${YELLOW}pip install dlib${NC}"
echo ""
echo "4. Copiar fotos a procesar:"
echo "   ${YELLOW}cp /ruta/fotos/*.jpg input_raw/2025/admission_01/${NC}"
echo ""
echo "5. Ejecutar el pipeline:"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo "   ${YELLOW}cd src && python main.py${NC}"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✨ Proyecto PhotoCrop v1.0.0 - Listo para usar"
echo ""

