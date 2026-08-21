import json
import logging
from pathlib import Path
from typing import Any
from langchain_postgres import PGVector
from langchain_core.documents import Document
from app.concepts.formatter import concept_to_text
from app.config import settings
from app.rag.vectorstore import get_embeddings

logger = logging.getLogger(__name__)

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

def get_concept_vectorstore() -> PGVector:
    embeddings = get_embeddings()
    return PGVector(embeddings=embeddings,collection_name=CONCEPT_COLLECTION_NAME,connection=settings.database_url,use_jsonb=True,create_extension=False)

def ingest_concepts() -> None:
    concepts = load_concepts()

    for concept_id, concept in concepts.items():
        validate_concept(concept_id, concept)

    if not concepts:
        logger.info("concepts.json boş. Eklenecek kavram yok.")
        return

    documents: list[Document] = []
    ids: list[str] = []

    for concept_id, concept in concepts.items():
        documents.append(
            Document(
                page_content=concept_to_text(concept),
                metadata={
                    "type": "concept",
                    "concept_id": concept_id,
                    "name": concept["name"],
                },
            )
        )
        ids.append(concept_id)

    vectorstore = get_concept_vectorstore()
    vectorstore.delete(ids=ids)
    vectorstore.add_documents(documents=documents, ids=ids)

    logger.info("%d kavram (yeniden) yüklendi.",len(ids))

if __name__ == "__main__":
    from app.logging_config import configure_logging

    configure_logging()
    ingest_concepts()