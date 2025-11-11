# Integración de Eliminación de Fondo con IA

## Enfoque y Modelo Usado

### Librería: rembg
- **Modelo:** U2-Net (U-Square Net)
- **Licencia:** MIT (open source)
- **Características:**
  - Funciona 100% offline después de descarga inicial del modelo
  - Precisión alta en detección de personas
  - Procesamiento rápido (GPU opcional)
  - Sin dependencias de servicios externos

### Modelo U2-Net
- Red neuronal especializada en segmentación de primer plano
- Entrenada con 15,000+ imágenes de personas
- Tamaño del modelo: ~176 MB
- Descarga automática en primera ejecución
- Almacenado localmente en `~/.u2net/`

---

## Instalación en Entorno Virtual

### Paso 1: Activar entorno virtual
```bash
cd /home/lmayta/PycharmProjects/PhotoCrop
source .venv/bin/activate
```

### Paso 2: Instalar rembg
```bash
# Instalación básica (CPU)
pip install rembg

# Instalación con GPU (CUDA - opcional, más rápido)
pip install rembg[gpu]

# Verificar instalación
python -c "from rembg import remove; print('OK')"
```

### Paso 3: Descarga inicial del modelo
```bash
# Primera ejecución descarga modelo automáticamente (~176 MB)
# El modelo se guarda en ~/.u2net/ para uso offline
python -c "from rembg import remove; print('Modelo descargado')"
```

### Dependencias adicionales
```bash
# Si hay problemas con dependencias
pip install pillow numpy onnxruntime
```

---

## Ejemplo de Uso por Consola

### Uso Básico
```bash
# Remover fondo con fondo blanco
python src/core/background_remover.py input.jpg output.jpg --color white

# Remover fondo con transparencia
python src/core/background_remover.py input.jpg output.png --color transparent

# Remover fondo con gris institucional
python src/core/background_remover.py input.jpg output.jpg --color gray
```

### Procesamiento por Lotes
```bash
# Procesar todos los archivos de un directorio
python src/core/background_remover.py ./input_dir/ ./output_dir/ --batch --color white

# Con color personalizado
python src/core/background_remover.py ./input_dir/ ./output_dir/ --batch --color institutional
```

### Colores Disponibles
- `transparent` - Fondo transparente (PNG)
- `white` - Blanco puro (255, 255, 255)
- `gray` - Gris claro (240, 240, 240)
- `light_gray` - Gris muy claro (245, 245, 245)
- `institutional` - Gris institucional (235, 235, 235)

---

## Ejemplo de Uso desde Python

### Uso Individual
```python
from pathlib import Path
from core.background_remover import BackgroundRemover

# Inicializar removedor
remover = BackgroundRemover()

# Remover fondo con blanco
success = remover.remove_background(
    input_path=Path("input.jpg"),
    output_path=Path("output.jpg"),
    background_color=(255, 255, 255, 255)  # RGBA blanco
)

# Remover fondo con transparencia
success = remover.remove_background(
    input_path=Path("input.jpg"),
    output_path=Path("output.png"),
    background_color=None  # Transparente
)
```

### Uso por Lotes
```python
from pathlib import Path
from core.background_remover import BackgroundRemover

remover = BackgroundRemover()

# Procesar directorio completo
stats = remover.process_batch(
    input_dir=Path("./prepared/"),
    output_dir=Path("./output/"),
    background_color=(255, 255, 255, 255),  # Blanco
    extensions=['.jpg', '.jpeg', '.png']
)

print(f"Procesadas: {stats['success']}/{stats['total']}")
print(f"Fallidas: {stats['failed']}")
```

### Función Helper Simplificada
```python
from core.background_remover import remove_background_from_image

# Uso simple con string de color
success = remove_background_from_image(
    input_path="foto.jpg",
    output_path="foto_nobg.jpg",
    background_color="white"  # o "transparent", "gray", etc.
)
```

---

## Pseudocódigo del Flujo Integrado

### Flujo Completo con Eliminación de Fondo

```pseudocode
INICIO PROCESAMIENTO CON REMOCIÓN DE FONDO

1. ESCANEO Y VALIDACIÓN
   - Escanear ./input_raw/
   - Filtrar archivos ya procesados
   - Validar imágenes

2. DETECCIÓN Y RECORTE FACIAL
   - Detectar rostros con dlib
   - Calcular crop_box con márgenes
   - Aplicar recorte
   - Guardar en ./working/faces_cropped/

3. ELIMINACIÓN DE FONDO [NUEVA ETAPA]
   PARA cada imagen en ./working/faces_cropped/:
   
   3.1 Cargar BackgroundRemover
       remover = BackgroundRemover()
   
   3.2 Definir color de fondo
       SI configuración.background_removal == true:
         background_color = configuración.bg_color  # (255, 255, 255, 255) blanco
       SINO:
         SALTAR esta etapa
   
   3.3 Procesar imagen
       input_path = ./working/faces_cropped/foto.jpg
       output_path = ./prepared/foto_nobg.jpg
       
       success = remover.remove_background(
         input_path,
         output_path,
         background_color
       )
   
   3.4 Actualizar metadata
       SI success:
         metadata["background_removed"] = true
         metadata["background_color"] = "white"  # o el color usado
         metadata["prepared_path"] = str(output_path)
         metadata["processing_history"].append({
           "timestamp": now(),
           "action": "background_removed",
           "status": "success",
           "background_color": "white"
         })
       SINO:
         metadata["background_removed"] = false
         metadata["error_message"] = "Error al remover fondo"
         # Usar imagen original sin remoción de fondo

4. CONTROL DE CALIDAD
   - Validar dimensiones finales
   - Verificar formato (JPG con fondo, PNG sin fondo)
   - Guardar metadata actualizado

5. SALIDA FINAL
   SI background_removed == true:
     - Copiar de ./prepared/ a ./output/
     - Formato: JPG con fondo de color
   SINO:
     - Copiar imagen recortada directamente a ./output/

6. RESUMEN
   - Total procesadas
   - Con fondo removido: X
   - Sin fondo removido: Y
   - Errores: Z

FIN PROCESAMIENTO
```

### Integración con Carpetas

```
FLUJO DE CARPETAS:

./input_raw/
    └── foto_001.jpg (original)
         │
         ↓ [DETECCIÓN + RECORTE]
         │
./working/faces_cropped/
    └── foto_001_cropped.jpg (rostro recortado)
         │
         ↓ [ELIMINACIÓN DE FONDO] ← NUEVA ETAPA
         │
./prepared/
    └── foto_001_nobg.jpg (sin fondo, fondo blanco)
         │
         ↓ [CONTROL DE CALIDAD]
         │
./output/
    └── foto_001_final.jpg (listo para uso)


ALTERNATIVA SIN REMOCIÓN:
./input_raw/ → [DETECCIÓN + RECORTE] → ./output/
```

---

## Ejemplo de Actualización de Metadatos

### Metadata Completo con Background Removal

```json
{
  "filename": "foto_001.jpg",
  "input_path": "./input_raw/foto_001.jpg",
  "current_path": "./output/foto_001_final.jpg",
  "output_path": "./output/foto_001_final.jpg",
  "format": "JPEG",
  "width": 600,
  "height": 800,
  "orientation": "portrait",
  "face_detected": true,
  "num_faces": 1,
  "face_box": [120, 200, 300, 300],
  "status": "processed",
  "error_message": null,
  "processing_time": "2025-11-11T10:30:45.123456Z",
  "batch_id": "admission_2025_01",
  "notes": null,
  "metadata_version": "1.0",
  "last_updated": "2025-11-11T10:30:48.789012Z",
  "background_removed": true,
  "background_color": "white",
  "background_removal_model": "u2net",
  "prepared_path": "./prepared/foto_001_nobg.jpg",
  "processing_history": [
    {
      "timestamp": "2025-11-11T10:30:45.123456Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-11T10:30:46.456789Z",
      "action": "face_detected_and_cropped",
      "status": "processed",
      "details": "Recorte aplicado exitosamente"
    },
    {
      "timestamp": "2025-11-11T10:30:47.891234Z",
      "action": "background_removed",
      "status": "success",
      "background_color": "white",
      "model": "u2net"
    },
    {
      "timestamp": "2025-11-11T10:30:48.789012Z",
      "action": "final_output",
      "status": "processed",
      "details": "Imagen final lista"
    }
  ]
}
```

### Metadata SIN Background Removal (opcional)

```json
{
  "filename": "foto_002.jpg",
  "status": "processed",
  "background_removed": false,
  "background_color": null,
  "processing_history": [
    {
      "timestamp": "2025-11-11T10:31:45.123456Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-11T10:31:46.456789Z",
      "action": "face_detected_and_cropped",
      "status": "processed",
      "details": "Recorte aplicado, fondo original mantenido"
    }
  ]
}
```

---

## Configuración del Sistema

### Archivo de Configuración (config/settings.yml)

```yaml
background_removal:
  enabled: true  # Activar/desactivar remoción de fondo
  color: "white"  # Color de fondo: white, gray, transparent
  model: "u2net"  # Modelo a usar
  batch_size: 10  # Procesar N imágenes a la vez
  
output:
  format: "jpg"  # jpg o png
  quality: 95  # Calidad JPEG (1-100)
  
paths:
  working_cropped: "./working/faces_cropped"
  prepared: "./prepared"
  output: "./output"
```

### Archivo de Configuración Alternativo (config/background.json)

```json
{
  "background_removal": {
    "enabled": true,
    "default_color": "white",
    "colors": {
      "white": [255, 255, 255, 255],
      "gray": [240, 240, 240, 255],
      "institutional": [235, 235, 235, 255]
    },
    "model": "u2net",
    "model_path": "~/.u2net/"
  }
}
```

---

## Integración con Sistema Actual

### Modificar deterministic_processor.py

```python
# Agregar import
from core.background_remover import BackgroundRemover

class DeterministicPhotoProcessor:
    
    def __init__(self, config_path: str = "./config/paths.json"):
        # ...existing code...
        
        # Agregar removedor de fondo
        self.background_remover = BackgroundRemover()
        self.enable_bg_removal = True  # Leer de config
        self.bg_color = (255, 255, 255, 255)  # Blanco por defecto
    
    def _process_successful_crop(self, img_path, img, metadata, batch_id, crop_box):
        """Procesamiento con eliminación de fondo integrada"""
        
        # 1. Aplicar recorte
        cropped_img = img.crop(crop_box)
        
        # 2. Guardar en working/faces_cropped
        working_dir = Path("./working/faces_cropped")
        working_dir.mkdir(parents=True, exist_ok=True)
        cropped_path = working_dir / img_path.name
        cropped_img.save(cropped_path, 'JPEG', quality=95)
        
        # 3. ELIMINACIÓN DE FONDO (nueva etapa)
        if self.enable_bg_removal:
            prepared_dir = Path("./prepared")
            prepared_dir.mkdir(parents=True, exist_ok=True)
            prepared_path = prepared_dir / img_path.name
            
            success = self.background_remover.remove_background(
                input_path=cropped_path,
                output_path=prepared_path,
                background_color=self.bg_color
            )
            
            if success:
                metadata["background_removed"] = True
                metadata["background_color"] = "white"
                metadata["prepared_path"] = str(prepared_path)
                final_source = prepared_path
            else:
                metadata["background_removed"] = False
                final_source = cropped_path
        else:
            final_source = cropped_path
            metadata["background_removed"] = False
        
        # 4. Copiar a output final
        output_dir = Path(self.paths["output"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / img_path.name
        shutil.copy2(final_source, output_path)
        
        # 5. Actualizar metadata
        metadata["current_path"] = str(output_path)
        metadata["output_path"] = str(output_path)
        metadata["status"] = "processed"
        
        # ...existing code...
```

---

## Testing y Validación

### Test Individual
```bash
# Activar entorno
source .venv/bin/activate

# Test simple
python src/core/background_remover.py test_input.jpg test_output.jpg --color white

# Verificar resultado
ls -lh test_output.jpg
```

### Test por Lotes
```bash
# Preparar directorio de prueba
mkdir -p test_batch_input test_batch_output
cp input_raw/*.jpg test_batch_input/

# Ejecutar batch
python src/core/background_remover.py test_batch_input/ test_batch_output/ --batch --color white

# Ver resultados
ls -lh test_batch_output/
```

### Test desde Python
```python
# test_bg_removal.py
from core.background_remover import BackgroundRemover
from pathlib import Path

remover = BackgroundRemover()

# Test 1: Fondo blanco
success = remover.remove_background(
    Path("test.jpg"),
    Path("test_white.jpg"),
    (255, 255, 255, 255)
)
print(f"Test blanco: {'OK' if success else 'FAIL'}")

# Test 2: Fondo transparente
success = remover.remove_background(
    Path("test.jpg"),
    Path("test_transparent.png"),
    None
)
print(f"Test transparente: {'OK' if success else 'FAIL'}")
```

---

## Troubleshooting

### Error: ModuleNotFoundError: No module named 'rembg'
```bash
source .venv/bin/activate
pip install rembg
```

### Error: No se descarga el modelo
```bash
# Forzar descarga
python -c "from rembg import remove; import requests; print('OK')"

# Verificar conexión en primera ejecución
# Después funciona 100% offline
```

### Error: Modelo no encontrado
```bash
# Verificar ubicación del modelo
ls -la ~/.u2net/

# Re-descargar si es necesario
rm -rf ~/.u2net/
python -c "from rembg import remove; print('Modelo re-descargado')"
```

### Rendimiento Lento
```bash
# Instalar versión GPU (requiere CUDA)
pip install rembg[gpu]

# O procesar por lotes más pequeños
# Ajustar batch_size en configuración
```

---

## Ventajas del Enfoque

### Ventajas Técnicas
- ✅ 100% offline después de descarga inicial
- ✅ No requiere API keys ni servicios externos
- ✅ Modelo de código abierto (MIT)
- ✅ Alta precisión en personas
- ✅ Procesamiento rápido
- ✅ Integración simple con flujo existente

### Ventajas Operativas
- ✅ Sin costos recurrentes
- ✅ Sin límites de procesamiento
- ✅ Privacidad garantizada (datos locales)
- ✅ Configurable por lote
- ✅ Múltiples opciones de color de fondo

---

## Alternativas

### Alternativa 1: remove.bg CLI (NO OFFLINE)
- Requiere API key
- Requiere internet
- Costo por imagen
- ❌ No cumple requisito offline

### Alternativa 2: DeepLabV3+ (PyTorch)
- Más complejo de configurar
- Requiere más dependencias
- Similar precisión
- ⚠️ Más pesado que rembg

### Alternativa 3: Selección manual (Photoshop/GIMP)
- 100% preciso
- Muy lento
- No escalable
- ❌ No automatizado

**Recomendación:** rembg es la mejor opción para este caso de uso.

