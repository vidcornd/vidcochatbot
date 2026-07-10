import redis
import json
from typing import Literal
from app.config import settings

MessageRole = Literal["user", "assistant"]

CONVERSATION_TTL_SECONDS = 60 * 60 * 24
MAX_MESSAGES = 10

def get_redis_client():
    return redis.Redis.from_url(settings.redis_url,decode_responses=True)

def get_summary_key(conversation_id: str) -> str:
    return f"conversation:{conversation_id}:summary"

def get_messages_key(conversation_id: str) -> str:
    return f"conversation:{conversation_id}:messages"

def get_conversation(conversation_id: str) -> dict:
    client = get_redis_client()
    summary_key = get_summary_key(conversation_id)
    messages_key = get_messages_key(conversation_id)

    summary = client.get(summary_key) or ""

    raw_messages = client.lrange(messages_key, 0, -1)
    messages = []

    for raw_message in raw_messages:
        try:
            messages.append(json.loads(raw_message))
        except json.JSONDecodeError:
            continue

    return {"summary": summary,"messages": messages}

def save_message(conversation_id: str,role: MessageRole,content: str) -> None:
    client = get_redis_client()
    summary_key = get_summary_key(conversation_id)
    messages_key = get_messages_key(conversation_id)

    message = {"role": role,"content": content}

    client.rpush(messages_key, json.dumps(message, ensure_ascii=False))

    if client.llen(messages_key) > MAX_MESSAGES:
        client.lpop(messages_key)

    client.expire(messages_key, CONVERSATION_TTL_SECONDS)
    client.expire(summary_key, CONVERSATION_TTL_SECONDS)


def save_summary(conversation_id: str, summary: str) -> None:
    client = get_redis_client()
    summary_key = get_summary_key(conversation_id)
    client.set(summary_key, summary)
    client.expire(summary_key, CONVERSATION_TTL_SECONDS)


def clear_conversation(conversation_id: str) -> None:
    client = get_redis_client()
    client.delete(get_summary_key(conversation_id),get_messages_key(conversation_id))

def ping_redis() -> bool:
    try:
        client = get_redis_client()
        return bool(client.ping())
    except Exception:
        return False