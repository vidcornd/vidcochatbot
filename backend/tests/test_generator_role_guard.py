from unittest.mock import MagicMock, patch

from app.rag.generator import answer_question

REAL_CHUNK_TEXT = (
    "Muayeneyi Onaya Gönderme Akışı\n"
    "Muayenenin onaya gönderilebilmesi için sistem kontrollerinden geçmiş olması gerekir. "
    "Onaylayan seçimi. Onaya gönderirken açıklama yazılabilir. Muayeneyi yapan kişi onay "
    "yetkisine de sahipse kendi muayenesini kendisi onaylayabilir; muayene kaydı "
    "güncellenerek onaylayan kişi veya muayene tarih/saati değiştirilebilir."
)

QUESTION = "Muayene onay personeli kendi yaptığı muayeneyi onaylayabilir mi?"

def fake_chunks() -> list[dict]:
    return [{
        "content": REAL_CHUNK_TEXT,
        "score": 0.2,
        "metadata": {"source": "is_emri_ve_muayene_yonetimi.pdf", "page": 7, "title": "İş Emri ve Muayene Yönetimi"}}]


def test_user_without_required_role_is_redirected_without_calling_llm():
    with patch("app.rag.generator.retrieve_relevant_chunks", return_value=fake_chunks()), \
         patch("app.rag.generator.get_chat_model") as mock_get_llm:
        mock_get_llm.return_value.invoke.return_value = MagicMock(content="LLM cevabı")

        result = answer_question(question=QUESTION, concept_context="dummy", user_roles=["Muayene Personeli"])

        assert result["answer"] == "Bu işlem Muayene Onay Personeli yetkisi gerektiriyor, sistem yöneticinizle iletişime geçin."
        assert result["sources"] == []
        assert mock_get_llm.return_value.invoke.called is False


def test_user_with_required_role_gets_normal_answer():
    with patch("app.rag.generator.retrieve_relevant_chunks", return_value=fake_chunks()), \
         patch("app.rag.generator.get_chat_model") as mock_get_llm:
        mock_get_llm.return_value.invoke.return_value = MagicMock(content="LLM cevabı")

        result = answer_question(question=QUESTION, concept_context="dummy", user_roles=["Muayene Onay Personeli"])

        assert result["answer"] == "LLM cevabı"
        assert mock_get_llm.return_value.invoke.called is True


def test_admin_gets_normal_answer():
    with patch("app.rag.generator.retrieve_relevant_chunks", return_value=fake_chunks()), \
         patch("app.rag.generator.get_chat_model") as mock_get_llm:
        mock_get_llm.return_value.invoke.return_value = MagicMock(content="LLM cevabı")

        result = answer_question(question=QUESTION, concept_context="dummy", user_roles=["Admin"])

        assert result["answer"] == "LLM cevabı"
        assert mock_get_llm.return_value.invoke.called is True


def test_no_role_info_gets_normal_answer():
    with patch("app.rag.generator.retrieve_relevant_chunks", return_value=fake_chunks()), \
         patch("app.rag.generator.get_chat_model") as mock_get_llm:
        mock_get_llm.return_value.invoke.return_value = MagicMock(content="LLM cevabı")

        result = answer_question(question=QUESTION, concept_context="dummy", user_roles=[])

        assert result["answer"] == "LLM cevabı"
        assert mock_get_llm.return_value.invoke.called is True