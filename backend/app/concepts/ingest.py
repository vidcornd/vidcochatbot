import hashlib
import json
from pathlib import Path
from typing import Any
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.concepts.formatter import concept_to_text
from app.config import settings
from app.rag.vectorstore import get_embeddings

BASE_DIR = Path(__file__).resolve().parents[2]
CONCEPTS_PATH = BASE_DIR / "data" / "concepts.json"
CONCEPT_COLLECTION_NAME = "vidco_concepts"
OPTIONAL_LIST_FIELDS = ["synonyms", "examples", "related"]

def load_concepts() -> dict[str, dict[str, Any]]:
    if not CONCEPTS_PATH.exists():
        raise FileNotFoundError(f"Concepts file not found: {CONCEPTS_PATH}")

    try:
        concepts = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file: {CONCEPTS_PATH}") from exc

    if not isinstance(concepts, dict):
        raise ValueError("concepts.json must be a JSON object.")

    return concepts


def validate_optional_list_field(concept_id: str,concept: dict[str, Any],field: str) -> None:
    if field not in concept:
        return

    if not isinstance(concept[field], list):
        raise ValueError(f"Invalid concept format. concept_id={concept_id}, field={field} must be a list.")

    for item in concept[field]:
        if not isinstance(item, str):
            raise ValueError(f"Invalid concept format. concept_id={concept_id}, field={field} must contain only strings.")

def validate_distinguish_from(concept_id: str,concept: dict[str, Any]) -> None:
    if "distinguish_from" not in concept:
        return

    distinguish_from = concept["distinguish_from"]

    if not isinstance(distinguish_from, dict):
        raise ValueError(f"Invalid concept format. concept_id={concept_id}, distinguish_from must be an object.")

    for other_concept, explanation in distinguish_from.items():
        if not isinstance(other_concept, str) or not other_concept.strip():
            raise ValueError(f"Invalid concept format. concept_id={concept_id}, distinguish_from keys must be non-empty strings.")

        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError(f"Invalid concept format. concept_id={concept_id}, distinguish_from values must be non-empty strings.")

def validate_concept(concept_id: str, concept: dict[str, Any]) -> None:
    if not isinstance(concept, dict):
        raise ValueError(f"Invalid concept format. concept_id={concept_id} must map to an object.")

    required_fields = ["name", "definition"]

    for field in required_fields:
        if field not in concept:
            raise ValueError(f"Invalid concept format. concept_id={concept_id}, missing field={field}.")

    if not isinstance(concept["name"], str) or not concept["name"].strip():
        raise ValueError(f"Invalid concept name. concept_id={concept_id}")

    if not isinstance(concept["definition"], str) or not concept["definition"].strip():
        raise ValueError(f"Invalid concept definition. concept_id={concept_id}")

    for field in OPTIONAL_LIST_FIELDS:
        validate_optional_list_field(concept_id, concept, field)

    validate_distinguish_from(concept_id, concept)

def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_raw_collection():
    client = chromadb.PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection(name=CONCEPT_COLLECTION_NAME)

def get_concept_vectorstore() -> Chroma:
    embeddings = get_embeddings()
    return Chroma(collection_name=CONCEPT_COLLECTION_NAME,embedding_function=embeddings,persist_directory=settings.chroma_path)

def get_existing_concepts() -> dict[str, dict[str, Any]]:
    collection = get_raw_collection()
    result = collection.get(where={"type": "concept"},include=["metadatas"])

    existing: dict[str, dict[str, Any]] = {}

    ids = result.get("ids", [])
    metadatas = result.get("metadatas", [])

    for concept_id, metadata in zip(ids, metadatas):
        existing[concept_id] = metadata or {}
    return existing


def delete_concepts(ids: list[str]) -> None:
    if not ids:
        return

    collection = get_raw_collection()
    collection.delete(ids=ids)

def ingest_concepts() -> None:
    concepts = load_concepts()
    existing = get_existing_concepts()

    current_ids = set(concepts.keys())
    existing_ids = set(existing.keys())

    ids_to_delete = sorted(existing_ids - current_ids)

    documents_to_upsert: list[Document] = []
    ids_to_upsert: list[str] = []
    unchanged_count = 0

    for concept_id, concept in concepts.items():
        validate_concept(concept_id, concept)

        document_text = concept_to_text(concept)
        document_hash = text_hash(document_text)

        old_metadata = existing.get(concept_id)
        old_hash = old_metadata.get("content_hash") if old_metadata else None

        if old_hash == document_hash:
            unchanged_count += 1
            continue

        documents_to_upsert.append(
            Document(
                page_content=document_text,
                metadata={
                    "type": "concept",
                    "concept_id": concept_id,
                    "name": concept["name"],
                    "content_hash": document_hash,
                },
            )
        )
        ids_to_upsert.append(concept_id)

    if ids_to_delete:
        delete_concepts(ids_to_delete)

    if ids_to_upsert:
        delete_concepts(ids_to_upsert)

        vectorstore = get_concept_vectorstore()
        vectorstore.add_documents(documents=documents_to_upsert,ids=ids_to_upsert)

    print(f"{len(ids_to_upsert)} kavram eklendi/güncellendi.")
    print(f"{len(ids_to_delete)} kavram silindi.")
    print(f"{unchanged_count} kavram değişmedi.")

    if not concepts:
        print("concepts.json boş. Eklenecek kavram yok.")

if __name__ == "__main__":
    ingest_concepts()