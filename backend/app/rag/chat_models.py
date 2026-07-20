from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from app.config import settings

def get_chat_model(temperature: float = 0.1):
    if settings.chat_provider == "deepseek":
        return ChatDeepSeek(model=settings.deepseek_model,api_key=settings.deepseek_api_key,temperature=temperature)

    return ChatGoogleGenerativeAI(model=settings.chat_model,google_api_key=settings.google_api_key,temperature=temperature)