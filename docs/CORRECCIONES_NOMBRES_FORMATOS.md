# Correcciones Aplicadas - Manejo de Nombres y Formatos

## 🔧 Cambios Realizados

### 1. NO Cambiar Nombre de Archivos
**Problema anterior:** Se agregaba sufijo `_nobg` a los archivos  
**Solución:** Mantener el nombre original del archivo en todo el proceso

#### Archivos Modificados:
- `src/core/background_remover.py` - Línea ~127
- `src/processor_with_bg_removal.py` - Todo el flujo

**Antes:**
```python
output_name = img_path.stem + '_nobg.jpg'  # ❌ Cambiaba nombre
```

**Después:**
```python
output_name = img_path.stem + '.jpg'  # ✅ Mantiene nombre original
```

---

### 2. Conversión al Formato Original

**Problema:** Al quitar fondo, todas las imágenes se convertían a JPG, perdiendo el formato original (PNG, BMP, etc.)

**Solución:** Nuevo módulo que convierte las imágenes al formato original basándose en metadata

#### Nuevo Módulo Creado:
**Archivo:** `src/core/format_converter.py`

**Características:**
- Lee formato original desde metadata JSON
- Convierte imagen al formato correcto
- Mantiene calidad alta (95% JPEG)
- Maneja transparencias correctamente
- Procesamiento individual o por lotes

---

### 3. Comando por Consola para Conversión

**Nuevo Script:** `convert_to_original_format.sh`

**Uso:**
```bash
# Sintaxis básica
./convert_to_original_format.sh <carpeta_origen> <carpeta_destino>

# Ejemplo: Convertir de prepared/ a output/
./convert_to_original_format.sh ./prepared ./output

# Ejemplo: De white/ a output_final/
./convert_to_original_format.sh ./white ./output_final

# Con metadata personalizado
./convert_to_original_format.sh ./white ./output_final ./metadata 95
```

**También disponible en Python:**
```bash
python src/core/format_converter.py ./white ./output_final --metadata-dir ./metadata --quality 95
```

---

## 📂 Flujo Actualizado

### Flujo Completo con Nombres Originales

```
ENTRADA:
./input_raw/
    ├── foto001.jpg
    ├── imagen002.png
    └── postulante003.jpeg

↓ [Detección + Recorte]

./working/faces_cropped/
    ├── foto001.jpg         ✅ Mismo nombre
    ├── imagen002.png       ✅ Mismo nombre
    └── postulante003.jpeg  ✅ Mismo nombre

↓ [Eliminación de Fondo]

./prepared/ (o ./white/)
    ├── foto001.jpg         ✅ Fondo blanco, formato JPG temporal
    ├── imagen002.jpg       ✅ Fondo blanco, formato JPG temporal
    └── postulante003.jpg   ✅ Fondo blanco, formato JPG temporal

↓ [Conversión a Formato Original] ← NUEVO PROCESO

./output/ (o ./output_final/)
    ├── foto001.jpg         ✅ Formato original (JPG)
    ├── imagen002.png       ✅ Formato original (PNG) ← CONVERTIDO
    └── postulante003.jpeg  ✅ Formato original (JPEG) ← CONVERTIDO
```

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Procesamiento Completo Integrado
```bash
# Procesar con eliminación de fondo
python src/processor_with_bg_removal.py --batch-id admission_2025

# Resultado:
# - Nombres originales mantenidos ✅
# - Formatos originales restaurados ✅
# - Archivos en ./output/ listos
```

### Ejemplo 2: Conversión Manual Posterior
```bash
# Si tienes fotos en ./white/ y quieres convertir a ./output_final/
./convert_to_original_format.sh ./white ./output_final

# O con Python
python src/core/format_converter.py ./white ./output_final
```

### Ejemplo 3: Solo Eliminar Fondo (Sin Conversión)
```bash
# Procesar una imagen
python src/core/background_remover.py foto.jpg salida.jpg --color white

# Resultado: salida.jpg (mismo nombre base, formato JPG)
```

### Ejemplo 4: Conversión por Lotes
```bash
# Convertir todas las fotos de prepared/ al formato original
python src/core/format_converter.py ./prepared ./output_final --quality 95
```

---

## 📋 Detección de Formato Original

El sistema detecta el formato original de 2 formas:

### 1. Desde Metadata (Preferido)
```json
{
  "filename": "imagen002.png",
  "format": "PNG",
  ...
}
```
El conversor lee el campo `format` del metadata JSON.

### 2. Desde Extensión del Archivo (Fallback)
Si no hay metadata, usa la extensión original del archivo:
- `imagen002.png` → Convierte a PNG
- `foto001.jpg` → Convierte a JPG

---

## 🔄 Conversiones Soportadas

| Formato Origen | Formato Destino | Conversión |
|----------------|-----------------|------------|
| JPG → JPG | No requiere | Copia directa |
| JPG → PNG | Sí | Convierte a PNG |
| JPG → BMP | Sí | Convierte a BMP |
| JPG → TIFF | Sí | Convierte a TIFF |
| JPG (con alpha) → JPG | Sí | Aplica fondo blanco |

**Manejo de Transparencias:**
- Si formato destino es JPG/JPEG → Aplica fondo blanco automáticamente
- Si formato destino es PNG → Mantiene transparencia si existe

---

## 🎨 Integración con Procesador

El procesador actualizado (`processor_with_bg_removal.py`) ahora:

1. ✅ **Mantiene nombre original** del archivo en todo momento
2. ✅ **Guarda formato original** en metadata
3. ✅ **Convierte automáticamente** al formato original en output
4. ✅ **Detecta formato** desde metadata o extensión

```python
# Ejemplo de uso
processor = PhotoProcessorWithBgRemoval(
    enable_bg_removal=True,
    background_color=(255, 255, 255, 255)
)

stats = processor.run(batch_id="test_2025")

# Resultado en ./output/:
# - Nombres originales ✅
# - Formatos originales ✅
# - Fondo blanco aplicado ✅
```

---

## 📝 Metadata Actualizado

El metadata ahora incluye formato original:

```json
{
  "filename": "imagen002.png",
  "format": "PNG",
  "original_extension": ".png",
  "input_path": "./input_raw/imagen002.png",
  "current_path": "./output/imagen002.png",
  "output_path": "./output/imagen002.png",
  "background_removed": true,
  "background_color": "white",
  "format_converted": true,
  "conversion_details": {
    "from": "JPEG",
    "to": "PNG",
    "quality": 95
  }
}
```

---

## 🚀 Comandos Rápidos

### Conversión de Prepared a Output
```bash
./convert_to_original_format.sh ./prepared ./output
```

### Conversión de White a Output Final
```bash
./convert_to_original_format.sh ./white ./output_final
```

### Con Calidad Personalizada
```bash
./convert_to_original_format.sh ./prepared ./output ./metadata 98
```

### Usando Python Directamente
```bash
python src/core/format_converter.py ./white ./output_final --quality 95
```

---

## ✅ Verificación de Correcciones

### Test 1: Verificar que NO se cambian nombres
```bash
# Copiar imagen
cp test.jpg input_raw/

# Procesar
python src/processor_with_bg_removal.py

# Verificar nombre en output
ls output/test.jpg  # ✅ Debe existir (mismo nombre)
ls output/test_nobg.jpg  # ❌ NO debe existir
```

### Test 2: Verificar conversión de formato
```bash
# Copiar PNG
cp imagen.png input_raw/

# Procesar
python src/processor_with_bg_removal.py

# Verificar formato en output
file output/imagen.png  # Debe decir "PNG image data"
```

### Test 3: Conversión manual
```bash
# Preparar directorio con JPGs
mkdir -p test_white
cp prepared/*.jpg test_white/

# Convertir a formatos originales
./convert_to_original_format.sh test_white test_output

# Verificar
ls -lh test_output/
```

---

## 📊 Resumen de Archivos Creados/Modificados

### Archivos Modificados
1. `src/core/background_remover.py`
   - Línea ~127: Eliminado sufijo `_nobg`
   - Mantiene nombre original

2. `src/processor_with_bg_removal.py`
   - Agregado import de `FormatConverter`
   - Detección de formato original
   - Conversión automática en output

### Archivos Nuevos
1. `src/core/format_converter.py`
   - Clase `FormatConverter`
   - Conversión basada en metadata
   - CLI integrado

2. `convert_to_original_format.sh`
   - Script bash para conversión por consola
   - Sintaxis simple
   - Manejo de errores

3. `docs/CORRECCIONES_NOMBRES_FORMATOS.md`
   - Este documento

---

## 🎉 Resultado Final

### Antes de las Correcciones
```
input_raw/imagen.png → output/imagen_nobg.jpg  ❌
- Nombre cambiado ❌
- Formato cambiado de PNG a JPG ❌
```

### Después de las Correcciones
```
input_raw/imagen.png → output/imagen.png  ✅
- Nombre original mantenido ✅
- Formato original restaurado (PNG) ✅
- Fondo blanco aplicado ✅
```

---

## 📞 Uso en Producción

### Flujo Recomendado

1. **Procesar fotos** (recorte + fondo blanco)
   ```bash
   python src/processor_with_bg_removal.py --batch-id admission_2025
   ```

2. **Verificar output**
   ```bash
   ls -lh output/
   ```

3. **Si necesitas conversión adicional**
   ```bash
   ./convert_to_original_format.sh ./output ./output_final
   ```

### Carpetas a Usar

- **input_raw/** - Fotos originales
- **working/** - Procesamiento temporal
- **prepared/** o **white/** - Fotos con fondo blanco (JPG)
- **output/** - Fotos finales con formato original ✅

---

**Fecha de correcciones:** 2025-11-11  
**Estado:** ✅ COMPLETADO Y PROBADO

