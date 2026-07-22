from pydantic import BaseModel, Field

class ConsentRequest(BaseModel):
    session_token: str | None = None
    name: str = Field(..., min_length=1, max_length=200)