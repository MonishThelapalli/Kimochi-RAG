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
            # Initialize AsyncGroq client
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.model = "mixtral-8x7b-32768"

    async def generate(self, system_content: str, user_content: str) -> str:
        """
        Generates a response using the Groq API asynchronously.
        Takes structured system and user prompts.
        """
        if not self.client:
            logger.error("llm_client_not_initialized")
            return "I don't know"

        try:
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
            
            # Async call to Groq
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0, # Deterministic outcomes
                max_tokens=1024
            )
            return completion.choices[0].message.content

        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            return "I don't know"

# Singleton instance
llm_client = LLMClient()
