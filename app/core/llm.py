from groq import Groq
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

class LLMClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            self.client = None
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = "mixtral-8x7b-32768"

    def generate(self, prompt: str) -> str:
        if not self.client:
            return "I don't know"

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error("llm_error", error=str(e))
            return "I don't know"

llm_client = LLMClient()
