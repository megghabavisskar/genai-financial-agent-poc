from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.agents.graph import create_graph
from typing import Optional
import logging
from app.services.llm import LLMConfigurationError

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    summary: Optional[str] = None


@router.post("/analyze", status_code=status.HTTP_200_OK, response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest) -> AnalyzeResponse:
    graph = create_graph()
    try:
        inputs = {"extracted_text": request.text}
        result = await graph.ainvoke(inputs)
        
        return AnalyzeResponse(
            summary=result.get("summary"),
        )
    except LLMConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Analyze workflow failed.")
        raise HTTPException(status_code=500, detail=f"Error in analysis workflow: {str(e)}")
