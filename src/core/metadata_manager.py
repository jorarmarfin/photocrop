"""
Gestor de metadatos para el pipeline de procesamiento de imágenes.
Maneja la creación, actualización y persistencia de archivos JSON de metadatos.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List, Any


class MetadataManager:
    """Gestiona los archivos de metadatos JSON para cada imagen procesada."""

    def __init__(self, metadata_base_dir: str = "./metadata"):
        self.metadata_base_dir = Path(metadata_base_dir)
        self.metadata_version = "1.0"

    def create_metadata(
        self,
        filename: str,
        input_path: str,
        batch_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        img_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crea un nuevo diccionario de metadatos con valores iniciales."""

        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        orientation = self._calculate_orientation(width, height) if width and height else None

        metadata = {
            "filename": filename,
            "input_path": input_path,
            "current_path": input_path,
            "output_path": None,
            "format": img_format,
            "width": width,
            "height": height,
            "orientation": orientation,
            "face_detected": False,
            "num_faces": 0,
            "face_box": None,
            "status": "pending",
            "error_message": None,
            "processing_time": timestamp,
            "batch_id": batch_id,
            "notes": None,
            "metadata_version": self.metadata_version,
            "last_updated": timestamp,
            "processing_history": [
                {
                    "timestamp": timestamp,
                    "action": "initial_scan",
                    "status": "pending"
                }
            ]
        }

        return metadata

    def update_metadata(
        self,
        metadata: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Actualiza campos específicos del metadata y registra en el historial."""

        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        metadata["last_updated"] = timestamp

        # Actualizar campos proporcionados
        for key, value in kwargs.items():
            if key in metadata:
                metadata[key] = value

        # Registrar en historial si hay cambio de estado
        if "status" in kwargs:
            history_entry = {
                "timestamp": timestamp,
                "action": kwargs.get("action", "update"),
                "status": kwargs["status"]
            }
            if "details" in kwargs:
                history_entry["details"] = kwargs["details"]

            metadata["processing_history"].append(history_entry)

        return metadata

    def save_metadata(self, metadata: Dict[str, Any], batch_id: str) -> Path:
        """Guarda el metadata en un archivo JSON."""

        # Crear estructura de directorios
        year = datetime.now(timezone.utc).year
        metadata_dir = self.metadata_base_dir / str(year) / batch_id
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre de archivo
        filename = Path(metadata["filename"]).stem + ".json"
        metadata_path = metadata_dir / filename

        # Guardar JSON
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata_path

    def load_metadata(self, filename: str, batch_id: str) -> Optional[Dict[str, Any]]:
        """Carga metadata existente si está disponible."""

        year = datetime.now(timezone.utc).year
        metadata_dir = self.metadata_base_dir / str(year) / batch_id
        json_filename = Path(filename).stem + ".json"
        metadata_path = metadata_dir / json_filename

        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None

    def create_batch_summary(
        self,
        batch_id: str,
        metadata_list: List[Dict[str, Any]],
        batch_path: str
    ) -> Dict[str, Any]:
        """Crea un resumen del lote procesado."""

        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Calcular estadísticas
        total = len(metadata_list)
        stats = {
            "processed": 0,
            "manual_review": 0,
            "errors": 0,
            "pending": 0
        }

        breakdown = {
            "face_detected_single": 0,
            "face_detected_multiple": 0,
            "no_face_detected": 0,
            "corrupted_files": 0
        }

        images = []

        for meta in metadata_list:
            status = meta.get("status", "pending")
            stats[status] = stats.get(status, 0) + 1

            # Breakdown detallado
            if meta.get("status") == "error":
                breakdown["corrupted_files"] += 1
            elif meta.get("num_faces") == 1:
                breakdown["face_detected_single"] += 1
            elif meta.get("num_faces") > 1:
                breakdown["face_detected_multiple"] += 1
            elif meta.get("num_faces") == 0 and meta.get("status") == "manual_review":
                breakdown["no_face_detected"] += 1

            # Resumen de imagen
            img_summary = {
                "filename": meta["filename"],
                "status": meta["status"],
                "face_detected": meta.get("face_detected", False)
            }
            if meta.get("num_faces", 0) > 1:
                img_summary["num_faces"] = meta["num_faces"]
            if meta.get("error_message"):
                img_summary["error"] = "corrupted file"

            images.append(img_summary)

        success_rate = stats["processed"] / total if total > 0 else 0
        requires_attention = stats["manual_review"] + stats["errors"]

        summary = {
            "batch_id": batch_id,
            "batch_path": batch_path,
            "processing_date": timestamp,
            "completion_date": timestamp,
            "total_images": total,
            "statistics": stats,
            "breakdown": breakdown,
            "success_rate": round(success_rate, 2),
            "requires_manual_attention": requires_attention,
            "images": images,
            "metadata_version": self.metadata_version,
            "pipeline_version": "1.0.0"
        }

        return summary

    def save_batch_summary(self, summary: Dict[str, Any]) -> Path:
        """Guarda el resumen del lote."""

        year = datetime.now(timezone.utc).year
        batch_id = summary["batch_id"]
        summary_dir = self.metadata_base_dir / str(year) / batch_id
        summary_dir.mkdir(parents=True, exist_ok=True)

        summary_path = summary_dir / "batch_summary.json"

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return summary_path

    @staticmethod
    def _calculate_orientation(width: int, height: int) -> str:
        """Calcula la orientación de la imagen."""
        ratio = width / height
        if ratio > 1.1:
            return "landscape"
        elif ratio < 0.9:
            return "portrait"
        else:
            return "square"

