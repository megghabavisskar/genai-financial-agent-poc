from fastapi.testclient import TestClient

from app.main import app
from app.services.llm import LLMConfigurationError


client = TestClient(app)


class FakeRAGService:
    async def query(self, question: str) -> str:
        return "Mocked answer"


class BadConfigRAGService:
    async def query(self, question: str) -> str:
        raise LLMConfigurationError("Missing OPENAI_API_KEY in environment.")


def test_qa_returns_answer(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.endpoints.qa.RAGService", FakeRAGService)

    response = client.post("/api/v1/qa", json={"question": "What is revenue?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == "What is revenue?"
    assert payload["answer"] == "Mocked answer"


def test_qa_returns_400_for_invalid_llm_config(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.endpoints.qa.RAGService", BadConfigRAGService)

    response = client.post("/api/v1/qa", json={"question": "What is revenue?"})

    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]
