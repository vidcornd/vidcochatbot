from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: str
    chroma_path: str = "./data/chroma"
    chroma_collection: str = "vidco_17020"
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash"
    chat_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    redis_url: str = "redis://localhost:6379/0"
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

settings = Settings()