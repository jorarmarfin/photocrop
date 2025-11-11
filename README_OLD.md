# PhotoCrop - Pipeline de Normalización de Fotos de Postulantes

Sistema automatizado para procesar y normalizar fotos de postulantes usando detección facial con dlib.

## Características

- ✅ Detección automática de rostros usando dlib
- ✅ Clasificación automática (procesado, revisión manual, error)
- ✅ Generación de metadatos JSON detallados
- ✅ Trazabilidad completa del procesamiento
- ✅ Organización jerárquica por año/lote
- ✅ Logging completo de operaciones

## Estructura del Proyecto

```
PhotoCrop/
├── src/
│   ├── core/
│   │   ├── metadata_manager.py    # Gestor de metadatos JSON
│   │   ├── face_detector.py       # Detector de rostros con dlib
│   │   └── image_processor.py     # Procesador de imágenes con Pillow
│   ├── utils/
│   │   ├── logger.py              # Sistema de logging
│   │   └── file_utils.py          # Utilidades de archivos
│   ├── pipeline.py                # Pipeline principal
│   └── main.py                    # Punto de entrada
├── input_raw/                     # Fotos originales (copiar aquí)
├── working/                       # Área de trabajo
├── prepared/                      # Fotos procesadas
├── manual_review/                 # Requieren revisión manual
├── errors/                        # Archivos con errores
├── metadata/                      # Metadatos JSON
├── logs/                          # Logs de ejecución
├── config/                        # Configuración
└── docs/                          # Documentación

```

## Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Nota sobre dlib:** En Ubuntu/Debian, puede ser necesario instalar dependencias del sistema:

```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

## Uso

### 1. Organizar fotos de entrada

Coloca tus fotos en `input_raw/` usando esta estructura:

```
input_raw/
└── 2025/
    └── admission_01/
        ├── IMG_0001.jpg
        ├── IMG_0002.jpg
        └── ...
```

### 2. Ejecutar el pipeline

```bash
cd src
python main.py
```

O directamente:

```bash
python src/main.py
```

### 3. Revisar resultados

- **Procesadas exitosamente:** `prepared/{año}/{lote}/`
- **Requieren revisión:** `manual_review/{año}/{lote}/`
- **Con errores:** `errors/{año}/{lote}/`
- **Metadatos:** `metadata/{año}/{lote}/`
- **Logs:** `logs/pipeline.log`

## Flujo de Procesamiento

1. **Escaneo:** Busca todas las imágenes en `input_raw/`
2. **Validación:** Verifica que los archivos sean válidos
3. **Detección facial:** Usa dlib para detectar rostros
4. **Clasificación:**
   - 1 rostro → `processed` → `prepared/`
   - 0 rostros → `manual_review`
   - Múltiples rostros → `manual_review`
   - Error → `errors/`
5. **Metadatos:** Genera JSON con información completa
6. **Resumen:** Crea `batch_summary.json` por lote

## Metadatos Generados

Cada imagen genera un archivo JSON con:

```json
{
  "filename": "IMG_0001.jpg",
  "status": "processed|manual_review|error|pending",
  "face_detected": true,
  "num_faces": 1,
  "face_box": [x, y, width, height],
  "width": 1920,
  "height": 2560,
  "orientation": "portrait|landscape|square",
  "processing_time": "2025-11-10T13:15:42Z",
  "batch_id": "admission_01",
  "processing_history": [...]
}
```

## Configuración

### Rutas (config/paths.json)

```json
{
  "paths": {
    "input_raw": "./input_raw",
    "metadata": "./metadata",
    "logs": "./logs",
    "errors": "./errors",
    "working": "./working",
    "prepared": "./prepared",
    "manual_review": "./manual_review"
  }
}
```

### Ajustes (config/settings.yml)

```yaml
standard_size:
  width: 300
  height: 400
face_threshold: 0.5
```

## Logs

El sistema genera logs detallados en `logs/pipeline.log`:

```
2025-11-10 13:15:42 - PhotoCropPipeline - INFO - Procesando: IMG_0001.jpg
2025-11-10 13:15:43 - PhotoCropPipeline - INFO - Rostros detectados: 1
2025-11-10 13:15:43 - PhotoCropPipeline - INFO - ✓ Metadata guardado
```

## Troubleshooting

### Error al instalar dlib

```bash
# Instalar cmake primero
pip install cmake
pip install dlib
```

### Imágenes no se procesan

- Verifica que estén en `input_raw/{año}/{lote}/`
- Revisa `logs/pipeline.log` para detalles
- Formatos soportados: JPG, PNG, BMP, TIFF

### No se detectan rostros

- Verifica la calidad de las imágenes
- Revisa imágenes en `manual_review/`
- Consulta metadatos JSON para detalles

## Desarrollo

### Ejecutar tests

```bash
# TODO: Agregar tests unitarios
pytest tests/
```

### Estructura de módulos

- `core/`: Componentes principales del sistema
- `utils/`: Utilidades auxiliares
- `pipeline.py`: Coordinador principal
- `main.py`: Punto de entrada

## Licencia

[Especificar licencia]

## Autor

[Tu nombre/organización]

## Changelog

### v1.0.0 (2025-11-10)
- Pipeline inicial con detección facial
- Generación de metadatos JSON
- Sistema de logging
- Clasificación automática de imágenes

