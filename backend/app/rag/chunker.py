from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
logger = logging.getLogger(__name__)

HEADING_MAX_LENGTH = 55
HEADING_END_CHARS = (".", ",", ";", ":")
MIN_SEGMENT_LENGTH = 200

def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > HEADING_MAX_LENGTH:
        return False
    if stripped[-1] in HEADING_END_CHARS:
        return False
    if not stripped[0].isupper():
        return False
    return True

def _split_by_headings(text: str) -> list[tuple[str | None, str]]:
    segments: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.split("\n"):
        if _looks_like_heading(line):
            if current_lines:
                segments.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        segments.append((current_heading, "\n".join(current_lines).strip()))

    return _merge_small_segments([(heading, body) for heading, body in segments if body])

def _merge_small_segments(segments: list[tuple[str | None, str]]) -> list[tuple[str | None, str]]:
    merged: list[tuple[str | None, str]] = []
    buffer_heading: str | None = None
    buffer_parts: list[str] = []
    buffer_len = 0

    for heading, body in segments:
        if buffer_parts:
            piece = f"{heading}\n{body}" if heading else body
            buffer_parts.append(piece)
            buffer_len += len(piece)
        else:
            buffer_heading = heading
            buffer_parts = [body]
            buffer_len = len(body)

        if buffer_len >= MIN_SEGMENT_LENGTH:
            merged.append((buffer_heading, "\n".join(buffer_parts)))
            buffer_heading, buffer_parts, buffer_len = None, [], 0

    if buffer_parts:
        merged.append((buffer_heading, "\n".join(buffer_parts)))

    return merged

def create_chunks(pages: list[dict]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150,separators=["\n\n", "\n", ". ", " ", ""])

    documents = []
    for page in pages:
        text = page["text"]
        metadata = page["metadata"]

        page_docs = []
        for heading, body in _split_by_headings(text):
            segment_docs = splitter.create_documents(texts=[body],metadatas=[metadata])
            for doc in segment_docs:
                if heading:
                    doc.page_content = f"{heading}\n{doc.page_content}"
            page_docs.extend(segment_docs)

        source = metadata["source"]
        page_number = metadata["page"]
        document_id = metadata.get("document_id") or source.replace(".pdf", "")

        for index, doc in enumerate(page_docs):
            doc.metadata["source"] = source
            doc.metadata["title"] = metadata.get("title", source)
            doc.metadata["page"] = page_number
            doc.metadata["document_id"] = document_id
            doc.metadata["doc_id"] = document_id
            doc.metadata["chunk_index"] = index + 1
            doc.metadata["chunk_id"] = f"{document_id}_p{metadata['page']}_c{index+1}"

            if "file_hash" in metadata:
                doc.metadata["file_hash"] = metadata["file_hash"]

            documents.append(doc)

    logger.info("Created chunks: %d",len(documents))
    return documents