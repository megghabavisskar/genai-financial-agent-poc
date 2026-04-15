from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.rag import RAGService
import logging
from app.services.llm import LLMConfigurationError

router = APIRouter()
logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str


@router.post("/qa", status_code=status.HTTP_200_OK, response_model=QuestionResponse)
async def ask_question(request: QuestionRequest) -> QuestionResponse:
    try:
        rag_service = RAGService()
        # Note: In a real app, you'd want to dependency inject the service 
        # or use a global instance to reuse the vector store loaded in memory.
        answer = await rag_service.query(request.question)
        return QuestionResponse(question=request.question, answer=answer)
    except LLMConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("QA endpoint failed.")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
