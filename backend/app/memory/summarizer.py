from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.memory.redis_store import get_conversation, save_summary, clear_conversation, save_message

SUMMARY_TRIGGER_MESSAGES = 8
RAW_MESSAGES_TO_KEEP = 4

def get_chat_model():
    return ChatGoogleGenerativeAI(model=settings.chat_model,google_api_key=settings.google_api_key,temperature=0.1)

def format_messages(messages: list[dict]) -> str:
    formatted_messages = []
    for message in messages:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        formatted_messages.append(f"{role}: {content}")
    return "\n".join(formatted_messages)


def summarize_conversation_if_needed(conversation_id: str) -> None:
    conversation = get_conversation(conversation_id)
    current_summary = conversation["summary"]
    messages = conversation["messages"]

    if len(messages) <= SUMMARY_TRIGGER_MESSAGES:
        return

    messages_to_summarize = messages[:-RAW_MESSAGES_TO_KEEP]
    messages_to_keep = messages[-RAW_MESSAGES_TO_KEEP:]

    old_messages_text = format_messages(messages_to_summarize)

    prompt = f"""
    Aşağıdaki konuşma geçmişini kısa ve bilgi yoğun şekilde özetle.

    Amaç:
    - Kullanıcının ne sorduğunu
    - Asistanın hangi bilgileri verdiğini
    - Devam sorularında gerekli olabilecek bağlamı

    Kurallar:
    - Türkçe yaz.
    - Gereksiz detay ekleme.
    - Kaynaklarda olmayan teknik bilgi uydurma.
    - Maksimum 6 madde kullan.

    Mevcut özet:
    {current_summary}

    Özetlenecek eski mesajlar:
    {old_messages_text}
    """

    llm = get_chat_model()
    response = llm.invoke(prompt)

    new_summary = response.content

    clear_conversation(conversation_id)
    save_summary(conversation_id, new_summary)

    for message in messages_to_keep:
        save_message(conversation_id=conversation_id,role=message["role"],content=message["content"])

def build_memory_context(conversation_id: str) -> str:
    conversation = get_conversation(conversation_id)
    summary = conversation["summary"]
    messages = conversation["messages"][-RAW_MESSAGES_TO_KEEP:]

    memory_parts = []

    if summary:
        memory_parts.append(f"Konuşma özeti:\n{summary}")
    if messages:
        memory_parts.append(f"Son mesajlar:\n{format_messages(messages)}")
    return "\n\n".join(memory_parts)