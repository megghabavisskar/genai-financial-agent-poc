from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class DummyVectorStore:
    def add_texts(self, texts, metadatas=None):
        return None


def test_csv_ingestion_returns_content(monkeypatch) -> None:
    monkeypatch.setattr("app.api.v1.endpoints.ingestion.VectorStoreService", DummyVectorStore)

    files = {"file": ("sample.csv", "col1,col2\n10,20\n", "text/csv")}
    response = client.post("/api/v1/ingest/csv", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "sample.csv"
    assert payload["content_length"] > 0
    assert "col1" in payload["full_content"]
