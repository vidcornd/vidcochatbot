from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    chroma_path: str = "./data/chroma"
    chroma_collection: str = "vidco_17020"
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash-lite"
    redis_url: str = "redis://localhost:6379/0"
    allowed_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def allowed_origins_list(self) -> list[str]:
        origins = self.allowed_origins.split(",")
        cleaned_origins = []

        for origin in origins:
            cleaned_origin = origin.strip()
            if cleaned_origin:
                cleaned_origins.append(cleaned_origin)

        return cleaned_origins


settings = Settings()