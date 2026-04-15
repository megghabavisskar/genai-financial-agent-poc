from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config
from app.api.v1.api import api_router
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title=config.settings.PROJECT_NAME)

# CORS validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for PoC
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=config.settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Financial Data Analysis API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
