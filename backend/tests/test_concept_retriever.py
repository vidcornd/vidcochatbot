from unittest.mock import patch

from app.concepts.retriever import ConceptRetriever


def test_constructor_does_not_touch_the_database():
    with patch("app.concepts.retriever.PGVector") as mock_pgvector:
        ConceptRetriever()

    assert mock_pgvector.called is False


def test_vectorstore_is_built_once_on_first_use():
    with patch("app.concepts.retriever.PGVector") as mock_pgvector, \
         patch("app.concepts.retriever.get_embeddings"):
        retriever = ConceptRetriever()

        first = retriever.get_vectorstore()
        second = retriever.get_vectorstore()

    assert mock_pgvector.call_count == 1
    assert first is second
