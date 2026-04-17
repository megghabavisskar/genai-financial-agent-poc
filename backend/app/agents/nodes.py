from app.agents.state import AgentState
from app.services.llm import LLMService
from langchain_core.messages import SystemMessage, HumanMessage
import json


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

    async def mcq_node(self, state: AgentState):
        text = state.get("extracted_text", "")
        if not text:
            return {"mcqs": []}
            
        prompt = """Generate 5 multiple choice questions based on the text. 
        Return the output as a JSON list of objects.
        Each object must have these keys:
        - "question": string
        - "options": list of strings (4 options)
        - "correct_answer": string (must be one of the options)
        
        Example:
        [
            {
                "question": "What is the revenue?",
                "options": ["$1M", "$2M", "$3M", "$4M"],
                "correct_answer": "$1M"
            }
        ]

        Text:
        """ + text[:10000]
        
        response = await self.llm_service.generate_response(prompt)
        
        # Cleanup markdown
        content = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            mcqs = json.loads(content)
            if not isinstance(mcqs, list):
                # If wrapped in an object like {"mcqs": [...]}, extract the list
                if isinstance(mcqs, dict):
                    mcqs = mcqs.get("mcqs", [])
        except json.JSONDecodeError:
            mcqs = [{"question": "Error parsing MCQs", "options": [], "correct_answer": "", "raw": response.content}]
            
        return {"mcqs": mcqs}

    async def analytics_node(self, state: AgentState):
        text = state.get("extracted_text", "")
        
        prompt = """Analyze the financial data in the text and identify key metrics that can be visualized.
        Generate a JSON object with a "charts" key containing a list of charts.
        Each chart object should have:
        - "type": "bar", "line", or "pie"
        - "title": string
        - "data": list of objects with "name" (string) and "value" (number) keys
        - "insights": string (brief explanation of the chart)
        
        Example:
        {
          "charts": [
            {
              "type": "bar",
              "title": "Revenue vs Expenses",
              "data": [{"name": "Revenue", "value": 1000}, {"name": "Expenses", "value": 800}],
              "insights": "Revenue exceeded expenses by 20%."
            }
          ]
        }
        
        If no suitable data for charts is found, return {"charts": [], "text_analysis": "Analysis..."}
        
        Text:
        """ + text[:10000]
        
        response = await self.llm_service.generate_response(prompt)
        
        # Simple cleanup to handle potential markdown code blocks in response
        content = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            analytics_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if valid JSON isn't returned
            analytics_data = {"charts": [], "text_analysis": response.content}
            
        return {"analytics_data": analytics_data}
