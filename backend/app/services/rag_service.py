from typing import Any
from app.concepts.resolver import ConceptResolver
from app.rag.rewriter import rewrite_follow_up_question
from app.rag.retriever import retrieve_relevant_chunks
from app.rag.generator import answer_question

class RagService:
    def __init__(self) -> None:
        self.concept_resolver = ConceptResolver()

    def prepare_query(self, user_query: str) -> dict[str, Any]:
        concepts = self.concept_resolver.resolve(user_query)
        concept_context = self.concept_resolver.build_context(concepts)

        rewritten_query = rewrite_follow_up_question(question=user_query,memory_context="",concept_context=concept_context)

        return {
            "original_query": user_query,
            "concepts": concepts,
            "concept_context": concept_context,
            "rewritten_query": rewritten_query,
        }
    
    def retrieve_documents(self, user_query: str, k: int = 3, fetch_k: int = 10) -> dict[str, Any]:
        prepared_query = self.prepare_query(user_query)
        rewritten_query = prepared_query["rewritten_query"]

        chunks = retrieve_relevant_chunks(question=rewritten_query,k=k,fetch_k=fetch_k,)

        return {**prepared_query,"chunks": chunks}
    
    def answer(self, user_query: str, memory_context: str = "", request_id: str | None = None,user_roles: list[str] | None = None, current_page: str | None = None) -> dict[str, Any]:
        concepts = self.concept_resolver.resolve(user_query)
        concept_context = self.concept_resolver.build_context(concepts)

        rewritten_query = rewrite_follow_up_question(question=user_query,memory_context=memory_context,concept_context=concept_context)
        result = answer_question(question=user_query,memory_context=memory_context,retrieval_query=rewritten_query,concept_context=concept_context,concepts=concepts,request_id=request_id,user_roles=user_roles,current_page=current_page)

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "original_query": user_query,
            "rewritten_query": rewritten_query,
            "concepts": concepts,
            "concept_context": concept_context,
        }