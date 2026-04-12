from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.ml.inference import predict_matches
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds
from src.ingestion.scrapers.understat import fetch_current_xg_stats
from src.ingestion.normalizer import TeamNormalizer
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index, query_index
from llama_index.core import Document

app = FastAPI(title="BetWise API")

# Initialize RAG globally (mocking a real index for now)
init_llama_index()
# Create an empty dummy index so it doesn't fail on boot
try:
    global_index = build_index([Document(text="Welcome to BetWise.")])
except Exception:
    global_index = None

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
    if not global_index:
        return ChatResponse(response="RAG Index not initialized.", sources=[])

    try:
        # Call real RAG pipeline
        import src.rag.pipeline as pipeline

        answer = pipeline.query_index(global_index, request.message)
        return ChatResponse(
            response=str(answer),
            sources=[
                SourceModel(
                    type="news", title="RAG Context", snippet="Queried local DB"
                )
            ],
        )
    except Exception as e:
        return ChatResponse(response=f"Error querying RAG: {e}", sources=[])


@app.get("/api/dashboard")
def get_dashboard_data():
    try:
        # 1. Fetch live odds (using demo key for safety)
        raw_odds = fetch_premier_league_odds(api_key="DEMO_KEY")

        # 2. Fetch real xG data
        xg_stats = fetch_current_xg_stats()

        # 3. Normalize and merge
        # Mocking a canonical list for V1 (ideally this comes from DB)
        canonical_teams = (
            list(xg_stats.keys())
            if xg_stats
            else [
                "Arsenal",
                "Chelsea",
                "Manchester City",
                "Manchester United",
                "Liverpool",
            ]
        )
        normalizer = TeamNormalizer(canonical_teams)

        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))

            # Apply real xG if found, else fallback to 1.0
            match["home_xg"] = (
                xg_stats.get(home_norm, {}).get("xg_for_avg", 1.0) if home_norm else 1.0
            )
            match["away_xg"] = (
                xg_stats.get(away_norm, {}).get("xg_for_avg", 1.0) if away_norm else 1.0
            )

        # 4. Run ML Inference
        predictions = predict_matches(raw_odds, model_dir="models")

        # 5. Merge results
        dashboard_data = []
        for idx, match in enumerate(raw_odds):
            pred = predictions[idx] if idx < len(predictions) else {}
            dashboard_data.append(
                {
                    "id": idx,
                    "home_team": match.get("home_team"),
                    "away_team": match.get("away_team"),
                    "prob_home_win": pred.get("prob_home_win", 0.33),
                    "prob_draw": pred.get("prob_draw", 0.33),
                    "prob_away_win": pred.get("prob_away_win", 0.34),
                }
            )
        return dashboard_data
    except Exception as e:
        return [{"error": str(e)}]


@app.get("/")
def read_root():
    return {"status": "ok", "message": "BetWise API is running"}
