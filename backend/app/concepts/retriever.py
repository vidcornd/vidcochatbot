from typing import Any
from langchain_postgres import PGVector
from app.config import settings
from app.rag.vectorstore import get_embeddings

CONCEPT_COLLECTION_NAME = "vidco_concepts"

class ConceptRetriever:
    def __init__(self) -> None:
        self._vectorstore: PGVector | None = None

    def get_vectorstore(self) -> PGVector:
        if self._vectorstore is None:
            self._vectorstore = PGVector(embeddings=get_embeddings(),collection_name=CONCEPT_COLLECTION_NAME,connection=settings.database_url,use_jsonb=True,create_extension=False)

        return self._vectorstore

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        docs_with_scores = self.get_vectorstore().similarity_search_with_score(query=query,k=top_k,filter={"type": "concept"})
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