from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class IngestResponse(BaseModel):
    document_id: UUID
    chunks_created: int
    message: str

class TextIngestRequest(BaseModel):
    title: str
    text: str
    tags: Optional[str] = None
