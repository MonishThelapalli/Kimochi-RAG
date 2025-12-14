import os
from groq import AsyncGroq
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

class LLMClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("groq_api_key_missing", message="LLM features will fail if key not provided")
            self.client = None
        else:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.model = "mixtral-8x7b-32768" # Good default for RAG, or llama3-70b-8192

    async def generate(self, prompt: str) -> str:
        if not self.client:
            return "I don't know (Configuration Error)"
            
        try:
            logger.info("llm_generating", prompt_len=len(prompt))
            completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            return "I don't know"

# Singleton
llm_client = LLMClient()
