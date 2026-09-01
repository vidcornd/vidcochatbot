import re
from pydantic_settings import BaseSettings, SettingsConfigDict

def _wildcard_pattern_to_regex(pattern: str) -> re.Pattern:
    domain = pattern[2:]
    escaped_domain = re.escape(domain)
    return re.compile(rf"^https?://([a-zA-Z0-9-]+\.)*{escaped_domain}$")

def origin_matches_allowed_patterns(origin: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if pattern.startswith("*."):
            if _wildcard_pattern_to_regex(pattern).match(origin):
                return True
        elif origin == pattern:
            return True
    return False

class Settings(BaseSettings):
    google_api_key: str
    vector_collection: str = "vidco_17020"
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash-lite"
    chat_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    widget_api_key: str = ""
    allowed_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173"
    )

    widget_bot_id: str = "bot_vidco_17020"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def allowed_origins_list(self) -> list[str]:
        origins = self.allowed_origins.split(",")
        cleaned_origins = []

        for origin in origins:
            cleaned_origin = origin.strip()
            if cleaned_origin:
                cleaned_origins.append(cleaned_origin)

        if "*" in cleaned_origins:
            raise ValueError(
                "ALLOWED_ORIGINS cannot contain '*': CORS is configured with "
                "allow_credentials=True, and browsers silently reject a wildcard "
                "origin when credentials are used. List explicit origins instead."
            )

        return cleaned_origins

    @property
    def exact_allowed_origins(self) -> list[str]:
        return [origin for origin in self.allowed_origins_list if not origin.startswith("*.")]

    @property
    def wildcard_allowed_origin_regex(self) -> str | None:
        wildcard_patterns = [origin for origin in self.allowed_origins_list if origin.startswith("*.")]
        if not wildcard_patterns:
            return None

        sub_patterns = [_wildcard_pattern_to_regex(pattern).pattern for pattern in wildcard_patterns]
        return "|".join(f"(?:{sub_pattern})" for sub_pattern in sub_patterns)

    def is_origin_allowed(self, origin: str) -> bool:
        return origin_matches_allowed_patterns(origin, self.allowed_origins_list)

settings = Settings()