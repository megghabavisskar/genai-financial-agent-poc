from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.agents.graph import create_graph
from typing import Dict, Any, List, Optional
import logging
from app.services.llm import LLMConfigurationError

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    text: str


class MCQItem(BaseModel):
    question: str
    options: List[str] = []
    correct_answer: str = ""


class ChartPoint(BaseModel):
    name: str
    value: float


class ChartItem(BaseModel):
    type: str
    title: str
    data: List[ChartPoint] = []
    insights: Optional[str] = None


class AnalyticsPayload(BaseModel):
    charts: List[ChartItem] = []
    text_analysis: Optional[str] = None
    insights: Optional[str] = None


class AnalyzeResponse(BaseModel):
    summary: Optional[str] = None
    mcqs: List[MCQItem] = []
    analytics: Dict[str, Any] | AnalyticsPayload | str | None = None


@router.post("/analyze", status_code=status.HTTP_200_OK, response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest) -> AnalyzeResponse:
    graph = create_graph()
    try:
        inputs = {"extracted_text": request.text}
        result = await graph.ainvoke(inputs)
        
        # Extract relevant parts from state
        return AnalyzeResponse(
            summary=result.get("summary"),
            mcqs=result.get("mcqs") or [],
            analytics=result.get("analytics_data"),
        )
    except LLMConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Analyze workflow failed.")
        raise HTTPException(status_code=500, detail=f"Error in analysis workflow: {str(e)}")
