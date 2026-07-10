from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.rag.vectorstore import get_vectorstore
from app.config import settings

app = FastAPI(title="Vidco 17020 RAG Assistant API",description="RAG-based assistant for Vidco 17020 usage manuals.",version="0.1.0")
app.include_router(chat_router)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health():
    vector_db_status = "ok"
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        collection.count()
    except Exception:
        vector_db_status = "error"

    if(vector_db_status != "ok"):
        return {"status": "degraded","vector_db": vector_db_status,"redis": "not_configured"}
    else:
        return {"status": "ok","vector_db": vector_db_status,"redis": "not_configured"}
