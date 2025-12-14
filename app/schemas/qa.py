from pydantic import BaseModel
from typing import List, Optional
from app.schemas.search import SearchResult

class QARequest(BaseModel):
    question: str
    k: int = 5

class QAResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
