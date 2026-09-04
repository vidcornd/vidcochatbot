import logging
import threading
import time
from app.memory.redis_store import get_redis_client
logger = logging.getLogger(__name__)

_fallback_counters: dict[str, tuple[int, float]] = {}
_fallback_lock = threading.Lock()

def check_rate_limit(key: str,limit: int,window_seconds: int,) -> bool:
    try:
        client = get_redis_client()
        current_count = client.incr(key)

        if current_count == 1:
            client.expire(key, window_seconds)

        if current_count > limit:
            return False
        return True
    except Exception:
        logger.warning("step=rate_limit status=redis_unavailable key=%s outcome=in_memory_fallback",key)
        return check_in_memory_rate_limit(key=key,limit=limit,window_seconds=window_seconds)

def check_in_memory_rate_limit(key: str,limit: int,window_seconds: int,) -> bool:
    now = time.monotonic()

    with _fallback_lock:
        expired_keys = []

        for counter_key, (_, counter_expires_at) in _fallback_counters.items():
            if counter_expires_at <= now:
                expired_keys.append(counter_key)

        for expired_key in expired_keys:
            del _fallback_counters[expired_key]

        current_count, expires_at = _fallback_counters.get(key, (0, now + window_seconds))
        current_count += 1
        _fallback_counters[key] = (current_count, expires_at)

    if current_count > limit:
        return False

    return True

def build_ip_rate_limit_key(ip_address: str) -> str:
    return f"rate_limit:ip:{ip_address}"

def build_conversation_rate_limit_key(conversation_id: str) -> str:
    return f"rate_limit:conversation:{conversation_id}"