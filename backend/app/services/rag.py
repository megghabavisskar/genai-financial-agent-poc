from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()

    async def query(self, question: str) -> str:
        # Retrieve context
        self.vector_store.load_or_create_index()
        docs = self.vector_store.similarity_search(question)
        context = "\n".join([d.page_content for d in docs])

        # Truncate context to ~3000 chars to stay well within token limits
        if len(context) > 3000:
            context = context[:3000] + "..."

        # Generate Answer
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        response = await self.llm_service.generate_response(prompt)
        return response.content
