import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=True)
    source = Column(String, nullable=True) # e.g. filename
    tags = Column(String, nullable=True) # comma separated
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentMetadata(id={self.id}, title={self.title})>"
