from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from app.config import settings
import logging
logger = logging.getLogger(__name__)

LLM_CALL_TIMEOUT_SECONDS = 20

def get_chat_model(temperature: float = 0.1):
    if settings.chat_provider == "deepseek":
        return ChatDeepSeek(model=settings.deepseek_model,api_key=settings.deepseek_api_key,temperature=temperature,timeout=LLM_CALL_TIMEOUT_SECONDS)

    return ChatGoogleGenerativeAI(model=settings.chat_model,google_api_key=settings.google_api_key,temperature=temperature,timeout=LLM_CALL_TIMEOUT_SECONDS)

def check_chat_provider_reachable() -> bool:
    try:
        get_chat_model().invoke("ping")
        return True
    except Exception as error:
        logger.warning("Chat provider (%s) reachability check failed: %s",settings.chat_provider,error)
        return False