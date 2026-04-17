from typing import TypedDict, Annotated, List, Dict, Any
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    file_path: str
    file_type: str
    extracted_text: str
    summary: str
    mcqs: List[Dict[str, Any]]
    analytics_data: Dict[str, Any]
    next_step: str
