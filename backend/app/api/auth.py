from fastapi import Header
from app.api.errors import api_error
from app.config import settings

def verify_widget_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.widget_api_key:
        return

    if x_api_key != settings.widget_api_key:
        raise api_error(status_code=401, error="unauthorized", message="Geçersiz veya eksik API anahtarı.")