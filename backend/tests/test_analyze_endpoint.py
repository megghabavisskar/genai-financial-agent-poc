from fastapi.testclient import TestClient

from app.main import app
from app.services.llm import LLMConfigurationError


client = TestClient(app)


class FakeGraph:
    async def ainvoke(self, inputs):
        return {
            "summary": "Short summary",
            "mcqs": [
                {
                    "question": "Sample question?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                }
            ],
            "analytics_data": {
                "charts": [
                    {
                        "type": "bar",
                        "title": "Revenue",
                        "data": [{"name": "Q1", "value": 100}],
                    }
                ]
            },
        }


class ErrorGraph:
    async def ainvoke(self, inputs):
        raise LLMConfigurationError("Missing GOOGLE_API_KEY in environment.")


def test_analyze_returns_structured_response(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.endpoints.agent.create_graph", lambda: FakeGraph())

    response = client.post("/api/v1/analyze", json={"text": "Revenue is 100"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "Short summary"
    assert len(payload["mcqs"]) == 1
    assert payload["analytics"]["charts"][0]["title"] == "Revenue"


def test_analyze_returns_400_for_invalid_llm_config(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.endpoints.agent.create_graph", lambda: ErrorGraph())

    response = client.post("/api/v1/analyze", json={"text": "Revenue is 100"})

    assert response.status_code == 400
    assert "GOOGLE_API_KEY" in response.json()["detail"]
