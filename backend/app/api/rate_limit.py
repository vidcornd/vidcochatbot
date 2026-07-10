from app.memory.redis_store import get_redis_client

def check_rate_limit(key: str,limit: int,window_seconds: int,) -> bool:
    client = get_redis_client()

    current_count = client.incr(key)

    if current_count == 1:
        client.expire(key, window_seconds)

    if current_count > limit:
        return False

    return True

def build_ip_rate_limit_key(ip_address: str) -> str:
    return f"rate_limit:ip:{ip_address}"

def build_conversation_rate_limit_key(conversation_id: str) -> str:
    return f"rate_limit:conversation:{conversation_id}"