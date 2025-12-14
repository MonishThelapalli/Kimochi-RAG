from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.postgres import get_db
from app.db.models import DocumentMetadata
from app.db.weaviate import get_weaviate_client
from app.core.embeddings import embedding_service
from app.schemas.search import SearchResponse, SearchResult
from app.core.logging import logger
import uuid

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search(q: str, k: int = 5, db: AsyncSession = Depends(get_db)):
    # 1. Embed query
    query_vector = embedding_service.embed_text(q)
    
    # 2. Search Weaviate
    weaviate_client = get_weaviate_client()
    try:
        results = weaviate_client.search(query_vector, limit=k)
    finally:
        weaviate_client.close()

    # 3. Merge metadata
    search_results = []
    
    # Pre-fetch doc metadata to avoid N+1 if possible, or just query one by one for simplicity (k is small)
    # Ideally, collect IDs and do IN query.
    doc_ids = set()
    for res in results:
        # Weaviate collections object returns properties as dict
        props = res.properties
        if 'document_id' in props:
            doc_ids.add(uuid.UUID(props['document_id']))

    # Bulk fetch metadata
    meta_map = {}
    if doc_ids:
        stmt = select(DocumentMetadata).where(DocumentMetadata.id.in_(doc_ids))
        result_proxy = await db.execute(stmt)
        metas = result_proxy.scalars().all()
        meta_map = {m.id: m for m in metas}

    for res in results:
        props = res.properties
        doc_id_str = props.get('document_id')
        doc_uuid = uuid.UUID(doc_id_str) if doc_id_str else None
        
        meta = meta_map.get(doc_uuid)
        
        # distance is returned in metadata, typical similarity = 1 - distance/2 or similar depends on metric
        # Weaviate typically returns distance. Let's just use 1/(1+distance) or similar proxy if needed, 
        # but for now we pass raw retrieval stats or just 1.0 if not provided.
        # Actually res.metadata.distance is available if requested.
        score = 0.0
        if res.metadata and res.metadata.distance is not None:
            score = 1.0 - res.metadata.distance # Approximate similarity

        search_results.append(SearchResult(
            document_id=doc_uuid,
            text=props.get('text', ''),
            score=score,
            title=meta.title if meta else "Unknown",
            source=meta.source if meta else "Unknown"
        ))

    return SearchResponse(results=search_results)
