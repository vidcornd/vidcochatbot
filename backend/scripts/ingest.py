import argparse
from pathlib import Path
from app.rag.pdf_loader import load_pdf, load_all_pdfs
from app.rag.chunker import create_chunks
from app.rag.vectorstore import (delete_document_chunks,ingest_documents,reset_chroma)
from app.rag.document_id import normalize_document_id
from app.rag.document_registry import (calculate_file_hash,is_document_unchanged,load_registry,reset_registry,save_registry,update_document_record)
import logging
from app.logging_config import configure_logging
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")

def enrich_pages_metadata(pages: list[dict],document_id: str,file_hash: str) -> list[dict]:
    for page in pages:
        page["metadata"]["document_id"] = document_id
        page["metadata"]["file_hash"] = file_hash

    return pages

def ingest_pdf(pdf_path: Path,registry: dict) -> tuple[int, int]:
    source = pdf_path.name
    document_id = normalize_document_id(pdf_path)
    file_hash = calculate_file_hash(pdf_path)

    if is_document_unchanged(registry, source, file_hash):
        logger.info("[SKIP] %s unchanged",source)
        return 0, 1

    logger.info("[INGEST] %s",source)

    if source in registry:
        delete_document_chunks(document_id)

    pages = load_pdf(str(pdf_path))
    pages = enrich_pages_metadata(pages=pages,document_id=document_id,file_hash=file_hash)
    chunks = create_chunks(pages)
    ingest_documents(chunks)
    update_document_record(registry=registry,source=source,document_id=document_id,file_hash=file_hash,chunk_count=len(chunks))
    save_registry(registry)

    return len(chunks), 0

def main():
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset",action="store_true",help="Reset ChromaDB and ingest registry before ingesting")
    args = parser.parse_args()

    logger.info("Starting ingestion...")

    if args.reset:
        reset_chroma()
        reset_registry()

    registry = load_registry()
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.info("No PDF files found in %s",RAW_DIR)
        return

    ingested_documents = 0
    skipped_documents = 0
    total_chunks = 0
    for pdf_file in pdf_files:
        chunks, skipped = ingest_pdf(pdf_file, registry)
        if skipped:
            skipped_documents += 1
        else:
            ingested_documents += 1
            total_chunks += chunks

    logger.info("Ingest summary: total_pdf_files=%d indexed_documents=%d skipped_documents=%d total_new_chunks=%d",len(pdf_files),ingested_documents,skipped_documents,total_chunks)
    logger.info("Ingestion completed.")


if __name__ == "__main__":
    main()