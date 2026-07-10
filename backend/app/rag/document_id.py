import re
import unicodedata
from pathlib import Path

def normalize_to_id(value: str, fallback: str = "document") -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")

    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")

    return normalized or fallback

def normalize_document_id(file_path: Path) -> str:
    return normalize_to_id(file_path.stem)

def normalize_source_id(source: str) -> str:
    return normalize_to_id(source)