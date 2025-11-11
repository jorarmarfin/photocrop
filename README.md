# PhotoCrop - Sistema Completo de Procesamiento de Fotos con IA

Sistema automatizado profesional para procesar, normalizar y preparar fotos de postulantes usando inteligencia artificial y visión por computadora.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🎯 Características Principales

### 🤖 Procesamiento Automático con IA
- ✅ **Detección facial** con dlib (modelo HOG + CNN)
- ✅ **Recorte inteligente** con márgenes optimizados (80% extra para cabello)
- ✅ **Eliminación de fondo** usando IA (modelo U2-Net - rembg)
- ✅ **Aplicación de fondo blanco** institucional
- ✅ **Conversión a formato original** (JPG, PNG, BMP, TIFF)
- ✅ **Clasificación automática** (exitosas, revisión manual, errores)

### 🌐 Dashboard Web Interactivo
- 📊 **Interfaz web moderna** con FastAPI
- 🔄 **Estadísticas en tiempo real** (actualización cada 5 segundos)
- 🎨 **Visualización de carpetas** con 6 tabs interactivos
- 📋 **Visor de logs** en tiempo real con scroll automático
- 🚀 **Procesamiento con un click** desde el navegador
- 📱 **Diseño responsive** para móviles y tablets

### 📊 Gestión y Trazabilidad
- 📝 **Metadatos JSON detallados** para cada imagen
- 🔄 **Re-ejecución segura** (no reprocesa archivos ya procesados)
- 📂 **Organización jerárquica** por año/lote
- 📊 **Historial completo** de procesamiento
- 🔍 **Logging exhaustivo** de operaciones
- ⚡ **Índice de procesados** (processed_index.json)

### 🛠️ Herramientas de Mantenimiento
- 🧹 **Limpieza del sistema** con confirmación
- 📊 **Verificación de estado** del sistema
- 🔧 **Scripts automatizados** de instalación
- 📚 **Documentación completa** (15+ documentos)

---

## 📁 Estructura del Proyecto

```
PhotoCrop/
├── src/
│   ├── core/
│   │   ├── metadata_manager.py       # Gestión de metadatos JSON
│   │   ├── face_detector.py          # Detección facial (dlib)
│   │   ├── image_processor.py        # Procesamiento de imágenes
│   │   ├── background_remover.py     # Eliminación de fondo (IA)
│   │   └── format_converter.py       # Conversión de formatos
│   ├── utils/
│   │   ├── logger.py                 # Sistema de logging
│   │   └── file_utils.py             # Utilidades de archivos
│   ├── webapp/
│   │   ├── app.py                    # Dashboard web (FastAPI)
│   │   ├── templates/index.html      # Interfaz HTML5
│   │   └── static/style.css          # Estilos CSS3
│   ├── deterministic_processor.py    # Procesador base
│   ├── processor_with_bg_removal.py  # Procesador con IA
│   └── main.py                       # CLI principal
│
├── input_raw/                        # 📥 Fotos originales
├── working/faces_cropped/            # ⚙️ Rostros recortados (temp)
├── prepared/                         # 🎨 Procesadas intermedias
├── output_white/                     # ⚪ Con fondo blanco (JPG)
├── output/                           # ✅ Recortadas finales
├── output_final/                     # 🎯 Formato original final
├── manual_review/                    # ⚠️ Revisión manual
├── errors/                           # ❌ Con errores
├── metadata/                         # 📊 Metadatos + índice
├── logs/                             # 📋 Logs del sistema
├── config/                           # ⚙️ Configuración JSON/YAML
├── docs/                             # 📚 Documentación completa
│
├── start_webapp.sh                   # 🚀 Iniciar dashboard
├── clean_system.py                   # 🧹 Limpiar sistema
├── setup.sh                          # 📦 Instalación
├── requirements.txt                  # 📋 Dependencias
└── README.md                         # 📖 Este archivo
```

---

## 🚀 Instalación Rápida

### 1. Clonar o Descargar el Proyecto
```bash
cd /home/tu_usuario/
git clone <repo_url> PhotoCrop
cd PhotoCrop
```

### 2. Ejecutar Instalación Automática
```bash
./setup.sh
```

Esto instalará:
- Entorno virtual Python (.venv)
- dlib (detección facial)
- rembg (eliminación de fondo)
- FastAPI (dashboard web)
- Todas las dependencias

### 3. Verificar Instalación
```bash
./verify_project.sh
```

---

## 💡 Uso del Sistema

### Opción 1: Dashboard Web (Recomendado) 🌐

#### Iniciar el Dashboard
```bash
./start_webapp.sh
```

**Opciones del menú:**
1. Iniciar Dashboard Web
2. Limpiar sistema
3. Salir

#### Acceder
```
🌐 http://localhost:8000
```

**Funcionalidades del Dashboard:**
- ✅ Botón "Procesar Nuevas Fotos"
- 📊 6 contadores en tiempo real
- 📂 Visualización de 6 carpetas
- 📋 Logs en tiempo real
- 🔄 Auto-refresh cada 5 segundos

---

### Opción 2: Línea de Comandos 💻

#### Procesamiento Completo con IA
```bash
source .venv/bin/activate
python src/processor_with_bg_removal.py --batch-id admission_2025
```

**Opciones disponibles:**
```bash
--batch-id <id>        # ID del lote
--no-bg-removal        # Sin eliminar fondo
--bg-color white       # Color de fondo (white/gray/institutional)
--auto-clean           # Limpiar input_raw después
```

#### Procesamiento sin Eliminación de Fondo
```bash
python src/processor_with_bg_removal.py --no-bg-removal
```

#### Solo Eliminar Fondo
```bash
python src/core/background_remover.py input.jpg output.jpg --color white
```

#### Convertir a Formato Original
```bash
./convert_to_original_format.sh ./output_white ./output_final
```

O con Python:
```bash
python src/core/format_converter.py ./output_white ./output_final --quality 95
```

---

## 🔄 Flujo de Procesamiento

### Flujo Completo (Con IA)

```
1. Usuario copia fotos → ./input_raw/

2. Procesamiento automático:
   ┌─────────────────────────────────────┐
   │ input_raw/foto.jpg                  │
   └─────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────────┐
   │ Detección facial (dlib)             │
   │ • 1 rostro → continuar              │
   │ • 0 rostros → manual_review         │
   │ • 2+ rostros → manual_review        │
   └─────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────────┐
   │ Recorte inteligente                 │
   │ • 80% margen superior (cabello)     │
   │ • Aspect ratio 3:4 (pasaporte)      │
   │ • working/faces_cropped/foto.jpg    │
   └─────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────────┐
   │ Eliminación de fondo (U2-Net AI)    │
   │ • Segmentación de persona           │
   │ • Aplicar fondo blanco              │
   │ • output_white/foto.jpg             │
   └─────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────────┐
   │ Conversión a formato original       │
   │ • Lee metadata JSON                 │
   │ • Convierte JPG → PNG/BMP/etc       │
   │ • output_final/foto.png             │
   └─────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────────┐
   │ Metadata JSON                       │
   │ • metadata/2025/admission_01/       │
   │ • processed_index.json actualizado  │
   └─────────────────────────────────────┘

3. Resultados disponibles en:
   • output_final/ → Fotos listas
   • manual_review/ → Para revisar
   • errors/ → Con problemas
```

---

## 🧹 Limpieza del Sistema

### Limpiar Todo (Resetear)
```bash
python clean_system.py
```

O desde el menú:
```bash
./start_webapp.sh
# Opción 2: Limpiar sistema
```

**Se eliminará:**
- ✓ Fotos en output, output_white, output_final
- ✓ Fotos en manual_review y errors
- ✓ Archivos temporales (working, prepared)
- ✓ Metadatos generados
- ✓ Índice de procesados
- ✓ Logs del sistema

**Se preservará:**
- ✓ Fotos en input_raw
- ✓ Configuración
- ✓ Documentación

### Ver Estado Actual
```bash
python clean_system.py --status
```

### Limpieza Sin Confirmación (Forzada)
```bash
python clean_system.py --force
```

---

## 📊 Metadatos Generados

Cada foto procesada genera un archivo JSON con información completa:

```json
{
  "filename": "foto001.jpg",
  "input_path": "./input_raw/foto001.jpg",
  "output_path": "./output_final/foto001.jpg",
  "format": "JPEG",
  "width": 1200,
  "height": 1600,
  "orientation": "portrait",
  "face_detected": true,
  "num_faces": 1,
  "face_box": [400, 500, 600, 700],
  "status": "processed",
  "background_removed": true,
  "background_color": "white",
  "background_removal_model": "u2net",
  "processing_time": "2025-11-11T10:30:45Z",
  "batch_id": "admission_2025_01",
  "processing_history": [
    {
      "timestamp": "2025-11-11T10:30:45Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-11T10:30:46Z",
      "action": "face_detected_and_cropped",
      "status": "processed"
    },
    {
      "timestamp": "2025-11-11T10:30:47Z",
      "action": "background_removed",
      "status": "success",
      "background_color": "white"
    }
  ]
}
```

---

## 📚 Documentación Completa

El proyecto incluye documentación exhaustiva en `docs/`:

| Documento | Descripción |
|-----------|-------------|
| `FLUJO_PROCESAMIENTO.md` | Flujo detallado del sistema |
| `INTEGRACION_ELIMINACION_FONDO.md` | IA de eliminación de fondo |
| `MEJORA_ALGORITMO_CABELLO.md` | Optimización de recorte |
| `WEB_DASHBOARD_DOCUMENTATION.md` | Documentación del dashboard |
| `CORRECCIONES_NOMBRES_FORMATOS.md` | Gestión de formatos |
| `QUICKSTART.md` | Guía rápida de inicio |
| `FIX_IMPORT_ERROR_WEBAPP.md` | Solución de problemas |

---

## ⚙️ Configuración

### Archivos de Configuración

#### `config/paths.json`
```json
{
  "paths": {
    "input_raw": "./input_raw",
    "output": "./output",
    "output_white": "./output_white",
    "output_final": "./output_final",
    "metadata": "./metadata",
    "logs": "./logs"
  }
}
```

#### `config/settings.yml`
```yaml
standard_size:
  width: 300
  height: 400

face_threshold: 0.5

background_removal:
  enabled: true
  color: "white"
  model: "u2net"
```

---

## 🔧 Troubleshooting

### Error: Puerto 8000 en uso
```bash
# Ver proceso usando puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O usar otro puerto
uvicorn src.webapp.app:app --port 8001
```

### Error: ModuleNotFoundError
```bash
# Verificar que estás en el directorio correcto
pwd

# Activar entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Warning: GPU device discovery failed
**Normal.** El sistema usa CPU automáticamente si no hay GPU NVIDIA.

---

## 🤝 Contribuir

Este es un proyecto interno. Para mejoras o sugerencias, contactar al equipo de desarrollo.

---

## 📝 Licencia

MIT License - Ver archivo LICENSE para más detalles.

---

## 👥 Créditos

**Desarrollado por:** Equipo PhotoCrop  
**Versión:** 1.0.0  
**Fecha:** Noviembre 2025

**Tecnologías utilizadas:**
- Python 3.12+
- dlib (detección facial)
- rembg / U2-Net (eliminación de fondo)
- FastAPI (dashboard web)
- Pillow (procesamiento de imágenes)
- Uvicorn (servidor ASGI)

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar documentación en `docs/`
2. Ejecutar `python clean_system.py --status`
3. Revisar logs en `logs/pipeline.log`

---

**¡PhotoCrop está listo para procesar miles de fotos con calidad profesional!** 🎉

