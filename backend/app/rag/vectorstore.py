from typing import Iterable, TypeVar
from sqlalchemy import select
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings
import time
import logging
logger = logging.getLogger(__name__)

T = TypeVar("T")

def batch_list(items: list[T], batch_size: int) -> Iterable[list[T]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model=settings.embedding_model,google_api_key=settings.google_api_key)

def check_gemini_reachable() -> bool:
    try:
        get_embeddings().embed_query("ping")
        return True
    except Exception as error:
        logger.warning("Gemini reachability check failed: %s",error)
        return False

def reset_vectorstore():
    get_vectorstore().delete_collection()
    logger.info("Deleted existing vector collection: %s",settings.vector_collection)

def get_vectorstore():
    embeddings = get_embeddings()
    return PGVector(embeddings=embeddings,collection_name=settings.vector_collection,connection=settings.database_url,use_jsonb=True,create_extension=False)

def _matching_chunk_ids(vectorstore: PGVector, document_id: str) -> list[str]:
    with vectorstore._make_sync_session() as session:
        collection = vectorstore.get_collection(session)
        if not collection:
            return []

        stmt = (
            select(vectorstore.EmbeddingStore.id)
            .where(vectorstore.EmbeddingStore.collection_id == collection.uuid)
            .where(vectorstore.EmbeddingStore.cmetadata["document_id"].astext == document_id)
        )
        return [row[0] for row in session.execute(stmt).all()]


def delete_document_chunks(document_id: str) -> None:
    vectorstore = get_vectorstore()
    try:
        matching_ids = _matching_chunk_ids(vectorstore, document_id)
        if matching_ids:
            vectorstore.delete(ids=matching_ids)
        logger.info("Deleted old chunks for document_id: %s (%d chunks)",document_id,len(matching_ids))
    except Exception:
        logger.exception("Could not delete chunks for document_id=%s",document_id)
        raise

def _is_rate_limit_error(error: Exception) -> bool:
    message = str(error)
    return "429" in message or "RESOURCE_EXHAUSTED" in message

def _add_documents_with_retry(vectorstore, batch, batch_number: int, max_retries: int = 5) -> None:
    attempt = 0
    while True:
        try:
            vectorstore.add_documents(batch)
            return
        except Exception as error:
            if not _is_rate_limit_error(error) or attempt >= max_retries:
                raise
            wait_seconds = min(60, 10 * (attempt + 1))
            logger.warning("Rate limited on batch %d, retrying in %ds (attempt %d/%d)",batch_number,wait_seconds,attempt + 1,max_retries,)
            time.sleep(wait_seconds)
            attempt += 1

def ingest_documents(documents, reset: bool = False,batch_size: int = 32):
    if reset:
        reset_vectorstore()

    if not documents:
        raise ValueError("No documents to ingest.")

    vectorstore = get_vectorstore()
    total_documents = len(documents)

    for batch_number, batch in enumerate(batch_list(documents, batch_size), start=1):
        _add_documents_with_retry(vectorstore, batch, batch_number)
        logger.info("Ingested batch %d: %d chunks (%d/%d)",batch_number,len(batch),min(batch_number * batch_size, total_documents),total_documents,)

    logger.info("Ingested chunks: %d",total_documents)
    logger.info("Collection: %s",settings.vector_collection)

    return vectorstore