#!/bin/bash
# Script para convertir imágenes procesadas al formato original
# Uso: ./convert_to_original_format.sh <carpeta_origen> <carpeta_destino>

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar argumentos
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Faltan argumentos${NC}"
    echo ""
    echo "Uso: $0 <carpeta_origen> <carpeta_destino> [metadata_dir] [quality]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 ./prepared ./output"
    echo "  $0 ./white ./output_final ./metadata 95"
    echo ""
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"
METADATA_DIR="${3:-./metadata}"
QUALITY="${4:-95}"

# Verificar que existe carpeta origen
if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}Error: No existe la carpeta origen: $INPUT_DIR${NC}"
    exit 1
fi

# Verificar que existe carpeta metadata
if [ ! -d "$METADATA_DIR" ]; then
    echo -e "${YELLOW}Advertencia: No existe carpeta metadata: $METADATA_DIR${NC}"
    echo -e "${YELLOW}Se usará extensión original de archivos${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Conversión a Formato Original${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Carpeta origen:   $INPUT_DIR"
echo "Carpeta destino:  $OUTPUT_DIR"
echo "Metadata:         $METADATA_DIR"
echo "Calidad JPEG:     $QUALITY"
echo ""

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo -e "${GREEN}Activando entorno virtual...${NC}"
    source .venv/bin/activate
fi

# Ejecutar conversión
echo -e "${GREEN}Iniciando conversión...${NC}"
echo ""

python src/core/format_converter.py \
    "$INPUT_DIR" \
    "$OUTPUT_DIR" \
    --metadata-dir "$METADATA_DIR" \
    --quality "$QUALITY"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Conversión completada exitosamente${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Archivos guardados en: $OUTPUT_DIR"
    echo ""
    echo "Ver archivos:"
    echo "  ls -lh $OUTPUT_DIR"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Error en la conversión${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    exit $EXIT_CODE
fi

