from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.db.models import DocumentMetadata
from app.db.weaviate import get_weaviate_client
from app.core.embeddings import embedding_service
from app.core.chunking import chunk_text
from app.core.logging import logger
from app.schemas.ingest import IngestResponse, TextIngestRequest
import pypdf
import io
import uuid

router = APIRouter()

async def process_document(title: str, text: str, tags: str, source: str, db: AsyncSession):
    # 1. Save metadata to Postgres
    doc_id = uuid.uuid4()
    doc_meta = DocumentMetadata(id=doc_id, title=title, source=source, tags=tags)
    db.add(doc_meta)
    await db.commit()
    await db.refresh(doc_meta)

    # 2. Chunk text
    chunks = chunk_text(text)
    
    # 3. Embed and store in Weaviate
    weaviate_client = get_weaviate_client()
    try:
        if chunks:
            # Batch embedding
            embeddings = embedding_service.embed_documents(chunks)
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                weaviate_client.insert_chunk(
                    chunk_text=chunk,
                    vector=vector,
                    document_id=str(doc_id),
                    chunk_index=i
                )
    finally:
        weaviate_client.close()

    return doc_id, len(chunks)

@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    tags: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    text = ""
    # Only simple PDF parsing for now
    if file.filename.endswith(".pdf"):
        content = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    else:
        # Assume text
        content = await file.read()
        text = content.decode("utf-8")

    doc_title = title or file.filename
    doc_id, chunk_count = await process_document(doc_title, text, tags, file.filename, db)
    
    return IngestResponse(document_id=doc_id, chunks_created=chunk_count, message="Document processed")

@router.post("/text", response_model=IngestResponse)
async def ingest_text(request: TextIngestRequest, db: AsyncSession = Depends(get_db)):
    doc_id, chunk_count = await process_document(request.title, request.text, request.tags, "manual_input", db)
    return IngestResponse(document_id=doc_id, chunks_created=chunk_count, message="Text processed")
