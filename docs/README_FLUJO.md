# Documentación del Flujo de Procesamiento - PhotoCrop

Este directorio contiene la documentación completa del sistema de procesamiento de imágenes.

## Documentos Disponibles

### 1. FLUJO_PROCESAMIENTO.md
Documento técnico completo que define:
- Pseudocódigo detallado del flujo de procesamiento
- Estructura de carpetas para metadatos
- Ejemplos de archivos JSON (metadatos, índice de procesados)
- Rutas clave del sistema
- Diagrama de flujo de estados

### 2. metadata_flow.md
Flujo específico de generación y actualización de metadatos.

### 3. ENTREGABLES_METADATA.md
Especificaciones de los metadatos y entregables del sistema.

### 4. QUICKSTART.md
Guía rápida para comenzar a usar el sistema.

## Implementación

El flujo documentado en `FLUJO_PROCESAMIENTO.md` está implementado en:
- **Archivo**: `src/deterministic_processor.py`
- **Clase Principal**: `DeterministicPhotoProcessor`

## Características Clave del Flujo

### Re-ejecución Segura
- Mantiene un índice de archivos procesados (`metadata/processed_index.json`)
- No reprocesa archivos ya tratados
- Permite copiar fotos sin riesgo de duplicar procesamiento

### Clasificación Automática
- **Procesadas exitosamente** → `./output/`
- **Sin rostro detectado** → `./manual_review/`
- **Múltiples rostros** → `./manual_review/`
- **Errores** → `./errors/`

### Trazabilidad Completa
- Cada imagen genera un archivo JSON con metadatos
- Historial de procesamiento con timestamps
- Logs detallados en `./logs/pipeline.log`

## Uso Básico

```python
from src.deterministic_processor import DeterministicPhotoProcessor

# Inicializar procesador
processor = DeterministicPhotoProcessor()

# Ejecutar procesamiento
stats = processor.run(
    batch_id="admission_2025_01",  # Identificador del lote
    auto_clean=False                # No eliminar de input_raw
)

# Resultados
print(f"Procesados: {stats['processed']}")
print(f"Revisión manual: {stats['manual_review']}")
print(f"Errores: {stats['errors']}")
```

## Flujo de Trabajo Recomendado

1. **Copiar fotos** en `./input_raw/`
2. **Ejecutar procesador**: `python src/deterministic_processor.py`
3. **Revisar resultados**:
   - Fotos correctas en `./output/`
   - Casos dudosos en `./manual_review/`
   - Errores en `./errors/`
4. **Consultar metadatos** en `./metadata/{año}/{lote}/`

## Protección de Datos

El `.gitignore` está configurado para NO subir:
- Fotos originales (`input_raw/`)
- Fotos procesadas (`output/`)
- Metadatos con información personal (`metadata/`)
- Casos de revisión manual (`manual_review/`)
- Errores (`errors/`)

Solo se suben:
- Código fuente
- Configuraciones (sin datos sensibles)
- Documentación
- Archivos de ejemplo

## Soporte

Para más detalles, consultar:
- `FLUJO_PROCESAMIENTO.md` - Especificación técnica completa
- `../PROJECT_COMPLETE.md` - Visión general del proyecto
- `../README.md` - Información general

