import shutil
from pathlib import Path
from typing import Iterable, TypeVar
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.config import settings

T = TypeVar("T")

def batch_list(items: list[T], batch_size: int) -> Iterable[list[T]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model=settings.embedding_model,google_api_key=settings.google_api_key)


def reset_chroma():
    chroma_path = Path(settings.chroma_path)

    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        print(f"Deleted existing Chroma directory: {settings.chroma_path}")


def get_vectorstore():
    embeddings = get_embeddings()

    return Chroma(collection_name=settings.chroma_collection,embedding_function=embeddings,persist_directory=settings.chroma_path)

def delete_document_chunks(document_id: str) -> None:
    vectorstore = get_vectorstore()
    try:
        vectorstore._collection.delete(where={"document_id": document_id})
        print(f"Deleted old chunks for document_id: {document_id}")
    except Exception as error:
        print(f"Could not delete chunks for document_id={document_id}: {error}")
        raise

def ingest_documents(documents, reset: bool = False,batch_size: int = 32):
    if reset:
        reset_chroma()

    if not documents:
        raise ValueError("No documents to ingest.")

    vectorstore = get_vectorstore()
    total_documents = len(documents)

    for batch_number, batch in enumerate(batch_list(documents, batch_size), start=1):
        vectorstore.add_documents(batch)
        print(f"Ingested batch {batch_number}: {len(batch)} chunks ({min(batch_number * batch_size, total_documents)}/{total_documents})")

    print(f"Ingested chunks: {total_documents}")
    print(f"Collection: {settings.chroma_collection}")
    print(f"Persist directory: {settings.chroma_path}")

    return vectorstore