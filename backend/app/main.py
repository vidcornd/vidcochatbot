import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.widget import router as widget_router
from app.rag.vectorstore import get_vectorstore, check_gemini_reachable
from app.memory.redis_store import ping_redis
from app.schemas.chat import HealthResponse
from app.rag.chat_models import check_chat_provider_reachable
from app.storage.postgres_store import init_db, ping_db
from app.config import settings
from app.logging_config import configure_logging
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Vidco 17020 RAG Assistant API",description="RAG-based assistant for Vidco 17020 usage manuals.",version="0.1.0")
app.include_router(chat_router)
app.include_router(widget_router)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

try:
    init_db()
except Exception as error:
    logger.warning("Postgres init failed: %s",error)

@app.get("/api/health", response_model=HealthResponse)
def health():
    vector_db_status = "ok"
    try:
        vectorstore = get_vectorstore()
        vectorstore.similarity_search("ping", k=1)
    except Exception as error:
        logger.warning("Vector DB health check failed: %s",error)
        vector_db_status = "error"

    redis_status = "ok" if ping_redis() else "error"
    gemini_status = "ok" if check_gemini_reachable() else "error"
    chat_provider_status = "ok" if check_chat_provider_reachable() else "error"
    database_status = "ok" if ping_db() else "error"

    all_ok = (vector_db_status == "ok" and redis_status == "ok" and gemini_status == "ok" and chat_provider_status == "ok" and database_status == "ok")
    overall_status = "ok" if all_ok else "degraded"

    return {"status": overall_status,"vector_db": vector_db_status,"redis": redis_status,"gemini": gemini_status,"chat_provider": chat_provider_status,"database": database_status}