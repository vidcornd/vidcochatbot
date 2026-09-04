from unittest.mock import MagicMock, patch

import app.api.rate_limit as rate_limit
from app.api.rate_limit import (build_conversation_rate_limit_key,build_ip_rate_limit_key,check_rate_limit)

REDIS_DOWN = ConnectionError("redis down")


def make_client(count: int) -> MagicMock:
    client = MagicMock()
    client.incr.return_value = count
    return client


def clear_fallback_counters() -> None:
    with rate_limit._fallback_lock:
        rate_limit._fallback_counters.clear()


def test_first_request_sets_expiry_and_is_allowed():
    client = make_client(1)

    with patch("app.api.rate_limit.get_redis_client", return_value=client):
        assert check_rate_limit(key="k", limit=5, window_seconds=60) is True

    client.expire.assert_called_once_with("k", 60)


def test_later_request_does_not_reset_expiry():
    client = make_client(3)

    with patch("app.api.rate_limit.get_redis_client", return_value=client):
        assert check_rate_limit(key="k", limit=5, window_seconds=60) is True

    assert client.expire.called is False


def test_request_at_limit_is_allowed():
    with patch("app.api.rate_limit.get_redis_client", return_value=make_client(5)):
        assert check_rate_limit(key="k", limit=5, window_seconds=60) is True


def test_request_over_limit_is_rejected():
    with patch("app.api.rate_limit.get_redis_client", return_value=make_client(6)):
        assert check_rate_limit(key="k", limit=5, window_seconds=60) is False


def test_unreachable_redis_still_enforces_the_limit():
    clear_fallback_counters()

    with patch("app.api.rate_limit.get_redis_client", side_effect=REDIS_DOWN):
        allowed = [check_rate_limit(key="down-1", limit=3, window_seconds=60) for _ in range(5)]

    assert allowed == [True, True, True, False, False]


def test_redis_failing_mid_command_still_enforces_the_limit():
    clear_fallback_counters()
    client = MagicMock()
    client.incr.side_effect = REDIS_DOWN

    with patch("app.api.rate_limit.get_redis_client", return_value=client):
        allowed = [check_rate_limit(key="down-2", limit=2, window_seconds=60) for _ in range(4)]

    assert allowed == [True, True, False, False]


def test_fallback_counts_each_key_separately():
    clear_fallback_counters()

    with patch("app.api.rate_limit.get_redis_client", side_effect=REDIS_DOWN):
        assert check_rate_limit(key="down-a", limit=1, window_seconds=60) is True
        assert check_rate_limit(key="down-a", limit=1, window_seconds=60) is False
        assert check_rate_limit(key="down-b", limit=1, window_seconds=60) is True


def test_fallback_window_expires():
    clear_fallback_counters()

    with patch("app.api.rate_limit.get_redis_client", side_effect=REDIS_DOWN):
        assert check_rate_limit(key="down-3", limit=1, window_seconds=60) is True
        assert check_rate_limit(key="down-3", limit=1, window_seconds=60) is False

        # Jump past the window: the counter should be dropped and start over.
        with patch("app.api.rate_limit.time.monotonic", return_value=rate_limit.time.monotonic() + 61):
            assert check_rate_limit(key="down-3", limit=1, window_seconds=60) is True


def test_working_redis_does_not_use_the_fallback():
    clear_fallback_counters()

    with patch("app.api.rate_limit.get_redis_client", return_value=make_client(1)):
        check_rate_limit(key="healthy", limit=5, window_seconds=60)

    assert rate_limit._fallback_counters == {}


def test_ip_and_conversation_keys_do_not_collide():
    assert build_ip_rate_limit_key("1.2.3.4") == "rate_limit:ip:1.2.3.4"
    assert build_conversation_rate_limit_key("1.2.3.4") == "rate_limit:conversation:1.2.3.4"
