# Flujo de Procesamiento de Imágenes - PhotoCrop

## Pseudocódigo del Flujo Completo

```pseudocode
INICIO PROCESAMIENTO

1. INICIALIZACIÓN
   - Cargar configuración de rutas desde ./config/paths.json
   - Verificar existencia de carpetas necesarias:
     * input_raw, metadata, errors, manual_review, output, logs, working, prepared
   - Cargar o crear processed_index.json desde ./metadata/processed_index.json
   - Inicializar logger en ./logs/pipeline.log
   - Inicializar componentes:
     * MetadataManager
     * FaceDetector (dlib)
     * ImageProcessor (Pillow)
   - Inicializar contadores de estadísticas:
     * total = 0
     * processed = 0
     * skipped = 0
     * manual_review = 0
     * errors = 0

2. ESCANEO DE ENTRADA
   - Listar archivos en ./input_raw/ (solo nivel raíz, sin subdirectorios)
   - Filtrar solo extensiones válidas: ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
   - Excluir archivos ocultos (que comienzan con '.')
   - Excluir archivos menores a 1KB (probablemente corruptos)
   - Registrar cantidad total encontrada
   - SI no hay archivos:
     REGISTRAR warning "No se encontraron imágenes"
     TERMINAR

3. FILTRADO DE ARCHIVOS NUEVOS
   PARA cada archivo en lista_encontrados:
     SI filename existe en processed_index.json["processed_files"]:
       REGISTRAR info "Archivo ya procesado, saltando: {filename}"
       skipped++
       CONTINUAR (saltar este archivo)
     SINO:
       Agregar a lista_pendientes
   
   REGISTRAR info "Archivos nuevos a procesar: {len(lista_pendientes)}"
   SI lista_pendientes está vacía:
     REGISTRAR info "No hay archivos nuevos para procesar"
     TERMINAR

4. PROCESAMIENTO DE ARCHIVOS NUEVOS
   PARA cada archivo en lista_pendientes:
     total++
     REGISTRAR info "=========================================="
     REGISTRAR info "Procesando: {filename}"
     REGISTRAR info "=========================================="
   
     4.1 VALIDACIÓN BÁSICA
         INTENTAR:
           - Abrir imagen con PIL.Image.open()
           - Verificar que se puede leer
           - Obtener dimensiones: width, height = image.size
           - Obtener formato: format = image.format
           - Calcular tamaño de archivo en bytes
           
           SI width == 0 O height == 0:
             LANZAR excepción "Dimensiones inválidas"
           
           REGISTRAR info "Dimensiones: {width}x{height}"
           REGISTRAR info "Formato: {format}"
         
         CAPTURAR excepción como e:
           REGISTRAR error "Error al cargar imagen: {str(e)}"
           - status_decision = "ERROR"
           - error_message = f"PIL error: {str(e)}"
           - SALTAR a sección 4.6 (Manejo de Error)
     
     4.2 CREACIÓN DE METADATO INICIAL
         - timestamp_actual = datetime.now(UTC).isoformat()
         - batch_id = extraer_batch_id_desde_ruta(input_path) O usar_default()
         - orientation = calcular_orientacion(width, height)
           SI height > width: orientation = "portrait"
           SI width > height: orientation = "landscape"
           SI width == height: orientation = "square"
         
         - Crear objeto metadato:
           {
             "filename": filename,
             "input_path": "./input_raw/" + filename,
             "current_path": "./input_raw/" + filename,
             "output_path": null,
             "format": format,
             "width": width,
             "height": height,
             "orientation": orientation,
             "face_detected": false,
             "num_faces": 0,
             "face_box": null,
             "status": "pending",
             "error_message": null,
             "processing_time": timestamp_actual,
             "batch_id": batch_id,
             "notes": null,
             "metadata_version": "1.0",
             "last_updated": timestamp_actual,
             "processing_history": [
               {
                 "timestamp": timestamp_actual,
                 "action": "initial_scan",
                 "status": "pending"
               }
             ]
           }
         
         - Guardar metadata inicial en:
           ./metadata/{year}/{batch_id}/{filename_sin_ext}.json
         
         REGISTRAR info "Metadata inicial creado"
     
     4.3 DETECCIÓN FACIAL (dlib)
         REGISTRAR info "Iniciando detección facial con dlib..."
         
         INTENTAR:
           - Convertir imagen a formato RGB si no lo está
           - Convertir a numpy array para dlib
           - Aplicar dlib.get_frontal_face_detector()
           - faces = detector(img_array, 1)
           - num_faces = len(faces)
           
           REGISTRAR info "Rostros detectados: {num_faces}"
           
           SI num_faces == 0:
             # SIN ROSTROS
             REGISTRAR warning "⚠️  No se detectó ningún rostro"
             - face_detected = false
             - num_faces = 0
             - face_box = null
             - decision_recorte = "MANUAL_REVIEW"
             - Actualizar metadata con estos valores
             - SALTAR a sección 4.5.2 (Manual Review)
           
           SI num_faces == 1:
             # UN SOLO ROSTRO
             REGISTRAR info "✓ Un rostro detectado"
             - face = faces[0]
             - face_box = [face.left(), face.top(), 
                           face.width(), face.height()]
             - face_detected = true
             - num_faces = 1
             - Actualizar metadata con estos valores
             
             # INVOCAR MÓDULO DE DECISIÓN DE RECORTE
             - crop_decision = calcular_decision_recorte(
                 width, height, face_box, orientation
               )
             
             SI crop_decision.status == "OK":
               - crop_box = crop_decision.crop_box
               - decision_recorte = "OK"
               - SALTAR a sección 4.5.1 (Procesamiento Exitoso)
             
             SI crop_decision.status == "MANUAL_REVIEW":
               - decision_recorte = "MANUAL_REVIEW"
               - notes = crop_decision.reason
               - SALTAR a sección 4.5.2 (Manual Review)
           
           SI num_faces > 1:
             # MÚLTIPLES ROSTROS
             REGISTRAR warning "⚠️  Detectados {num_faces} rostros"
             - face_detected = true
             - num_faces = cantidad
             - Encontrar rostro más grande:
               largest_face = max(faces, key=lambda f: f.width() * f.height())
             - face_box = [largest_face.left(), largest_face.top(),
                           largest_face.width(), largest_face.height()]
             - decision_recorte = "MANUAL_REVIEW"
             - notes = f"Múltiples rostros detectados ({num_faces})"
             - Actualizar metadata
             - SALTAR a sección 4.5.2 (Manual Review)
         
         CAPTURAR excepción como e:
           REGISTRAR error "Error en detección facial: {str(e)}"
           - error_message = f"dlib error: {str(e)}"
           - status = "error"
           - decision_recorte = "ERROR"
           - SALTAR a sección 4.6 (Manejo de Error)
     
     4.4 MÓDULO DE DECISIÓN DE RECORTE
         # Este módulo analiza si la imagen puede ser recortada correctamente
         # Basado en reglas establecidas
         
         FUNCIÓN calcular_decision_recorte(width, height, face_box, orientation):
           - [x, y, w, h] = face_box
           - face_center_x = x + w/2
           - face_center_y = y + h/2
           
           # Verificar que el rostro no esté en el borde
           margin = 50  # píxeles mínimos de margen
           SI face_center_x < margin O face_center_x > (width - margin):
             RETORNAR {status: "MANUAL_REVIEW", reason: "Rostro muy cercano al borde horizontal"}
           
           SI face_center_y < margin O face_center_y > (height - margin):
             RETORNAR {status: "MANUAL_REVIEW", reason: "Rostro muy cercano al borde vertical"}
           
           # Calcular crop_box para formato pasaporte (3:4)
           target_aspect = 3/4
           crop_height = min(height, w * 1.5 * (4/3))
           crop_width = crop_height * target_aspect
           
           # Centrar en el rostro con offset hacia arriba
           crop_x = max(0, face_center_x - crop_width/2)
           crop_y = max(0, face_center_y - crop_height * 0.4)
           
           # Ajustar si se sale de los límites
           SI crop_x + crop_width > width:
             crop_x = width - crop_width
           SI crop_y + crop_height > height:
             crop_y = height - crop_height
           
           SI crop_x < 0 O crop_y < 0:
             RETORNAR {status: "MANUAL_REVIEW", reason: "No hay espacio suficiente para recorte"}
           
           crop_box = [int(crop_x), int(crop_y), 
                       int(crop_x + crop_width), int(crop_y + crop_height)]
           
           RETORNAR {status: "OK", crop_box: crop_box, reason: null}
     
     4.5 PROCESAMIENTO SEGÚN DECISIÓN
         
         4.5.1 SI decision_recorte == "OK":
               REGISTRAR info "✓ Aplicando recorte..."
               
               - Aplicar recorte: cropped_img = image.crop(crop_box)
               - Redimensionar si es necesario para cumplir estándares
               - Optimizar calidad JPEG
               
               - output_filename = filename (mantener mismo nombre)
               - output_path = "./output/" + output_filename
               - Guardar cropped_img en output_path con calidad alta
               
               - Actualizar metadata:
                 * current_path = output_path
                 * output_path = output_path
                 * status = "processed"
                 * action = "face_detected_and_cropped"
                 * processing_history.append({
                     timestamp, action, status: "processed",
                     details: "Recorte aplicado exitosamente"
                   })
               
               - Guardar metadata actualizado
               - Agregar filename a processed_index.json["processed_files"]
               - Guardar processed_index.json
               - processed++
               
               REGISTRAR info "✓ Imagen procesada exitosamente → {output_path}"
               
               # OPCIONAL: Eliminar de input_raw
               - SI configuración permite limpieza:
                 ELIMINAR archivo de ./input_raw/
         
         4.5.2 SI decision_recorte == "MANUAL_REVIEW":
               REGISTRAR warning "⚠️  Enviando a revisión manual..."
               
               - year = año_actual
               - dest_dir = "./manual_review/{year}/{batch_id}/"
               - Crear dest_dir si no existe
               - dest_path = dest_dir + filename
               - COPIAR imagen desde input_path a dest_path
               
               - Actualizar metadata:
                 * current_path = dest_path
                 * status = "manual_review"
                 * action = "sent_to_manual_review"
                 * SI notes existe, mantenerlo
                 * processing_history.append({
                     timestamp, action, status: "manual_review",
                     details: notes O "Requiere revisión manual"
                   })
               
               - Guardar metadata actualizado
               - Agregar filename a processed_index.json["processed_files"]
               - Guardar processed_index.json
               - manual_review++
               
               REGISTRAR warning "⚠️  Imagen enviada a revisión manual → {dest_path}"
     
     4.6 MANEJO DE ERROR
         REGISTRAR error "✗ Error en procesamiento"
         
         - year = año_actual
         - error_dir = "./errors/{year}/{batch_id}/"
         - Crear error_dir si no existe
         - error_path = error_dir + filename
         
         INTENTAR:
           - MOVER archivo desde input_path a error_path
         CAPTURAR:
           - REGISTRAR error crítico si no se puede mover
         
         - Actualizar O crear metadata:
           * filename = filename
           * input_path = input_path_original
           * current_path = error_path
           * status = "error"
           * error_message = mensaje_de_error
           * action = "error_detected"
           * processing_history.append({
               timestamp, action, status: "error",
               details: error_message
             })
         
         - Guardar metadata
         - Agregar filename a processed_index.json["processed_files"]
         - Guardar processed_index.json
         - errors++
         
         REGISTRAR error "✗ Imagen con error → {error_path}"
     
     4.7 PERSISTENCIA
         - Asegurar que metadata fue guardado
         - Asegurar que processed_index.json fue actualizado
         - Asegurar que logs fueron escritos
         - Flush de logger

5. GENERACIÓN DE RESUMEN DE LOTE
   SI se procesaron archivos del mismo batch_id:
     - Recopilar todos los metadatos del lote
     - Crear batch_summary.json:
       {
         "batch_id": batch_id,
         "input_path": "./input_raw/{year}/{batch_id}/",
         "total_images": cantidad,
         "processed": cantidad_procesadas,
         "manual_review": cantidad_manual,
         "errors": cantidad_errores,
         "processing_date": timestamp,
         "files": [lista de filenames]
       }
     - Guardar en ./metadata/{year}/{batch_id}/batch_summary.json
     REGISTRAR info "Resumen de lote generado"

6. LIMPIEZA OPCIONAL
   SI configuración permite auto-limpieza:
     PARA cada archivo en input_raw:
       SI filename está en processed_index.json:
         SI status == "processed":
           ELIMINAR de input_raw
           REGISTRAR info "Limpiado: {filename}"

7. RESUMEN FINAL
   REGISTRAR info "=========================================="
   REGISTRAR info "RESUMEN DE PROCESAMIENTO"
   REGISTRAR info "=========================================="
   REGISTRAR info "Total encontrados: {total}"
   REGISTRAR info "Saltados (ya procesados): {skipped}"
   REGISTRAR info "Nuevos procesados:"
   REGISTRAR info "  ✓ Exitosos: {processed}"
   REGISTRAR info "  ⚠️  Revisión manual: {manual_review}"
   REGISTRAR info "  ✗ Errores: {errors}"
   REGISTRAR info "=========================================="
   
   - Retornar estadísticas finales

FIN PROCESAMIENTO
```

## Ejemplo de processed_index.json

```json
{
  "processed_files": [
    "IMG_0001.jpg",
    "IMG_0002.jpg",
    "IMG_0003.jpg",
    "foto_candidato_001.png",
    "postulante_2025_456.jpg",
    "imagen_corrupta.jpg",
    "multi_face_photo.jpg"
  ],
  "last_updated": "2025-11-10T18:45:32.123456Z",
  "total_processed": 7,
  "metadata_version": "1.0",
  "statistics": {
    "total_processed": 7,
    "successful": 3,
    "manual_review": 3,
    "errors": 1
  }
}
```

## JSON de Rutas Clave del Flujo

```json
{
  "paths": {
    "input_raw": "./input_raw",
    "output": "./output",
    "errors": "./errors",
    "manual_review": "./manual_review",
    "metadata": "./metadata",
    "processed_index": "./metadata/processed_index.json",
    "logs": "./logs",
    "working": "./working",
    "prepared": "./prepared"
  }
}
```

## Ejemplo de Metadato JSON Completo

### Caso 1: Imagen Procesada Exitosamente

```json
{
  "filename": "IMG_0001.jpg",
  "input_path": "./input_raw/IMG_0001.jpg",
  "current_path": "./output/IMG_0001.jpg",
  "output_path": "./output/IMG_0001.jpg",
  "format": "JPEG",
  "width": 2048,
  "height": 1536,
  "orientation": "landscape",
  "face_detected": true,
  "num_faces": 1,
  "face_box": [512, 384, 640, 640],
  "status": "processed",
  "error_message": null,
  "processing_time": "2025-11-10T18:30:45.123456Z",
  "batch_id": "admission_2025_01",
  "notes": null,
  "metadata_version": "1.0",
  "last_updated": "2025-11-10T18:30:47.891234Z",
  "processing_history": [
    {
      "timestamp": "2025-11-10T18:30:45.123456Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-10T18:30:47.891234Z",
      "action": "face_detected_and_cropped",
      "status": "processed",
      "details": "Recorte aplicado exitosamente"
    }
  ]
}
```

### Caso 2: Imagen Sin Rostro (Revisión Manual)

```json
{
  "filename": "IMG_0002.jpg",
  "input_path": "./input_raw/IMG_0002.jpg",
  "current_path": "./manual_review/2025/admission_2025_01/IMG_0002.jpg",
  "output_path": null,
  "format": "JPEG",
  "width": 1920,
  "height": 1080,
  "orientation": "landscape",
  "face_detected": false,
  "num_faces": 0,
  "face_box": null,
  "status": "manual_review",
  "error_message": null,
  "processing_time": "2025-11-10T18:31:12.456789Z",
  "batch_id": "admission_2025_01",
  "notes": "No se detectó rostro en la imagen",
  "metadata_version": "1.0",
  "last_updated": "2025-11-10T18:31:14.123456Z",
  "processing_history": [
    {
      "timestamp": "2025-11-10T18:31:12.456789Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-10T18:31:14.123456Z",
      "action": "sent_to_manual_review",
      "status": "manual_review",
      "details": "No se detectó rostro en la imagen"
    }
  ]
}
```

### Caso 3: Múltiples Rostros (Revisión Manual)

```json
{
  "filename": "IMG_0003.jpg",
  "input_path": "./input_raw/IMG_0003.jpg",
  "current_path": "./manual_review/2025/admission_2025_01/IMG_0003.jpg",
  "output_path": null,
  "format": "JPEG",
  "width": 3024,
  "height": 4032,
  "orientation": "portrait",
  "face_detected": true,
  "num_faces": 3,
  "face_box": [890, 1200, 512, 512],
  "status": "manual_review",
  "error_message": null,
  "processing_time": "2025-11-10T18:32:05.789012Z",
  "batch_id": "admission_2025_01",
  "notes": "Múltiples rostros detectados (3)",
  "metadata_version": "1.0",
  "last_updated": "2025-11-10T18:32:08.345678Z",
  "processing_history": [
    {
      "timestamp": "2025-11-10T18:32:05.789012Z",
      "action": "initial_scan",
      "status": "pending"
    },
    {
      "timestamp": "2025-11-10T18:32:08.345678Z",
      "action": "sent_to_manual_review",
      "status": "manual_review",
      "details": "Múltiples rostros detectados (3)"
    }
  ]
}
```

### Caso 4: Imagen con Error

```json
{
  "filename": "corrupted_image.jpg",
  "input_path": "./input_raw/corrupted_image.jpg",
  "current_path": "./errors/2025/admission_2025_01/corrupted_image.jpg",
  "output_path": null,
  "format": null,
  "width": null,
  "height": null,
  "orientation": null,
  "face_detected": false,
  "num_faces": 0,
  "face_box": null,
  "status": "error",
  "error_message": "PIL.UnidentifiedImageError: cannot identify image file - archivo corrupto o formato inválido",
  "processing_time": "2025-11-10T18:33:22.567890Z",
  "batch_id": "admission_2025_01",
  "notes": null,
  "metadata_version": "1.0",
  "last_updated": "2025-11-10T18:33:22.567890Z",
  "processing_history": [
    {
      "timestamp": "2025-11-10T18:33:22.567890Z",
      "action": "error_detected",
      "status": "error",
      "details": "PIL.UnidentifiedImageError: cannot identify image file - archivo corrupto o formato inválido"
    }
  ]
}
```

## Estructura de Carpetas para Metadata

```
./metadata/
├── processed_index.json          # Índice global de archivos procesados
├── README.md                      # Documentación del sistema de metadatos
├── 2024/
│   └── exam_session_01/
│       ├── batch_summary.json
│       ├── student_001.json
│       └── student_002.json
└── 2025/
    ├── admission_01/
    │   ├── batch_summary.json
    │   ├── IMG_0001.json
    │   ├── IMG_0002.json
    │   └── IMG_0003.json
    └── admission_02/
        ├── batch_summary.json
        ├── foto_123.json
        └── foto_456.json
```

## Diagrama de Flujo de Estados

```
[INPUT_RAW]
     |
     v
[VALIDACIÓN] --error--> [ERRORS]
     |
     v
[METADATA INICIAL]
     |
     v
[DETECCIÓN FACIAL]
     |
     +--0 rostros--> [MANUAL_REVIEW]
     |
     +--1 rostro--> [DECISIÓN RECORTE]
     |                   |
     |                   +--OK--> [OUTPUT]
     |                   |
     |                   +--REVIEW--> [MANUAL_REVIEW]
     |
     +-->1 rostros--> [MANUAL_REVIEW]

Todos los casos --> [PROCESSED_INDEX]
```

