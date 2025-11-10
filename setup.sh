#!/bin/bash
# Script de instalación y configuración del proyecto PhotoCrop

echo "==============================================="
echo "PhotoCrop - Instalación y Configuración"
echo "==============================================="
echo ""

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"
echo ""

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ Entorno virtual ya existe"
fi
echo ""

# Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo ""
echo "Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "==============================================="
echo "✓ Instalación completada"
echo "==============================================="
echo ""
echo "Para usar el sistema:"
echo "  1. Activa el entorno: source .venv/bin/activate"
echo "  2. Copia fotos en: input_raw/2025/admission_01/"
echo "  3. Ejecuta: python src/main.py"
echo ""

