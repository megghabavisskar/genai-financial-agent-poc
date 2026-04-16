# Financial Agent PoC

PoC for deriving financial insights from PDF/CSV documents using LLMs and a multi-agent workflow.

## What This Project Does

- Ingests financial documents (`.pdf`, `.csv`)
- Stores extracted content in a FAISS vector index for retrieval
- Runs a LangGraph workflow to produce:
  - Document summary
- Supports Q&A over ingested documents using RAG
- Provides a Streamlit UI for upload, analysis, and chat

## Architecture

- Backend API: FastAPI (`backend/app`)
- Agentic workflow: LangGraph (`backend/app/agents`)
- LLM provider: OpenAI via `langchain-openai`
- Vector store: FAISS with sentence-transformer embeddings
- Frontend: Streamlit (`streamlit_app.py`)

## Prerequisites

- Python 3.10+
- An OpenAI API key

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create env file:

```bash
cp .env.example .env
```

Edit `backend/.env` and set:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Run

Start FastAPI backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start Streamlit app:

```bash
cd backend
source venv/bin/activate
cd ..
streamlit run streamlit_app.py
```

## Endpoints

- Health: `GET /health`
- Ingest PDF: `POST /api/v1/ingest/pdf`
- Ingest CSV: `POST /api/v1/ingest/csv`
- Analyze text via agents: `POST /api/v1/analyze`
- Ask question (RAG): `POST /api/v1/qa`

## Development Dependencies

If you need test tooling:

```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt
```

## Notes

- This is a PoC configuration and uses permissive CORS (`*`).
- FAISS index is stored at `backend/data/faiss_index`.
- Keep `backend/.env` out of version control.
