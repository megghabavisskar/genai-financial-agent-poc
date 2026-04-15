import pandas as pd
import pypdf
from fastapi import UploadFile, HTTPException
import io

class IngestionService:
    @staticmethod
    async def process_pdf(file: UploadFile) -> str:
        try:
            content = await file.read()
            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    @staticmethod
    async def process_csv(file: UploadFile) -> str:
         try:
            content = await file.read()
            # Determine encoding if necessary, defaulting to utf-8
            df = pd.read_csv(io.BytesIO(content))
            # Prefer markdown for LLM readability; fall back to CSV if tabulate is not installed.
            try:
                return df.to_markdown(index=False)
            except ImportError:
                return df.to_csv(index=False)
         except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

