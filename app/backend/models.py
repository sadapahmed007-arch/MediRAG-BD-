"""Pydantic models for API request/response."""
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class ProcessingStage(BaseModel):
    stage: str
    status: str
    detail: str = ""


class QuestionResponse(BaseModel):
    question: str
    language: str = ""
    topic: str = ""
    intent: str = ""
    safety_category: str = ""
    answer: str = ""
    matched_question: str = ""
    similarity_score: float = 0.0
    evidence: list = []
    sources: list = []
    abstained: bool = False
    related_questions: list = []
    processing_stages: list = []
    latency_ms: float = 0.0


class ClassifyResponse(BaseModel):
    question: str
    language: str
    topic: str
    intent: str
    safety_category: str


class RetrieveResponse(BaseModel):
    question: str
    results: list = []


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    dataset_size: int = 0
    index_size: int = 0


class DashboardResponse(BaseModel):
    dataset_stats: dict = {}
    classification_results: dict = {}
    retrieval_results: dict = {}
    multilingual_results: dict = {}
