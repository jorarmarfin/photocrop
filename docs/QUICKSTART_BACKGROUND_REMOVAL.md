# Guía Rápida: Eliminación de Fondo con IA

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalación
```bash
cd /home/lmayta/PycharmProjects/PhotoCrop
source .venv/bin/activate
./install_background_removal.sh
```

### 2. Test de Verificación
```bash
python test_background_removal.py
```

### 3. Uso Básico
```bash
# Procesar UNA imagen
python src/core/background_remover.py foto.jpg foto_nobg.jpg --color white

# Procesar TODO el directorio
python src/processor_with_bg_removal.py --batch-id test_2025
```

---

## 📋 Comandos Principales

### Procesamiento Individual
```bash
# Fondo blanco
python src/core/background_remover.py input.jpg output.jpg --color white

# Fondo transparente (PNG)
python src/core/background_remover.py input.jpg output.png --color transparent

# Fondo gris institucional
python src/core/background_remover.py input.jpg output.jpg --color gray
```

### Procesamiento por Lotes
```bash
# Con fondo blanco
python src/processor_with_bg_removal.py --batch-id admission_2025

# Sin eliminación de fondo (solo recorte)
python src/processor_with_bg_removal.py --no-bg-removal

# Con fondo gris
python src/processor_with_bg_removal.py --bg-color gray

# Con limpieza automática
python src/processor_with_bg_removal.py --auto-clean
```

---

## 📂 Flujo de Carpetas

```
input_raw/                  # Fotos originales aquí
    └── foto.jpg
         │
         ↓ [Detección + Recorte]
         │
working/faces_cropped/      # Rostros recortados (temporal)
    └── foto.jpg
         │
         ↓ [Eliminación de Fondo] ← NUEVA ETAPA
         │
prepared/                   # Fotos con fondo blanco
    └── foto.jpg
         │
         ↓ [Control de Calidad]
         │
output/                     # Fotos finales listas
    └── foto.jpg
```

---

## 🎨 Colores Disponibles

| Color | Código | Uso |
|-------|--------|-----|
| `white` | RGB(255, 255, 255) | Pasaporte, DNI |
| `gray` | RGB(240, 240, 240) | Institucional |
| `institutional` | RGB(235, 235, 235) | Corporativo |
| `transparent` | PNG transparente | Edición posterior |

---

## 📊 Ejemplo de Salida

### Procesamiento Exitoso
```bash
$ python src/processor_with_bg_removal.py

================================================================================
INICIO DE PROCESADOR DETERMINISTA
================================================================================
Configuración cargada desde: ./config/paths.json
✓ BackgroundRemover inicializado
Inicialización completada

2. ESCANEO DE ENTRADA
Total de archivos encontrados: 3

3. FILTRADO DE ARCHIVOS NUEVOS
Archivos nuevos a procesar: 3

4. PROCESAMIENTO DE ARCHIVOS NUEVOS

Procesando: foto1.jpg
  ✓ Un rostro detectado
  ✓ Aplicando recorte...
  🎨 Removiendo fondo con IA...
  ✓ Fondo removido: ./prepared/foto1.jpg
  ✓ Imagen procesada exitosamente → output/foto1.jpg

Procesando: foto2.jpg
  ✓ Un rostro detectado
  ✓ Aplicando recorte...
  🎨 Removiendo fondo con IA...
  ✓ Fondo removido: ./prepared/foto2.jpg
  ✓ Imagen procesada exitosamente → output/foto2.jpg

7. RESUMEN DE PROCESAMIENTO
Total encontrados: 3
Procesados: 3
Revisión manual: 0
Errores: 0

RESUMEN CON ELIMINACIÓN DE FONDO
Eliminación de fondo: ✓ Activada
Color de fondo: white
Total procesadas: 3
```

---

## 🔧 Troubleshooting Rápido

### Error: "No module named 'rembg'"
```bash
source .venv/bin/activate
pip install rembg
```

### Error: Modelo no descargado
```bash
# Primera ejecución descarga automáticamente
python test_background_removal.py
```

### Procesamiento muy lento
```bash
# Procesar en lotes más pequeños
# O instalar versión GPU:
pip install rembg[gpu]
```

### Ver logs detallados
```bash
tail -f logs/pipeline.log
```

---

## 📖 Documentación Completa

- **Integración técnica:** `docs/INTEGRACION_ELIMINACION_FONDO.md`
- **Flujo de procesamiento:** `docs/FLUJO_PROCESAMIENTO.md`
- **Mejoras del algoritmo:** `docs/MEJORA_ALGORITMO_CABELLO.md`

---

## ✅ Checklist de Verificación

- [ ] Entorno virtual activado
- [ ] rembg instalado (`pip list | grep rembg`)
- [ ] Modelo descargado (`ls ~/.u2net/`)
- [ ] Test pasado (`python test_background_removal.py`)
- [ ] Carpetas creadas (`ls working/ prepared/ output/`)
- [ ] Primera imagen procesada exitosamente

---

## 🎯 Próximos Pasos

1. **Procesar lote de prueba:**
   ```bash
   cp test_photos/*.jpg input_raw/
   python src/processor_with_bg_removal.py
   ```

2. **Revisar resultados:**
   ```bash
   ls -lh output/
   cat metadata/2025/*/foto1.json
   ```

3. **Ajustar configuración:**
   - Editar `src/processor_with_bg_removal.py`
   - Cambiar `background_color` según necesidad
   - Activar/desactivar con `--no-bg-removal`

---

**¿Listo para producción?** ✅

Copiar fotos en `input_raw/` y ejecutar:
```bash
python src/processor_with_bg_removal.py --batch-id produccion_2025
```

