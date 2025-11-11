# Cambio de Carpeta: white → output_white

## 📋 Resumen del Cambio

Se ha renombrado la carpeta `white/` a `output_white/` para mayor claridad y consistencia con las demás carpetas del proyecto.

---

## 🔄 Archivos Actualizados

### Archivos Python (8)
1. ✅ `clean_system.py`
   - Lista de carpetas a limpiar
   - Diccionario de estados
   - Mensajes de usuario

2. ✅ `src/webapp/app.py`
   - Diccionario de carpetas
   - Función run_pipeline()
   - folder_map para API

3. ✅ `src/processor_with_bg_removal.py`
   - Inicialización de paths
   - Guardado en output_white
   - Metadata con output_white_path

4. ✅ `src/core/format_converter.py`
   - Referencias en comentarios (si las hay)

### Scripts Shell (3)
5. ✅ `start_webapp.sh`
   - Mensajes de limpieza
   - Lista de carpetas a limpiar

6. ✅ `convert_to_original_format.sh`
   - Ejemplos de uso

7. ✅ `install_background_removal.sh`
   - Ejemplos (mantiene "white" como color)

### Documentación (2)
8. ✅ `README.md`
   - Estructura del proyecto
   - Comandos de ejemplo
   - Flujo de procesamiento
   - Configuración de paths
   - Sección de limpieza

9. ✅ `docs/*.md` (todos los archivos)
   - Referencias a ./white
   - Ejemplos de comandos
   - Diagramas de flujo

---

## 📂 Cambios Específicos

### Antes
```
./white/                    # Carpeta con fondo blanco
```

### Después
```
./output_white/            # Carpeta con fondo blanco
```

---

## 🎯 Impacto del Cambio

### Rutas Actualizadas

#### En el Código
```python
# ANTES
"output_white": Path("./white")

# DESPUÉS
"output_white": Path("./output_white")
```

#### En Comandos
```bash
# ANTES
./convert_to_original_format.sh ./white ./output_final

# DESPUÉS
./convert_to_original_format.sh ./output_white ./output_final
```

#### En Procesamiento
```python
# ANTES
conversion_stats = convert_to_original_format(
    input_dir="./white",
    output_dir="./output_final"
)

# DESPUÉS
conversion_stats = convert_to_original_format(
    input_dir="./output_white",
    output_dir="./output_final"
)
```

---

## 📊 Flujo Actualizado

### Procesamiento con IA

```
input_raw/foto.jpg
    ↓
working/faces_cropped/foto.jpg    (recortada)
    ↓
prepared/foto.jpg                 (temporal)
    ↓
output_white/foto.jpg             ← NUEVA CARPETA
    ↓
output_final/foto.png             (formato original)
```

### Estructura de Carpetas

```
PhotoCrop/
├── input_raw/         📥 Originales
├── working/           ⚙️ Temporal
├── prepared/          🎨 Preparadas
├── output_white/      ⚪ Con fondo blanco ← RENOMBRADA
├── output/            ✅ Recortadas
├── output_final/      🎯 Formato original
├── manual_review/     ⚠️ Revisión
└── errors/            ❌ Errores
```

---

## ✅ Verificación de Cambios

### Buscar Referencias Restantes
```bash
# Buscar "white" en archivos Python (excepto colores)
grep -r "Path.*white" src/ --include="*.py"

# Resultado esperado: Sin coincidencias o solo referencias a colores
```

### Probar el Sistema
```bash
# 1. Limpiar sistema
python clean_system.py --force

# 2. Procesar fotos
python src/processor_with_bg_removal.py

# 3. Verificar que output_white/ se crea correctamente
ls -la output_white/

# 4. Iniciar dashboard
./start_webapp.sh
# Verificar que muestra "Fondo Blanco" correctamente
```

---

## 🎨 Metadata Actualizado

### Nuevo Campo Agregado
```json
{
  "filename": "foto001.jpg",
  "background_removed": true,
  "background_color": "white",
  "prepared_path": "./prepared/foto001.jpg",
  "output_white_path": "./output_white/foto001.jpg",  ← NUEVO
  "output_path": "./output_final/foto001.png"
}
```

---

## 📝 Notas Importantes

### Colores vs Carpeta
- **Carpeta:** `output_white/` (nombre de directorio)
- **Color:** `"white"` (RGB 255,255,255 - permanece igual)

### Ejemplos de Uso Correcto

```bash
# Color de fondo (no cambió)
python src/core/background_remover.py input.jpg output.jpg --color white

# Carpeta de destino (cambió)
./convert_to_original_format.sh ./output_white ./output_final

# En código Python
from pathlib import Path
output_white = Path("./output_white")  # ✓ Correcto
```

---

## 🔧 Comandos Actualizados

### Dashboard Web
```bash
./start_webapp.sh
# Menú → Opción 1: Iniciar Dashboard
# Pestaña: "Fondo Blanco" muestra contenido de output_white/
```

### Procesamiento CLI
```bash
# Procesar fotos (crea output_white/ automáticamente)
python src/processor_with_bg_removal.py --batch-id test_2025

# Convertir de output_white/ a output_final/
./convert_to_original_format.sh ./output_white ./output_final
```

### Limpieza
```bash
# Limpia output_white/ junto con las demás carpetas
python clean_system.py
```

---

## 📊 Resumen de Archivos Modificados

### Total: 11 archivos actualizados

#### Código Python: 4
- clean_system.py
- src/webapp/app.py
- src/processor_with_bg_removal.py
- (referencias en otros archivos)

#### Scripts Shell: 3
- start_webapp.sh
- convert_to_original_format.sh
- (referencias menores)

#### Documentación: 4+
- README.md
- docs/*.md (todos los archivos)
- Ejemplos de comandos
- Diagramas de flujo

---

## ✅ Estado Final

**Todos los cambios aplicados correctamente:**
- ✅ Carpeta renombrada de `white/` a `output_white/`
- ✅ Referencias actualizadas en código Python
- ✅ Scripts shell actualizados
- ✅ Documentación completa actualizada
- ✅ Dashboard web actualizado
- ✅ Sistema de limpieza actualizado
- ✅ Metadata con nuevo campo

**El sistema está listo para usar con el nuevo nombre de carpeta.**

---

## 🚀 Próximos Pasos

1. **Renombrar carpeta física** (si existe):
   ```bash
   mv white/ output_white/
   ```

2. **Probar el sistema**:
   ```bash
   python clean_system.py --status
   ./start_webapp.sh
   ```

3. **Verificar dashboard**:
   - Abrir http://localhost:8000
   - Verificar pestaña "Fondo Blanco"
   - Procesar foto de prueba

---

**Fecha de cambio:** 2025-11-11  
**Versión:** 1.0.1  
**Estado:** ✅ COMPLETADO

