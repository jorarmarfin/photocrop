# Corrección de Error de Importación - Web Dashboard

## 🐛 Error Original

```
ModuleNotFoundError: No module named 'deterministic_processor'
```

**Traceback:**
```python
File "/home/lmayta/PycharmProjects/PhotoCrop/src/webapp/app.py", line 20
    from src.processor_with_bg_removal import PhotoProcessorWithBgRemoval
File "/home/lmayta/PycharmProjects/PhotoCrop/src/processor_with_bg_removal.py", line 13
    from deterministic_processor import DeterministicPhotoProcessor
ModuleNotFoundError: No module named 'deterministic_processor'
```

---

## 🔧 Problema

Los imports estaban usando rutas relativas inconsistentes que no funcionaban cuando se ejecutaba uvicorn desde diferentes ubicaciones.

**Imports problemáticos:**
```python
from deterministic_processor import ...      # ❌ Ruta relativa
from core.metadata_manager import ...        # ❌ Ruta relativa
from utils.logger import ...                 # ❌ Ruta relativa
```

---

## ✅ Solución Aplicada

### 1. Corregir Imports a Rutas Absolutas

**Archivos modificados:**

#### `src/deterministic_processor.py`
```python
# ANTES
from core.metadata_manager import MetadataManager
from core.face_detector import FaceDetector
from utils.logger import setup_logger

# DESPUÉS
from src.core.metadata_manager import MetadataManager
from src.core.face_detector import FaceDetector
from src.utils.logger import setup_logger
```

#### `src/processor_with_bg_removal.py`
```python
# ANTES
from deterministic_processor import DeterministicPhotoProcessor
from core.background_remover import BackgroundRemover

# DESPUÉS
from src.deterministic_processor import DeterministicPhotoProcessor
from src.core.background_remover import BackgroundRemover
```

#### `src/webapp/app.py`
```python
# Agregar directorio raíz al PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Imports correctos
from src.processor_with_bg_removal import PhotoProcessorWithBgRemoval
from src.core.format_converter import convert_to_original_format
```

#### `src/pipeline.py`
```python
# ANTES
from core.metadata_manager import MetadataManager

# DESPUÉS
from src.core.metadata_manager import MetadataManager
```

#### `src/test_pipeline.py`
```python
# ANTES
from core.metadata_manager import MetadataManager

# DESPUÉS
from src.core.metadata_manager import MetadataManager
```

### 2. Crear Archivos __init__.py

Para que Python reconozca `src` como paquete:

**Archivos creados:**
- `src/__init__.py`
- `src/webapp/__init__.py`

### 3. Actualizar Script de Inicio

**`start_webapp.sh`**
```bash
# Cambiar al directorio del proyecto
PROJECT_DIR="/home/lmayta/PycharmProjects/PhotoCrop"
cd "$PROJECT_DIR"

# Agregar al PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Iniciar servidor
uvicorn src.webapp.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ Verificación

### Test de Importación
```bash
cd /home/lmayta/PycharmProjects/PhotoCrop
source .venv/bin/activate
python -c "from src.webapp.app import app; print('✓ Imports correctos')"
```

**Resultado:**
```
✓ Imports correctos
```

### Iniciar Servidor
```bash
./start_webapp.sh
```

**O directamente:**
```bash
cd /home/lmayta/PycharmProjects/PhotoCrop
source .venv/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
uvicorn src.webapp.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📋 Resumen de Cambios

### Archivos Modificados (6)
1. ✅ `src/deterministic_processor.py` - Imports corregidos
2. ✅ `src/processor_with_bg_removal.py` - Imports corregidos
3. ✅ `src/pipeline.py` - Imports corregidos
4. ✅ `src/test_pipeline.py` - Imports corregidos
5. ✅ `src/webapp/app.py` - PYTHONPATH y imports corregidos
6. ✅ `start_webapp.sh` - PYTHONPATH agregado

### Archivos Creados (2)
1. ✅ `src/__init__.py` - Paquete Python
2. ✅ `src/webapp/__init__.py` - Subpaquete

---

## 🚀 Uso Actualizado

### Iniciar Dashboard Web
```bash
# Desde el directorio raíz del proyecto
./start_webapp.sh
```

### Acceder
```
http://localhost:8000
```

---

## 🔍 Explicación Técnica

### ¿Por qué falló?

1. **Rutas relativas inconsistentes:** 
   - `from deterministic_processor` busca en el mismo nivel
   - Falla cuando se ejecuta desde otro directorio

2. **uvicorn ejecuta desde directorio raíz:**
   - El comando `uvicorn src.webapp.app:app` espera imports absolutos
   - Las rutas relativas no resuelven correctamente

3. **PYTHONPATH no configurado:**
   - Python no sabía dónde buscar el módulo `src`

### ¿Cómo se solucionó?

1. **Imports absolutos desde `src`:**
   ```python
   from src.core.module import Class
   ```
   - Siempre resuelve correctamente
   - Funciona desde cualquier directorio

2. **PYTHONPATH configurado:**
   ```bash
   export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
   ```
   - Python encuentra el paquete `src`
   - Los imports absolutos funcionan

3. **Archivos __init__.py:**
   - Convierte directorios en paquetes Python
   - Permite imports absolutos

---

## ⚠️ Notas Importantes

### Warning de GPU (Normal)
```
[W:onnxruntime] GPU device discovery failed
```
**Es normal si no tienes GPU NVIDIA.** El sistema usa CPU automáticamente.

### IDE Warnings (Ignorar)
```
Unresolved reference 'fastapi'
```
**Es advertencia del IDE.** Los paquetes están instalados en `.venv` y funcionan correctamente.

---

## ✅ Estado Final

**Sistema corregido y funcionando:**
- ✅ Imports corregidos en 6 archivos
- ✅ __init__.py creados
- ✅ PYTHONPATH configurado
- ✅ Script de inicio actualizado
- ✅ Verificación exitosa

**Listo para usar:**
```bash
./start_webapp.sh
# Dashboard disponible en http://localhost:8000
```

---

**Fecha de corrección:** 2025-11-11  
**Estado:** ✅ RESUELTO

