from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.ingestion import IngestionService
from app.services.vector_store import VectorStoreService
from pydantic import BaseModel

router = APIRouter()


class IngestResponse(BaseModel):
    filename: str
    content_length: int
    content_preview: str
    full_content: str


@router.post("/ingest/pdf", status_code=status.HTTP_200_OK, response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    content = await IngestionService.process_pdf(file)
    
    # Add to Vector Store
    vector_store = VectorStoreService()
    vector_store.add_texts([content], metadatas=[{"source": file.filename}])

    return IngestResponse(
        filename=file.filename,
        content_length=len(content),
        content_preview=content[:500] if len(content) > 500 else content,
        full_content=content,
    )


@router.post("/ingest/csv", status_code=status.HTTP_200_OK, response_model=IngestResponse)
async def ingest_csv(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await IngestionService.process_csv(file)

    # Add to Vector Store
    vector_store = VectorStoreService()
    vector_store.add_texts([content], metadatas=[{"source": file.filename}])
    
    return IngestResponse(
        filename=file.filename,
        content_length=len(content),
        content_preview=content[:500] if len(content) > 500 else content,
        full_content=content,
    )
