from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1,max_length = 2000)
    user_roles: list[str] = Field(default_factory=list)
    current_page: str | None = None

class Source(BaseModel):
    title: str | None = None
    source: str | None = None
    page: int | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: str
    conversation_id: str

class HealthResponse(BaseModel):
    status: str
    vector_db: str
    redis: str
    gemini: str
    chat_provider: str
    database: str