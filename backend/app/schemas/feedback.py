from typing import Literal
from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    rating: Literal["up", "down"]
    question: str = Field(default="", max_length=2000)
    answer: str = Field(default="", max_length=4000)