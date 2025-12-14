from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.api.search import search
from app.schemas.qa import QARequest, QAResponse
from app.core.llm import llm_client
from app.core.prompts import QA_PROMPT_TEMPLATE
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=QAResponse)
async def question_answering(request: QARequest, db: AsyncSession = Depends(get_db)):
    # 1. Retrieve context via search
    # Reuse the search logic
    search_resp = await search(q=request.question, k=request.k, db=db)
    
    # 2. Build Context
    context_text = "\n\n".join([r.text for r in search_resp.results])
    
    # 3. Prompt Construction
    prompt = QA_PROMPT_TEMPLATE.format(
        context=context_text,
        question=request.question
    )
    
    # 4. LLM Generation
    answer = await llm_client.generate(prompt)
    
    return QAResponse(
        answer=answer.strip(),
        sources=search_resp.results
    )
