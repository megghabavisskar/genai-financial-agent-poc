from app.agents.state import AgentState
from app.services.llm import LLMService
 

class AgentNodes:
    def __init__(self):
        self.llm_service = LLMService()

    async def summary_node(self, state: AgentState):
        text = state.get("extracted_text", "")
        if not text:
            return {"summary": "No text to summarize."}
        
        prompt = f"Summarize the following financial document text. Focus on key financial metrics, trends, and risks.\n\nText:\n{text[:10000]}"
        response = await self.llm_service.generate_response(prompt)
        return {"summary": response.content}
