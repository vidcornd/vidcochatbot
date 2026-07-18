import concurrent.futures
from fastapi import APIRouter, Depends,HTTPException, Request
from app.services.rag_service import RagService
from app.schemas.chat import ChatRequest, ChatResponse
from app.memory.redis_store import save_message
from app.memory.summarizer import build_memory_context, summarize_conversation_if_needed
from app.rag.router import route_message
from app.api.errors import api_error
from app.api.rate_limit import (check_rate_limit,build_ip_rate_limit_key,build_conversation_rate_limit_key)
from app.api.auth import verify_widget_api_key
from app.schemas.feedback import FeedbackRequest
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"], dependencies=[Depends(verify_widget_api_key)])

rag_service = RagService()

ANSWER_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)
IP_RATE_LIMIT = 20
CONVERSATION_RATE_LIMIT = 10
RATE_LIMIT_WINDOW_SECONDS = 60
LLM_TIMEOUT_SECONDS = 40

def safe_save_message(conversation_id: str, role: str, content: str) -> None:
    try:
        save_message(conversation_id=conversation_id,role=role,content=content)
    except Exception:
        pass

def safe_summarize_conversation(conversation_id: str) -> None:
    try:
        summarize_conversation_if_needed(conversation_id)
    except Exception:
        pass

def safe_build_memory_context(conversation_id: str) -> str:
    try:
        return build_memory_context(conversation_id)
    except Exception:
        return ""

def run_rag_answer_with_timeout(question: str, memory_context: str, request_id: str) -> dict:
    future = ANSWER_EXECUTOR.submit(rag_service.answer,user_query=question,memory_context=memory_context,request_id=request_id)
    try:
        return future.result(timeout=LLM_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError:
        future.cancel()
        logger.warning("request_id=%s step=rag_answer status=timeout", request_id)
        raise api_error(status_code=504,error="timeout",message="Yanıt hazırlanırken zaman aşımı oluştu. Lütfen tekrar deneyin.")
    except Exception as exc:
        logger.exception("request_id=%s step=rag_answer status=error", request_id)
        raise api_error(status_code=503,error="llm_error",message="Yanıt üretme modeli geçici olarak kullanılamıyor. Lütfen kısa bir süre sonra tekrar deneyin.")

def check_chat_rate_limits(request: Request, conversation_id: str) -> None:
    client_host = "unknown"
    if request.client and request.client.host:
        client_host = request.client.host

    ip_key = build_ip_rate_limit_key(client_host)
    conversation_key = build_conversation_rate_limit_key(conversation_id)

    ip_allowed = check_rate_limit(key=ip_key,limit=IP_RATE_LIMIT,window_seconds=RATE_LIMIT_WINDOW_SECONDS)

    if not ip_allowed:
        raise api_error(status_code=429,error="rate_limit_exceeded",message="Çok fazla istek gönderildi. Lütfen biraz sonra tekrar deneyin.")

    conversation_allowed = check_rate_limit(key=conversation_key,limit=CONVERSATION_RATE_LIMIT,window_seconds=RATE_LIMIT_WINDOW_SECONDS)

    if not conversation_allowed:
        raise api_error(status_code=429,error="rate_limit_exceeded",message="Bu konuşma için çok fazla istek gönderildi. Lütfen biraz sonra tekrar deneyin.")

@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, chat_request: ChatRequest):
    request_id = str(uuid.uuid4())
    logger.info("request_id=%s step=received conversation_id=%s",request_id,chat_request.conversation_id)
    try:
        check_chat_rate_limits(request=request,conversation_id=chat_request.conversation_id)

        memory_context = safe_build_memory_context(chat_request.conversation_id)

        route = route_message(chat_request.message, memory_context, request_id=request_id)
        if route.get("needs_context") and not memory_context.strip():
            logger.info("request_id=%s step=routed intent=%s outcome=needs_context",request_id,route["intent"])
            result = {"answer": "Hangi işlemden sonra ne yapmanız gerektiğini belirtir misiniz? Örneğin muayene raporu, e-imza süreci veya mobil uygulama kurulumu hakkında sorabilirsiniz.","sources": [],"confidence": "low"}
            return ChatResponse(answer=result["answer"],sources=result["sources"],confidence=result["confidence"],conversation_id=chat_request.conversation_id)
        
        safe_save_message(conversation_id=chat_request.conversation_id,role="user",content=chat_request.message)

        if route["intent"] == "smalltalk":
            result = {"answer": route["smalltalk_response"] or "Vidco 17020 kullanım kılavuzları hakkında yardımcı olabilirim.","sources": [],"confidence": "high"}
        elif route["intent"] == "fallback":
            result = {"answer": "Bu bilgi Vidco 17020 kullanım kılavuzlarında açıkça bulunamadı.","sources": [],"confidence": "low"}
        else:
            result = run_rag_answer_with_timeout(question=chat_request.message,memory_context=memory_context,request_id=request_id)

        safe_save_message(conversation_id=chat_request.conversation_id,role="assistant",content=result["answer"])
        safe_summarize_conversation(chat_request.conversation_id)
        logger.info("request_id=%s step=answered intent=%s confidence=%s",request_id,route["intent"],result["confidence"])
        return ChatResponse(answer=result["answer"],sources=result["sources"],confidence=result["confidence"],conversation_id=chat_request.conversation_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("request_id=%s step=unhandled_error",request_id)
        raise api_error(status_code=500,error="internal_error",message="Beklenmeyen bir hata oluştu.")

@router.post("/feedback", status_code=204)
def feedback(feedback_request: FeedbackRequest):
    logger.info(
        "step=feedback conversation_id=%s rating=%s question=%r answer=%r",
        feedback_request.conversation_id,
        feedback_request.rating,
        feedback_request.question[:200],
        feedback_request.answer[:200])