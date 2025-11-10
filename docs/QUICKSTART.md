# Guía de Inicio Rápido - PhotoCrop

## Instalación Rápida

```bash
# 1. Clonar o descargar el proyecto
cd /ruta/al/proyecto/PhotoCrop

# 2. Ejecutar script de instalación
chmod +x setup.sh
./setup.sh

# O manualmente:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Estructura de Archivos Creados

```
PhotoCrop/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── metadata_manager.py      # ✓ Gestor de metadatos
│   │   ├── face_detector.py         # ✓ Detector facial con dlib
│   │   └── image_processor.py       # ✓ Procesador de imágenes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                # ✓ Sistema de logging
│   │   └── file_utils.py            # ✓ Utilidades
│   ├── pipeline.py                  # ✓ Pipeline principal
│   ├── main.py                      # ✓ Punto de entrada
│   └── test_pipeline.py             # ✓ Suite de pruebas
├── config/
│   ├── paths.json                   # ✓ Configuración de rutas
│   └── settings.yml                 # ✓ Configuración general
├── metadata/
│   ├── README.md
│   └── 2025/admission_01/           # ✓ Ejemplos de metadatos
├── docs/
│   ├── metadata_flow.md             # ✓ Diseño del flujo
│   ├── ENTREGABLES_METADATA.md      # ✓ Resumen de entregables
│   └── QUICKSTART.md                # Este archivo
├── requirements.txt                 # ✓ Dependencias
├── setup.sh                         # ✓ Script de instalación
├── .gitignore                       # ✓ Git ignore
└── README.md                        # ✓ Documentación principal
```

## Prueba del Sistema (Sin dlib)

Antes de instalar dlib, puedes probar que el resto del sistema funciona:

```bash
source .venv/bin/activate
cd src
python test_pipeline.py
```

Esto probará:
- ✓ Carga de configuración
- ✓ Sistema de logging
- ✓ Procesador de imágenes (validaciones básicas)
- ✓ Gestor de metadatos (creación y actualización)

## Instalación de dlib (Ubuntu/Debian)

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y build-essential cmake
sudo apt-get install -y libopenblas-dev liblapack-dev
sudo apt-get install -y libx11-dev libgtk-3-dev

# Activar entorno virtual
source .venv/bin/activate

# Instalar dlib
pip install cmake
pip install dlib
```

## Uso Básico

### 1. Preparar Imágenes

```bash
# Crear estructura de entrada
mkdir -p input_raw/2025/admission_01

# Copiar tus imágenes
cp /ruta/a/fotos/*.jpg input_raw/2025/admission_01/
```

### 2. Ejecutar Pipeline

```bash
cd src
python main.py
```

### 3. Revisar Resultados

```bash
# Ver logs
tail -f logs/pipeline.log

# Ver imágenes procesadas
ls -l prepared/2025/admission_01/

# Ver metadatos
cat metadata/2025/admission_01/IMG_0001.json

# Ver resumen del lote
cat metadata/2025/admission_01/batch_summary.json
```

## Ejemplos de Metadatos Generados

El sistema genera archivos JSON para cada imagen procesada. Ver ejemplos en:

```bash
cat metadata/2025/admission_01/IMG_0001.json  # Procesada exitosamente
cat metadata/2025/admission_01/IMG_0002.json  # Sin rostros
cat metadata/2025/admission_01/IMG_0003.json  # Múltiples rostros
cat metadata/2025/admission_01/IMG_0004.json  # Error
cat metadata/2025/admission_01/batch_summary.json  # Resumen del lote
```

## Flujo de Clasificación

```
input_raw/
    └── imagen.jpg
         ↓
    [Validación]
         ↓
    [Detección Facial]
         ↓
    ┌────┴────┬──────────┬─────────┐
    │         │          │         │
  1 rostro  0 rostros  >1 rostros  error
    ↓         ↓          ↓         ↓
processed  manual_   manual_    errors/
           review    review
    ↓         ↓          ↓         ↓
prepared/  [revisar] [revisar]  [revisar]
```

## Troubleshooting

### Error: No module named 'dlib'

```bash
# Ver sección "Instalación de dlib" arriba
# O ejecutar primero: python test_pipeline.py
```

### No se encuentran imágenes

```bash
# Verificar estructura
tree input_raw/

# Debe ser: input_raw/YYYY/batch_name/*.jpg
```

### Permission denied en setup.sh

```bash
chmod +x setup.sh
./setup.sh
```

## Próximos Pasos

1. ✅ Estructura del proyecto creada
2. ✅ Código fuente implementado
3. ✅ Documentación completa
4. ✅ Ejemplos de metadatos
5. ⏭ Instalar dlib
6. ⏭ Probar con imágenes reales
7. ⏭ Ajustar parámetros según necesidades

## Soporte

- Documentación completa: `README.md`
- Diseño del flujo: `docs/metadata_flow.md`
- Logs del sistema: `logs/pipeline.log`

