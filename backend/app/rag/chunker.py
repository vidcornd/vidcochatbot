from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(pages: list[dict]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150,separators=["\n\n", "\n", ". ", " ", ""])

    documents = []
    for page in pages:
        text = page["text"]
        metadata = page["metadata"]

        page_docs = splitter.create_documents(texts=[text],metadatas=[metadata])

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

    print(f"Created chunks: {len(documents)}")
    return documents