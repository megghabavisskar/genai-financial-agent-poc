import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Financial Data Analysis PoC"
    API_V1_STR: str = "/api/v1"
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_BASE_DELAY_SECONDS: int = int(os.getenv("LLM_BASE_DELAY_SECONDS", "2"))

settings = Settings()
