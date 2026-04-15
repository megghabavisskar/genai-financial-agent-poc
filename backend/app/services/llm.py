from langchain_google_genai import ChatGoogleGenerativeAI
import os
import logging
from app.core import config


logger = logging.getLogger(__name__)


class LLMConfigurationError(Exception):
    pass

class LLMService:
    def __init__(self):
        # Ensure GOOGLE_API_KEY is set in environment or pass it here
        api_key = os.getenv("GOOGLE_API_KEY")
        self._validate_api_key(api_key)
        logger.info("GOOGLE_API_KEY loaded successfully for LLM service.")
        
        self.llm = ChatGoogleGenerativeAI(
            model=config.settings.GEMINI_MODEL,
            google_api_key=api_key,
        )

    @staticmethod
    def _validate_api_key(api_key: str | None) -> None:
        if not api_key:
            raise LLMConfigurationError("Missing GOOGLE_API_KEY in environment.")

        placeholder_prefixes = ("your_", "sk-xxxx", "api_key_here")
        if api_key.lower().startswith(placeholder_prefixes):
            raise LLMConfigurationError("GOOGLE_API_KEY appears to be a placeholder; provide a real key.")

    async def generate_response(self, prompt: str):
        import asyncio
        from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
        
        max_retries = config.settings.LLM_MAX_RETRIES
        base_delay = config.settings.LLM_BASE_DELAY_SECONDS
        
        for attempt in range(max_retries):
            try:
                return await self.llm.ainvoke(prompt)
            except (ResourceExhausted, ServiceUnavailable) as e:
                if attempt == max_retries - 1:
                    raise e
                
                logger.warning(
                    "LLM quota/service issue. Retrying in %ss (attempt %s/%s)",
                    base_delay,
                    attempt + 1,
                    max_retries,
                )
                await asyncio.sleep(base_delay)
                base_delay *= 2  # Exponential backoff

        raise RuntimeError("LLM call failed after retries.")

