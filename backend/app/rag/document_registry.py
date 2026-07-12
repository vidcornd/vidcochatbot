import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import logging
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("data/ingest_registry.json")

def calculate_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()

def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {}

    with REGISTRY_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_registry(registry: dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REGISTRY_PATH.open("w", encoding="utf-8") as file:
        json.dump(registry, file, ensure_ascii=False, indent=2)

def is_document_unchanged(registry: dict[str, Any],source: str,file_hash: str) -> bool:
    document_record = registry.get(source)

    if not document_record:
        return False

    return document_record.get("file_hash") == file_hash

def update_document_record(registry: dict[str, Any],source: str,document_id: str,file_hash: str,chunk_count: int) -> None:
    registry[source] = {"document_id": document_id,"file_hash": file_hash,"chunk_count": chunk_count,"last_ingested_at": datetime.now(timezone.utc).isoformat()}

def remove_document_record(registry: dict[str, Any],source: str) -> None:
    registry.pop(source, None)

def reset_registry() -> None:
    if REGISTRY_PATH.exists():
        REGISTRY_PATH.unlink()
        logger.info("Deleted ingest registry: %s",REGISTRY_PATH)