from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class SearchResult(BaseModel):
    document_id: UUID
    text: str
    score: float
    title: Optional[str] = None
    source: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
