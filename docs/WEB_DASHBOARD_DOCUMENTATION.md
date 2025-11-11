# Aplicación Web PhotoCrop - Documentación Completa

## 📋 Arquitectura Propuesta

### Componentes del Sistema

```
PhotoCrop Web Dashboard
├── Backend: FastAPI (Python)
│   ├── API REST (JSON)
│   ├── Procesamiento en background
│   └── Lectura de estadísticas
│
├── Frontend: HTML + CSS + JavaScript Vanilla
│   ├── Dashboard interactivo
│   ├── Botones de control
│   └── Auto-refresh cada 5 segundos
│
└── Integración con Sistema Existente
    ├── processor_with_bg_removal.py
    ├── format_converter.py
    └── metadata/processed_index.json
```

### Flujo de Datos

```
Usuario Web → FastAPI → run_pipeline() → Procesador Python
                ↓
         Background Task
                ↓
         Actualizar Stats
                ↓
         Frontend (Auto-refresh)
```

---

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar FastAPI y dependencias
pip install fastapi uvicorn[standard] jinja2 python-multipart

# O usar requirements.txt actualizado
pip install -r requirements.txt
```

### 2. Estructura de Archivos

```
src/webapp/
├── app.py              # Aplicación FastAPI principal
├── templates/
│   └── index.html      # Interfaz HTML
└── static/
    └── style.css       # Estilos CSS
```

---

## 🎯 Características Implementadas

### 1. Dashboard Principal
- **Botón "Procesar Nuevas Fotos"** - Ejecuta el pipeline completo
- **Estadísticas en tiempo real** - Se actualizan cada 5 segundos
- **6 contadores visuales:**
  - 📥 Fotos en Input
  - ✅ Procesadas
  - ⚠️ Revisión Manual
  - ❌ Errores
  - 🎨 Fondo Blanco
  - 🎯 Finales

### 2. Visualización de Carpetas
- **6 pestañas interactivas:**
  - Output
  - Fondo Blanco (white/)
  - Final (output_final/)
  - Revisión Manual
  - Errores
  - Input Raw

- **Información de cada imagen:**
  - Nombre del archivo
  - Tamaño (KB)
  - Fecha de modificación

### 3. Visor de Logs
- Últimas 50 líneas de `logs/pipeline.log`
- Botón para refrescar logs
- Estilo terminal oscuro
- Auto-scroll al final

### 4. Procesamiento Asíncrono
- Ejecuta en background sin bloquear UI
- Indica estado "Procesando..."
- Desactiva botón durante procesamiento
- Muestra resultado al terminar

---

## 📡 API Endpoints

### GET `/`
**Descripción:** Página principal del dashboard  
**Respuesta:** HTML

### GET `/api/stats`
**Descripción:** Obtiene estadísticas del sistema  
**Respuesta:**
```json
{
  "folders": {
    "input_raw": 5,
    "output": 3,
    "output_white": 3,
    "output_final": 3,
    "manual_review": 1,
    "errors": 0
  },
  "processed": {
    "total_processed": 4,
    "successful": 3,
    "manual_review": 1,
    "errors": 0
  },
  "processing": {
    "is_processing": false,
    "last_run": "2025-11-11T10:30:45",
    "last_stats": {...},
    "error": null
  },
  "timestamp": "2025-11-11T10:35:12"
}
```

### POST `/api/process`
**Descripción:** Inicia procesamiento de fotos  
**Parámetros opcionales:**
- `batch_id` (string) - ID del lote

**Respuesta:**
```json
{
  "success": true,
  "message": "Procesamiento iniciado",
  "timestamp": "2025-11-11T10:30:45"
}
```

### GET `/api/logs?lines=50`
**Descripción:** Obtiene últimas líneas del log  
**Parámetros:**
- `lines` (int) - Número de líneas (default: 50)

**Respuesta:**
```json
{
  "logs": ["línea1", "línea2", ...],
  "count": 50
}
```

### GET `/api/images/{folder}?limit=20`
**Descripción:** Lista imágenes en carpeta  
**Carpetas válidas:**
- `output`
- `output_white`
- `output_final`
- `manual_review`
- `errors`
- `input_raw`

**Respuesta:**
```json
{
  "folder": "output",
  "images": [
    {
      "name": "foto001.jpg",
      "path": "./output/foto001.jpg",
      "size": 245760,
      "modified": "2025-11-11 10:30:45"
    }
  ],
  "count": 1
}
```

### GET `/api/health`
**Descripción:** Health check del servicio  
**Respuesta:**
```json
{
  "status": "healthy",
  "service": "PhotoCrop Dashboard",
  "version": "1.0",
  "timestamp": "2025-11-11T10:30:45"
}
```

---

## 🔧 Integración con el Sistema

### Llamada a run_pipeline()

```python
def run_pipeline(batch_id: Optional[str] = None) -> Dict:
    """
    Ejecuta el pipeline completo de procesamiento.
    Integración con processor_with_bg_removal.py
    """
    # 1. Inicializar procesador con eliminación de fondo
    processor = PhotoProcessorWithBgRemoval(
        enable_bg_removal=True,
        background_color=(255, 255, 255, 255)
    )
    
    # 2. Ejecutar procesamiento
    stats = processor.run(
        batch_id=batch_id,
        auto_clean=False
    )
    
    # 3. Convertir a formato original
    conversion_stats = convert_to_original_format(
        input_dir="./output_white",
        output_dir="./output_final",
        metadata_dir="./metadata",
        quality=95
    )
    
    return {
        "success": True,
        "stats": stats,
        "conversion": conversion_stats
    }
```

### Lectura de Estadísticas

```python
def get_folder_stats() -> Dict:
    """Lee estadísticas de carpetas del sistema"""
    stats = {}
    folders = {
        "input_raw": Path("./input_raw"),
        "output": Path("./output"),
        "output_white": Path("./output_white"),
        # ...
    }
    
    for key, folder in folders.items():
        if folder.exists():
            # Contar imágenes
            count = 0
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                count += len(list(folder.rglob(f"*{ext}")))
            stats[key] = count
    
    return stats
```

### Lectura de Logs

```python
def get_recent_logs(lines: int = 50) -> List[str]:
    """Lee últimas líneas de logs/pipeline.log"""
    log_path = Path("./logs/pipeline.log")
    
    with open(log_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        return all_lines[-lines:]
```

---

## 🚀 Comandos de Ejecución

### Opción 1: Script de inicio (Recomendado)
```bash
./start_webapp.sh
```

### Opción 2: uvicorn directo
```bash
# Desde el directorio raíz del proyecto
uvicorn src.webapp.app:app --host 0.0.0.0 --port 8000 --reload
```

### Opción 3: Python directo
```bash
python src/webapp/app.py
```

### Opción 4: Con configuración personalizada
```bash
# Puerto personalizado
uvicorn src.webapp.app:app --port 8080

# Solo localhost (más seguro)
uvicorn src.webapp.app:app --host 127.0.0.1 --port 8000

# Sin auto-reload (producción)
uvicorn src.webapp.app:app --host 0.0.0.0 --port 8000
```

---

## 🌐 Acceso a la Aplicación

### URLs Disponibles
```
Dashboard principal:
  http://localhost:8000
  http://127.0.0.1:8000

API Docs (Swagger):
  http://localhost:8000/docs

API ReDoc:
  http://localhost:8000/redoc
```

---

## 📊 Funcionalidades del Dashboard

### Auto-Refresh
```javascript
// Actualiza estadísticas cada 5 segundos
setInterval(() => {
    updateStats();
}, 5000);
```

### Procesamiento en Background
```python
@app.post("/api/process")
async def process_photos(background_tasks: BackgroundTasks):
    # Ejecuta sin bloquear
    background_tasks.add_task(process_photos_background)
    return {"success": True, "message": "Procesamiento iniciado"}
```

### Estado del Procesamiento
- ✅ **Idle:** Botón activo, listo para procesar
- ⏳ **Procesando:** Botón desactivado, mensaje "Procesando fotos..."
- ✓ **Completado:** Muestra timestamp de última ejecución
- ❌ **Error:** Muestra mensaje de error

---

## 🎨 Personalización

### Colores del Dashboard
Editar `src/webapp/static/style.css`:

```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Color de botón primario */
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Intervalo de Auto-Refresh
Editar `src/webapp/templates/index.html`:

```javascript
// Cambiar 5000 a los milisegundos deseados
setInterval(() => {
    updateStats();
}, 5000);  // 5 segundos
```

### Número de Logs
```javascript
// En refreshLogs()
const response = await fetch('/api/logs?lines=100');  // Cambiar a 100 líneas
```

---

## 🔒 Seguridad y Consideraciones

### Seguridad Básica
- **Sin autenticación** - Solo para uso local
- **CORS desactivado** - No accesible desde otros dominios
- **Host 0.0.0.0** - Accesible desde red local
- **Host 127.0.0.1** - Solo localhost (más seguro)

### Recomendaciones para Producción
1. Agregar autenticación básica
2. Usar HTTPS con certificado
3. Limitar acceso por IP
4. Agregar rate limiting
5. Validar inputs del usuario

---

## 🧪 Testing

### Verificar Instalación
```bash
# Test de importación
python -c "from src.webapp.app import app; print('✓ OK')"

# Test de servidor
curl http://localhost:8000/api/health
```

### Test de Endpoints
```bash
# Stats
curl http://localhost:8000/api/stats

# Logs
curl http://localhost:8000/api/logs?lines=10

# Imágenes
curl http://localhost:8000/api/images/output

# Procesar (POST)
curl -X POST http://localhost:8000/api/process
```

---

## 📝 Logs y Debugging

### Ubicación de Logs
- **Sistema:** `logs/pipeline.log`
- **Web Server:** Consola donde se ejecuta uvicorn

### Modo Debug
```bash
# Con logs detallados
uvicorn src.webapp.app:app --reload --log-level debug
```

### Ver Logs en Tiempo Real
```bash
# Terminal 1: Servidor
./start_webapp.sh

# Terminal 2: Logs
tail -f logs/pipeline.log
```

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError
```bash
# Verificar que estás en el directorio correcto
pwd  # Debe mostrar: /home/lmayta/PycharmProjects/PhotoCrop

# Activar entorno virtual
source .venv/bin/activate
```

### Error: Port already in use
```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O usar otro puerto
uvicorn src.webapp.app:app --port 8001
```

### Error: Templates not found
```bash
# Verificar estructura
ls -la src/webapp/templates/
ls -la src/webapp/static/

# Debe existir:
# - src/webapp/templates/index.html
# - src/webapp/static/style.css
```

---

## 🚀 Próximos Pasos

### Mejoras Sugeridas
1. **Subida de archivos** - Drag & drop de imágenes
2. **Visualización de imágenes** - Thumbnails con lightbox
3. **Comparación antes/después** - Side by side
4. **Configuración en UI** - Ajustar parámetros desde web
5. **Descarga de resultados** - ZIP con fotos procesadas
6. **Historial de procesos** - Log de ejecuciones anteriores

### Extensiones Posibles
1. **WebSockets** - Updates en tiempo real
2. **Base de datos** - SQLite para historial
3. **Autenticación** - Login básico
4. **API REST completa** - CRUD de configuraciones
5. **Modo oscuro** - Toggle en UI

---

## 📚 Referencias

### Documentación Oficial
- **FastAPI:** https://fastapi.tiangolo.com/
- **Uvicorn:** https://www.uvicorn.org/
- **Jinja2:** https://jinja.palletsprojects.com/

### Archivos del Proyecto
- `src/webapp/app.py` - Backend FastAPI
- `src/webapp/templates/index.html` - Frontend HTML
- `src/webapp/static/style.css` - Estilos CSS
- `start_webapp.sh` - Script de inicio

---

## ✅ Checklist de Instalación

- [ ] Entorno virtual activado
- [ ] FastAPI instalado (`pip install fastapi`)
- [ ] Uvicorn instalado (`pip install uvicorn[standard]`)
- [ ] Jinja2 instalado (`pip install jinja2`)
- [ ] Estructura de carpetas creada
- [ ] Archivos copiados correctamente
- [ ] Permisos de ejecución dados a scripts
- [ ] Servidor web iniciado
- [ ] Dashboard accesible en http://localhost:8000

---

**Fecha de creación:** 2025-11-11  
**Versión:** 1.0  
**Estado:** ✅ PRODUCCIÓN

