import json
import secrets
from typing import Any
from app.memory.redis_store import get_redis_client

SESSION_TTL_SECONDS = 3600

def get_session_key(session_token: str) -> str:
    return f"widget_session:{session_token}"

def create_session(data: dict[str, Any]) -> str:
    client = get_redis_client()
    session_token = secrets.token_urlsafe(32)
    client.set(get_session_key(session_token),json.dumps(data, ensure_ascii=False),ex=SESSION_TTL_SECONDS)
    return session_token

def get_session(session_token: str) -> dict[str, Any] | None:
    client = get_redis_client()
    raw_session = client.get(get_session_key(session_token))

    if not raw_session:
        return None
    
    return json.loads(raw_session)