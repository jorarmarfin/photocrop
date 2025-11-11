#!/bin/bash
# Script de instalación de eliminación de fondo con IA
# Para Ubuntu/Linux con Python 3 + venv

echo "=============================================="
echo "Instalación de Eliminación de Fondo con IA"
echo "=============================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Activar entorno virtual
echo "1. Activando entorno virtual..."
if [ ! -d ".venv" ]; then
    echo "Error: Entorno virtual no encontrado. Crear con: python3 -m venv .venv"
    exit 1
fi

source .venv/bin/activate

# Instalar rembg
echo ""
echo "2. Instalando rembg..."
pip install rembg>=2.0.50

# Instalar onnxruntime
echo ""
echo "3. Instalando onnxruntime..."
pip install onnxruntime>=1.16.0

# Verificar instalación
echo ""
echo "4. Verificando instalación..."
python3 -c "from rembg import remove; print('✓ rembg instalado correctamente')" || {
    echo "✗ Error al importar rembg"
    exit 1
}

# Descargar modelo (primera vez)
echo ""
echo "5. Descargando modelo U2-Net (~176 MB)..."
echo "   Esto solo se hace una vez, luego funciona offline"
python3 -c "from rembg import remove; import io; from PIL import Image; img = Image.new('RGB', (100, 100), (255, 255, 255)); img_bytes = io.BytesIO(); img.save(img_bytes, format='PNG'); img_bytes.seek(0); remove(img_bytes.read()); print('✓ Modelo descargado en ~/.u2net/')" || {
    echo "⚠ Error al descargar modelo. Intentar manualmente."
    echo "   El modelo se descargará en el primer uso."
}

# Verificar ubicación del modelo
echo ""
echo "6. Verificando modelo..."
if [ -d "$HOME/.u2net" ]; then
    echo "✓ Modelo encontrado en: $HOME/.u2net/"
    ls -lh "$HOME/.u2net/"
else
    echo "⚠ Modelo no encontrado. Se descargará en primer uso."
fi

# Test rápido
echo ""
echo "7. Ejecutando test rápido..."
python3 << 'EOF'
from core.background_remover import BackgroundRemover
print("✓ Módulo BackgroundRemover cargado correctamente")
print("✓ Sistema listo para eliminar fondos")
EOF

echo ""
echo "=============================================="
echo "✓ Instalación completada exitosamente"
echo "=============================================="
echo ""
echo "Uso:"
echo "  1. Por consola:"
echo "     python src/core/background_remover.py input.jpg output.jpg --color white"
echo ""
echo "  2. Desde Python:"
echo "     from core.background_remover import BackgroundRemover"
echo "     remover = BackgroundRemover()"
echo "     remover.remove_background(input_path, output_path, bg_color)"
echo ""
echo "Documentación: docs/INTEGRACION_ELIMINACION_FONDO.md"
echo ""

