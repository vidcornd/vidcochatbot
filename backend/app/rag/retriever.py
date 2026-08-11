import re

from app.rag.vectorstore import get_vectorstore

def detect_metadata_filter(question: str) -> dict | None:
    question_lower = question.casefold()

    has_android = "android" in question_lower
    has_apple = any(keyword in question_lower for keyword in ["apple", "ios", "iphone", "ipad"])

    if has_android and has_apple:
        return None

    if has_android:
        return {"doc_id": "mobil_android"}

    if has_apple:
        return {"doc_id": "mobil_apple"}

    return None


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.casefold())
    return [token for token in tokens if len(token) >= 3]


def lexical_bonus(question: str, content: str) -> float:
    question_tokens = set(tokenize(question))
    content_tokens = set(tokenize(content))

    if not question_tokens:
        return 0.0

    overlap = question_tokens.intersection(content_tokens)

    return min(len(overlap), 8) * 0.03


def rerank_chunks(question: str, results: list[tuple]) -> list[tuple]:
    reranked = []

    for document, score in results:
        bonus = lexical_bonus(question, document.page_content)
        rerank_score = float(score) - bonus
        reranked.append((document, score, rerank_score))

    reranked.sort(key=lambda item: item[2])
    return reranked

MAX_RELEVANT_SCORE = 0.70

def filter_relevant(reranked_results: list[tuple]) -> list[tuple]:
    return [item for item in reranked_results if item[1] <= MAX_RELEVANT_SCORE]

def retrieve_relevant_chunks(question: str, k: int = 3, fetch_k: int = 10):
    vectorstore = get_vectorstore()
    metadata_filter = detect_metadata_filter(question)

    search_kwargs = {"query": question,"k": fetch_k,}

    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    results = vectorstore.similarity_search_with_score(**search_kwargs)

    if not results and metadata_filter:
        results = vectorstore.similarity_search_with_score(query=question,k=fetch_k)

    reranked_results = rerank_chunks(question, results)
    relevant_results = filter_relevant(reranked_results)
    selected_results = relevant_results[:k]

    chunks = []
    for document, score, rerank_score in selected_results:
        chunks.append({"content": document.page_content,"metadata": document.metadata,"score": float(score),"rerank_score": float(rerank_score)})
    
    return chunks


def format_context(chunks: list[dict]) -> str:
    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        source_label = (f"{metadata.get('title', metadata.get('source'))}, s. {metadata.get('page')}")
        context_parts.append(f"[Kaynak {index}: {source_label}]\n{chunk['content']}")

    return "\n\n---\n\n".join(context_parts)


def extract_sources(chunks: list[dict]) -> list[dict]:
    seen = set()
    sources = []

    for chunk in chunks:
        metadata = chunk["metadata"]
        key = (metadata.get("title"), metadata.get("page"))

        if key in seen:
            continue

        seen.add(key)
        sources.append({"title": metadata.get("title"),"source": metadata.get("source"),"page": metadata.get("page")})

    return sources