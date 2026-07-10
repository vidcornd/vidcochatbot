from typing import Any
from langchain_chroma import Chroma
from app.config import settings
from app.rag.vectorstore import get_embeddings

CONCEPT_COLLECTION_NAME = "vidco_concepts"

class ConceptRetriever:
    def __init__(self) -> None:
        self.vectorstore = Chroma(collection_name=CONCEPT_COLLECTION_NAME,embedding_function=get_embeddings(),persist_directory=settings.chroma_path)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        docs_with_scores = self.vectorstore.similarity_search_with_score(query=query,k=top_k,filter={"type": "concept"})
        concepts: list[dict[str, Any]] = []
        for doc, score in docs_with_scores:
            metadata = doc.metadata or {}
            concepts.append({
                    "concept_id": metadata.get("concept_id"),
                    "name": metadata.get("name"),
                    "text": doc.page_content,
                    "score": score,
                    "match_type": "vector"})
        return concepts