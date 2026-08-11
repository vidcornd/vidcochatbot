from langchain_core.documents import Document
from app.rag.retriever import MAX_RELEVANT_SCORE, filter_relevant, lexical_bonus, rerank_chunks

def make_result(content: str, score: float) -> tuple:
    return (Document(page_content=content, metadata={}), score)

def test_lexical_bonus_counts_shared_tokens():
    bonus = lexical_bonus("toplu firma kaydı nasıl oluşturulur", "toplu firma kaydı için Admin girişi gerekir")
    assert bonus > 0.0

def test_lexical_bonus_zero_when_no_overlap():
    assert lexical_bonus("firma nasıl eklenir", "cihaz kalibrasyonu tamamlandı") == 0.0

def test_rerank_sorts_by_rerank_score_ascending():
    results = [make_result("alakasız içerik", 0.30), make_result("çok alakalı içerik", 0.50)]
    reranked = rerank_chunks("alakalı", results)
    assert reranked[0][2] <= reranked[1][2]

def test_filter_relevant_drops_low_score_chunks():
    reranked = [
        (Document(page_content="a"), 0.20, 0.20),
        (Document(page_content="b"), MAX_RELEVANT_SCORE, MAX_RELEVANT_SCORE),
        (Document(page_content="c"), MAX_RELEVANT_SCORE + 0.01, MAX_RELEVANT_SCORE + 0.01),
        (Document(page_content="d"), 0.95, 0.60),
    ]
    filtered = filter_relevant(reranked)
    assert [item[0].page_content for item in filtered] == ["a", "b"]


def test_filter_relevant_uses_raw_score_not_rerank_score():
    reranked = [(Document(page_content="d"), 0.95, 0.60)]
    assert filter_relevant(reranked) == []