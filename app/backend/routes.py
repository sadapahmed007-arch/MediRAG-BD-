from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from .models import QuestionRequest, QuestionResponse, ClassifyRequest, ClassifyResponse, RetrieveRequest, RetrieveResponse, HealthResponse
from .pipeline import pipeline

router = APIRouter(prefix="/api")

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest):
    try:
        return pipeline.process_question(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest):
    return ClassifyResponse(
        language="English",
        topic="General",
        intent="Information",
        safety_category="Safe",
        is_safe=True
    )

@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest):
    return RetrieveResponse(results=[])

@router.get("/source/{question_id}")
async def get_source(question_id: str):
    return {"id": question_id, "content": "Mock source content"}

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        models_loaded=pipeline.models_loaded,
        version="0.1.0"
    )

@router.get("/stats")
async def get_stats():
    return {"total_records": 10000, "languages": ["English", "Bangla"]}

@router.get("/dashboard")
async def get_dashboard():
    return {
        "stats": {"total": 10000, "english": 5000, "bangla": 5000},
        "performance": {"recall": 0.85, "mrr": 0.75}
    }
