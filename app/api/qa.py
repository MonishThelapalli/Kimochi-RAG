from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.api.search import search
from app.schemas.qa import QARequest, QAResponse
from app.core.llm import llm_client
from app.core.prompts import QA_SYSTEM_PROMPT, QA_USER_PROMPT_TEMPLATE
from app.core.logging import logger

router = APIRouter()

@router.post("", response_model=QAResponse)
async def question_answering(request: QARequest, db: AsyncSession = Depends(get_db)):
    """
    RAG QA Endpoint.
    1. Search for relevant context.
    2. Build strict context for LLM.
    3. Generate answer asynchronously.
    """
    try:
        # 1. Retrieve context via search
        # We reuse the existing search logic which correctly queries Weaviate + Postgres
        search_resp = await search(q=request.question, k=request.k, db=db)
        
        # SAFEGUARD: If no context is found, return I don't know immediately
        if not search_resp.results:
            logger.info("qa_no_context", question=request.question)
            return QAResponse(answer="I don't know", sources=[])
        
        # 2. Build Context (Enriched Format)
        # We include ID, Title, and Score to give the LLM full visibility
        context_chunks = []
        for i, res in enumerate(search_resp.results, 1):
            # Using get() for safety, though schema guarantees fields
            # Fix: Use real title, fallback to Unknown
            doc_title = getattr(res, "title", "Unknown Document") 
            score = getattr(res, "score", 0.0)
            
            chunk_text = (
                f"[Source {i}]\n"
                f"Document: {doc_title}\n"
                f"Similarity: {score:.4f}\n"
                f"Content: {res.text}"
            )
            context_chunks.append(chunk_text)
        
        enriched_context = "\n\n".join(context_chunks)
        
        # 3. Prompt Construction
        user_prompt = QA_USER_PROMPT_TEMPLATE.format(
            context=enriched_context,
            question=request.question
        )
        
        # 4. LLM Generation
        # Await the async generator
        answer = await llm_client.generate(system_content=QA_SYSTEM_PROMPT, user_content=user_prompt)
        
        # 5. Logging & Return
        logger.info("qa_success", question_len=len(request.question), response_len=len(answer))
        
        return QAResponse(
            answer=answer.strip(),
            sources=search_resp.results
        )
        
    except Exception as e:
        logger.error("qa_endpoint_failed", error=str(e), question=request.question)
        # Graceful degradation - never crash the API for a runtime error
        return QAResponse(answer="I don't know", sources=[])
