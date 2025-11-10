# Flujo de Generación y Actualización de Metadatos

## Pseudocódigo del Flujo

```
INICIO pipeline_procesamiento_imagenes()

1. INICIALIZAR
   - Cargar configuración desde ./config/settings.yml
   - Crear logger que escribe en ./logs/pipeline.log
   - Obtener timestamp_ejecucion (ISO8601)
   - Detectar o solicitar batch_id (ej: "admission_2025_01")

2. ESCANEAR_INPUT
   - Listar todos los archivos en ./input_raw/{año}/{lote}/
   - Filtrar extensiones válidas: [.jpg, .jpeg, .png, .pdf, .bmp, .tiff]
   - Crear lista archivos_a_procesar[]

3. PARA CADA archivo EN archivos_a_procesar:
   
   3.1 VALIDACION_BASICA(archivo)
       - Intentar abrir archivo con Pillow
       - SI archivo corrupto o vacío:
           * Registrar error en logs/pipeline.log
           * Mover archivo a ./errors/{batch_id}/
           * Crear metadata con status: "error"
           * CONTINUAR con siguiente
       
   3.2 EXTRAER_DATOS_BASICOS(archivo)
       - filename = nombre_base_archivo
       - format = extensión (JPG, PNG, PDF)
       - width, height = dimensiones_imagen
       - orientation = calcular_orientacion(width, height)
       - input_path = ruta_completa_original
       - current_path = input_path (inicial)
       
   3.3 CREAR_METADATA_INICIAL
       - Construir ruta: ./metadata/{batch_id}/{filename}.json
       - SI ya existe el JSON:
           * Cargar metadata existente
           * Preservar campos históricos
           * Añadir "last_updated": timestamp_ejecucion
       - SI NO existe:
           * Crear nuevo diccionario metadata
           * Inicializar todos los campos
           * status = "pending"
       
   3.4 ANALISIS_FACIAL(imagen)
       - Cargar detector dlib
       - faces = detector.detectar_rostros(imagen)
       - num_faces = contar(faces)
       
       - SI num_faces == 0:
           * face_detected = false
           * num_faces = 0
           * face_box = null
           * status = "manual_review"
           * current_path = ./manual_review/{batch_id}/{filename}
           * notes = "No se detectó ningún rostro"
           
       - SI num_faces == 1:
           * face_detected = true
           * num_faces = 1
           * face_box = [x, y, width, height] del rostro
           * status = "processed"
           * current_path = ./working/faces_detected/{batch_id}/{filename}
           * output_path = ./prepared/{batch_id}/{filename}
           
       - SI num_faces > 1:
           * face_detected = true
           * num_faces = cantidad_detectada
           * face_box = coordenadas del rostro más grande/central
           * status = "manual_review"
           * current_path = ./manual_review/{batch_id}/{filename}
           * notes = "Se detectaron múltiples rostros"
       
   3.5 MANEJO_EXCEPCIONES
       - SI ocurre error durante análisis facial:
           * status = "error"
           * error_message = descripción del error
           * current_path = ./errors/{batch_id}/{filename}
           * Registrar en logs
       
   3.6 ACTUALIZAR_METADATA
       - metadata["processing_time"] = timestamp_ejecucion
       - metadata["batch_id"] = batch_id
       - Guardar JSON en ./metadata/{batch_id}/{filename}.json
       - Formato: UTF-8, indent=2, ensure_ascii=false
       
   3.7 MOVER_IMAGEN
       - Copiar/mover imagen a current_path según status
       - Preservar original en input_raw si configurado

4. GENERAR_RESUMEN_LOTE
   - Contar: total, procesados, manual_review, errores
   - Crear ./metadata/{batch_id}/batch_summary.json
   - Registrar estadísticas en logs

5. FINALIZAR
   - Cerrar logger
   - Retornar resumen de ejecución

FIN pipeline_procesamiento_imagenes()


FUNCION calcular_orientacion(width, height):
    ratio = width / height
    SI ratio > 1.1:
        RETORNAR "landscape"
    SI ratio < 0.9:
        RETORNAR "portrait"
    SINO:
        RETORNAR "square"
```

## Estructura de Carpetas para Metadata

```
metadata/
├── 2025/
│   ├── admission_01/
│   │   ├── IMG_0001.json
│   │   ├── IMG_0002.json
│   │   ├── ...
│   │   └── batch_summary.json
│   ├── admission_02/
│   │   ├── ...
│   │   └── batch_summary.json
│   └── ...
├── 2024/
│   └── ...
└── README.md
```

Reglas de organización:
- Primer nivel: año (YYYY)
- Segundo nivel: identificador de lote (admission_NN, transfer_NN, etc.)
- Tercer nivel: archivos JSON individuales por imagen
- Archivo especial: batch_summary.json con estadísticas agregadas del lote

