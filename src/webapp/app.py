"""
Aplicación Web para PhotoCrop - Dashboard de Control
FastAPI + HTML simple para gestión de procesamiento de fotos
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Imports del sistema PhotoCrop
from src.processor_with_bg_removal import PhotoProcessorWithBgRemoval
from src.core.format_converter import convert_to_original_format

# Configuración de FastAPI
app = FastAPI(title="PhotoCrop Dashboard", version="1.0")

# Configuración de templates y archivos estáticos
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Estado global del procesamiento
processing_status = {
    "is_processing": False,
    "last_run": None,
    "last_stats": None,
    "error": None
}


def get_folder_stats() -> Dict:
    """Obtiene estadísticas de las carpetas del sistema."""
    stats = {
        "input_raw": 0,
        "output": 0,
        "output_white": 0,
        "output_final": 0,
        "manual_review": 0,
        "errors": 0,
        "metadata": 0
    }

    folders = {
        "input_raw": Path("./input_raw"),
        "output": Path("./output"),
        "output_white": Path("./output_white"),
        "output_final": Path("./output_final"),
        "manual_review": Path("./manual_review"),
        "errors": Path("./errors"),
        "metadata": Path("./metadata")
    }

    for key, folder in folders.items():
        if folder.exists():
            if key == "metadata":
                # Contar archivos JSON en metadata
                stats[key] = len(list(folder.rglob("*.json")))
            else:
                # Contar imágenes en otras carpetas
                count = 0
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    count += len(list(folder.rglob(f"*{ext}")))
                stats[key] = count

    return stats


def get_processed_index_stats() -> Dict:
    """Lee estadísticas del processed_index.json."""
    index_path = Path("./metadata/processed_index.json")

    if not index_path.exists():
        return {
            "total_processed": 0,
            "successful": 0,
            "manual_review": 0,
            "errors": 0
        }

    try:
        with open(index_path, 'r') as f:
            data = json.load(f)
            return data.get("statistics", {
                "total_processed": 0,
                "successful": 0,
                "manual_review": 0,
                "errors": 0
            })
    except:
        return {
            "total_processed": 0,
            "successful": 0,
            "manual_review": 0,
            "errors": 0
        }


def get_recent_logs(lines: int = 50) -> List[str]:
    """Lee las últimas líneas del log."""
    log_path = Path("./logs/pipeline.log")

    if not log_path.exists():
        return ["No hay logs disponibles"]

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        return [f"Error al leer logs: {str(e)}"]


def get_images_in_folder(folder: str, limit: int = 20) -> List[Dict]:
    """Lista imágenes en una carpeta específica."""
    folder_path = Path(folder)
    images = []

    if not folder_path.exists():
        return images

    extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    count = 0

    for ext in extensions:
        for img_path in folder_path.rglob(f"*{ext}"):
            if count >= limit:
                break

            images.append({
                "name": img_path.name,
                "path": str(img_path.relative_to(Path("."))),
                "size": img_path.stat().st_size,
                "modified": datetime.fromtimestamp(
                    img_path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
            })
            count += 1

    return sorted(images, key=lambda x: x["modified"], reverse=True)


def run_pipeline(batch_id: Optional[str] = None) -> Dict:
    """
    Ejecuta el pipeline completo de procesamiento.
    Esta función es llamada desde el endpoint /process
    """
    try:
        # Configurar batch_id si no se proporciona
        if batch_id is None:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Inicializar procesador con eliminación de fondo
        processor = PhotoProcessorWithBgRemoval(
            enable_bg_removal=True,
            background_color=(255, 255, 255, 255)  # Blanco
        )

        # Ejecutar procesamiento
        stats = processor.run(
            batch_id=batch_id,
            auto_clean=False
        )

        # Convertir fotos de output_white/ a output_final/ con formato original
        try:
            conversion_stats = convert_to_original_format(
                input_dir="./output_white",
                output_dir="./output_final",
                metadata_dir="./metadata",
                quality=95
            )
            stats["conversion"] = conversion_stats
        except Exception as e:
            stats["conversion_error"] = str(e)

        return {
            "success": True,
            "stats": stats,
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def process_photos_background(batch_id: Optional[str] = None):
    """Ejecuta el procesamiento en background."""
    global processing_status

    processing_status["is_processing"] = True
    processing_status["error"] = None

    try:
        result = run_pipeline(batch_id)
        processing_status["last_run"] = result["timestamp"]
        processing_status["last_stats"] = result.get("stats")

        if not result["success"]:
            processing_status["error"] = result.get("error")

    except Exception as e:
        processing_status["error"] = str(e)

    finally:
        processing_status["is_processing"] = False


# ============================================================================
# RUTAS / ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal del dashboard."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "PhotoCrop Dashboard"
    })


@app.get("/api/stats")
async def get_stats():
    """Obtiene estadísticas actuales del sistema."""
    folder_stats = get_folder_stats()
    processed_stats = get_processed_index_stats()

    return JSONResponse({
        "folders": folder_stats,
        "processed": processed_stats,
        "processing": processing_status,
        "timestamp": datetime.now().isoformat()
    })


@app.post("/api/process")
async def process_photos(background_tasks: BackgroundTasks, batch_id: Optional[str] = None):
    """Inicia el procesamiento de fotos en background."""
    if processing_status["is_processing"]:
        return JSONResponse({
            "success": False,
            "message": "Ya hay un procesamiento en curso"
        }, status_code=409)

    # Ejecutar en background
    background_tasks.add_task(process_photos_background, batch_id)

    return JSONResponse({
        "success": True,
        "message": "Procesamiento iniciado",
        "timestamp": datetime.now().isoformat()
    })


@app.post("/api/remove-background")
async def remove_background_endpoint():
    """Quita el fondo de las fotos en output/ y las guarda en output_white/."""
    try:
        from src.core.background_remover import BackgroundRemover

        output_dir = Path("./output")
        output_white_dir = Path("./output_white")
        output_white_dir.mkdir(parents=True, exist_ok=True)

        if not output_dir.exists() or not any(output_dir.iterdir()):
            return JSONResponse({
                "success": False,
                "message": "No hay fotos en output/ para procesar"
            })

        remover = BackgroundRemover()
        processed = 0

        for img_file in output_dir.glob("*"):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                output_path = output_white_dir / f"{img_file.stem}.jpg"
                success = remover.remove_background(
                    input_path=img_file,
                    output_path=output_path,
                    background_color=(255, 255, 255, 255)
                )
                if success:
                    processed += 1

        return JSONResponse({
            "success": True,
            "message": f"Fondo removido de {processed} fotos",
            "processed": processed,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.post("/api/convert-format")
async def convert_format_endpoint():
    """Convierte fotos de output_white/ al formato original en output_final/."""
    try:
        from src.core.format_converter import convert_to_original_format

        output_white_dir = Path("./output_white")

        if not output_white_dir.exists() or not any(output_white_dir.iterdir()):
            return JSONResponse({
                "success": False,
                "message": "No hay fotos en output_white/ para convertir"
            })

        stats = convert_to_original_format(
            input_dir="./output_white",
            output_dir="./output_final",
            metadata_dir="./metadata",
            quality=95
        )

        return JSONResponse({
            "success": True,
            "message": f"Convertidas {stats['converted']} fotos al formato original",
            "converted": stats['converted'],
            "failed": stats['failed'],
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.get("/api/logs")
async def get_logs(lines: int = 50):
    """Obtiene las últimas líneas del log."""
    logs = get_recent_logs(lines)

    return JSONResponse({
        "logs": logs,
        "count": len(logs)
    })


@app.get("/api/images/{folder}")
async def get_images(folder: str, limit: int = 20):
    """Lista imágenes en una carpeta específica."""
    folder_map = {
        "output": "./output",
        "output_white": "./output_white",
        "output_final": "./output_final",
        "manual_review": "./manual_review",
        "errors": "./errors",
        "input_raw": "./input_raw"
    }

    if folder not in folder_map:
        return JSONResponse({
            "error": "Carpeta no válida"
        }, status_code=400)

    images = get_images_in_folder(folder_map[folder], limit)

    return JSONResponse({
        "folder": folder,
        "images": images,
        "count": len(images)
    })


@app.get("/api/health")
async def health_check():
    """Endpoint de health check."""
    return JSONResponse({
        "status": "healthy",
        "service": "PhotoCrop Dashboard",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

