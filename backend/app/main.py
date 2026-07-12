from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.rag.vectorstore import get_vectorstore, check_gemini_reachable
from app.memory.redis_store import ping_redis
from app.schemas.chat import HealthResponse
from app.config import settings
from app.logging_config import configure_logging
import logging
configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Vidco 17020 RAG Assistant API",description="RAG-based assistant for Vidco 17020 usage manuals.",version="0.1.0")
app.include_router(chat_router)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health", response_model=HealthResponse)
def health():
    vector_db_status = "ok"
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        collection.count()
    except Exception as error:
        logger.warning("Chroma health check failed: %s",error)
        vector_db_status = "error"

    redis_status = "ok" if ping_redis() else "error"
    gemini_status = "ok" if check_gemini_reachable() else "error"

    all_ok = vector_db_status == "ok" and redis_status == "ok" and gemini_status == "ok"
    overall_status = "ok" if all_ok else "degraded"

    return {"status": overall_status,"vector_db": vector_db_status,"redis": redis_status,"gemini": gemini_status}