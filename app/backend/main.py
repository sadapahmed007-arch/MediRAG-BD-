"""FastAPI backend for MediRAG-BD."""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.backend.models import (
    QuestionRequest, QuestionResponse, ClassifyResponse,
    RetrieveResponse, HealthResponse, DashboardResponse
)
from app.backend.pipeline import MediRAGPipeline

pipeline = MediRAGPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup."""
    print("Loading MediRAG-BD models...")
    pipeline.load_models()
    yield
    print("Shutting down MediRAG-BD...")


app = FastAPI(
    title="MediRAG-BD API",
    description="Multilingual Bangla-English-Banglish Medical QA and Semantic Retrieval System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Process a medical question through the full pipeline."""
    if not pipeline.models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded yet")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = pipeline.process_question(request.question)
    return QuestionResponse(**result)


@app.post("/api/classify", response_model=ClassifyResponse)
async def classify_question(request: QuestionRequest):
    """Classify a question (language, topic, intent, safety)."""
    if not pipeline.models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded yet")
    from src.language.detector import detect_language
    from src.preprocessing.text_processor import preprocess_question
    q = request.question
    lang = detect_language(q)
    processed = preprocess_question(q, lang)['processed_question']
    topic = pipeline.topic_clf.predict([processed])[0] if pipeline.topic_clf else ""
    intent = pipeline.intent_clf.predict([processed])[0] if pipeline.intent_clf else ""
    safety = pipeline.safety_clf.predict(q) if pipeline.safety_clf else ""
    return ClassifyResponse(question=q, language=lang, topic=topic, intent=intent, safety_category=safety)


@app.post("/api/retrieve", response_model=RetrieveResponse)
async def retrieve(request: QuestionRequest):
    """Retrieve top matching records."""
    if not pipeline.models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded yet")
    results = pipeline.hybrid_ret.search(request.question, top_k=10) if pipeline.hybrid_ret else []
    clean_results = []
    for r in results:
        clean_results.append({
            "question_id": str(r.get("question_id", "")),
            "question": str(r.get("question", ""))[:300],
            "answer": str(r.get("answer", ""))[:500],
            "topic": str(r.get("topic", "")),
            "similarity_score": round(r.get("similarity_score", 0), 4),
            "source": str(r.get("source", "")),
        })
    return RetrieveResponse(question=request.question, results=clean_results)


@app.get("/api/source/{question_id}")
async def get_source(question_id: str):
    """Get a source record by question_id."""
    record = pipeline.get_source(question_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    # Clean NaN values
    return {k: (str(v) if str(v) != 'nan' else '') for k, v in record.items()}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if pipeline.models_loaded else "loading",
        models_loaded=pipeline.models_loaded,
        dataset_size=len(pipeline.dataset) if pipeline.dataset is not None else 0,
        index_size=pipeline.dense_ret.index.ntotal if pipeline.dense_ret and pipeline.dense_ret.index else 0,
    )


@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Get research dashboard data."""
    data = pipeline.get_dashboard_data()
    return DashboardResponse(**data)


@app.get("/api/suggestions")
async def get_suggestions(q: str = ""):
    """Return autocomplete suggestions from the dataset questions."""
    if not q.strip() or pipeline.dataset is None:
        return {"suggestions": []}
    query_lower = q.lower().strip()
    matches = []
    seen = set()
    for question in pipeline.dataset["question"].dropna():
        q_str = str(question)
        if query_lower in q_str.lower() and q_str not in seen:
            # Truncate long questions for display
            display = q_str[:150] + ("..." if len(q_str) > 150 else "")
            matches.append(display)
            seen.add(q_str)
            if len(matches) >= 8:
                break
    return {"suggestions": matches}
