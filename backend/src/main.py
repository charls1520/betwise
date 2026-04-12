from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="BetWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    match_id: int


class SourceModel(BaseModel):
    type: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    market: Optional[str] = None
    value: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[SourceModel] = []


@app.post("/api/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Mocked RAG response
    return ChatResponse(
        response=f"Received your query: '{request.message}'. The RAG pipeline is being integrated.",
        sources=[
            SourceModel(
                type="news", title="System", snippet="RAG backend integration pending."
            )
        ],
    )


@app.get("/")
def read_root():
    return {"status": "ok", "message": "BetWise API is running"}
