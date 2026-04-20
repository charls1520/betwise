from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.ml.inference import predict_matches
from src.ml.reliability import calculate_value_edge, meets_data_threshold
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds
from src.ingestion.scrapers.understat import fetch_current_xg_stats
from src.ingestion.normalizer import TeamNormalizer
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index, query_index
from llama_index.core import Document

import os
import glob
import json
from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from src.ingestion.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(title="BetWise API", lifespan=lifespan)

# Initialize RAG globally
init_llama_index()


def load_real_documents():
    docs = []
    # 1. Load News from Data Lake
    # Find latest news files
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        # Look for news json files
        news_files = glob.glob(f"{raw_dir}/**/news_*.json", recursive=True)
        for fpath in news_files:
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for article in data.get("articles", []):
                        text = f"News Title: {article.get('title')}\nSummary: {article.get('summary')}"
                        docs.append(Document(text=text, metadata={"source": "bbc_news"}))
                except Exception:
                    pass
        
        # Look for odds json files
        odds_files = glob.glob(f"{raw_dir}/**/odds_*.json", recursive=True)
        for fpath in odds_files:
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for match in data.get("matches", []):
                        text = f"Match: {match.get('home_team')} vs {match.get('away_team')}"
                        docs.append(Document(text=text, metadata={"source": "odds"}))
                except Exception:
                    pass

    if not docs:
        docs.append(Document(text="System online. Waiting for first data scrape."))
    return docs


try:
    print("Building RAG index from real data...")
    global_index = build_index(load_real_documents())
    print("RAG index built successfully.")
except Exception as e:
    print(f"Failed to build RAG index: {e}")
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


def get_latest_ml_suggestions() -> list:
    """Evaluates the latest cached odds using the ML model to find value edges."""
    try:
        raw_dir = "data/raw"
        if not os.path.exists(raw_dir):
            return []
            
        odds_files = glob.glob(f"{raw_dir}/**/odds_*.json", recursive=True)
        if not odds_files:
            return []
            
        latest_file = sorted(odds_files, key=os.path.getmtime)[-1]
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_odds = data.get("matches", [])
            
        if not raw_odds:
            return []

        xg_stats = fetch_current_xg_stats()
        canonical_teams = list(xg_stats.keys()) if xg_stats else []
        normalizer = TeamNormalizer(canonical_teams)

        valid_odds = []
        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))

            if home_norm and home_norm in xg_stats and away_norm and away_norm in xg_stats:
                match["home_xg"] = xg_stats[home_norm].get("xg_for_avg")
                match["away_xg"] = xg_stats[away_norm].get("xg_for_avg")
                valid_odds.append(match)

        if not valid_odds:
            return []

        predictions = predict_matches(valid_odds, model_dir="models")
        
        suggestions = []
        for idx, match in enumerate(valid_odds):
            pred = predictions[idx] if idx < len(predictions) else {}
            home_prob = pred.get("prob_home_win", 0.0)
            
            home_odds = 2.0
            bookmakers = match.get("bookmakers", [])
            if bookmakers and len(bookmakers) > 0:
                markets = bookmakers[0].get("markets", [])
                if markets and len(markets) > 0:
                    outcomes = markets[0].get("outcomes", [])
                    for outcome in outcomes:
                        if outcome.get("name") == match.get("home_team"):
                            home_odds = outcome.get("price", 2.0)
                            break

            edge = calculate_value_edge(home_prob, home_odds)
            suggestions.append({
                "match": f"{match.get('home_team')} vs {match.get('away_team')}",
                "prob_home": f"{home_prob * 100:.0f}%",
                "odds": home_odds,
                "edge": f"{edge * 100:.1f}%"
            })
            
        return suggestions
    except Exception as e:
        print(f"Error in ML suggestions: {e}")
        return []

import re

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    if not global_index:
        return ChatResponse(response="RAG Index not initialized.", sources=[])

    try:
        import src.rag.pipeline as pipeline
        
        # 1. Normalize User Input
        xg_stats = fetch_current_xg_stats()
        canonical_teams = list(xg_stats.keys()) if xg_stats else []
        normalizer = TeamNormalizer(canonical_teams)
        
        user_msg = request.message
        normalized_context = "Ningún alias detectado."
        
        # Simple heuristic: Look for capitalized words as potential teams
        potential_teams = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', user_msg)
        for pt in potential_teams:
            if len(pt) > 3:
                norm = normalizer.normalize(pt)
                if norm and norm != pt:
                    normalized_context = f"El usuario mencionó '{pt}', refiriéndose a '{norm}'."

        # 2. Get ML Suggestions
        suggestions = get_latest_ml_suggestions()
        ml_text = "Sin datos de predicción disponibles hoy."
        if suggestions:
            ml_text = "Predicciones Matemáticas (Value Edge):\n"
            for s in suggestions:
                ml_text += f"- {s['match']}: Prob. Local {s['prob_home']}, Cuota {s['odds']}, Edge: {s['edge']}\n"

        # 3. Build Super Prompt
        prompt = f"""Actúas como un experto asesor de apuestas de la Premier League.
Tienes la siguiente información matemática proveniente de nuestro modelo de Machine Learning:
{ml_text}

[Contexto Auto-Ajustado del usuario]: {normalized_context}

Pregunta del usuario: {request.message}

Usa el contexto matemático anterior y las noticias de tu base de datos para dar recomendaciones sólidas, explicando SIEMPRE el "Value Edge" o la probabilidad matemática. No inventes partidos ni cuotas.
"""
        answer = pipeline.query_index(global_index, prompt)
        
        return ChatResponse(
            response=str(answer),
            sources=[
                SourceModel(type="news", title="RAG Context", snippet="Queried local DB and ML Engine")
            ],
        )
    except Exception as e:
        return ChatResponse(response=f"Error querying RAG: {e}", sources=[])


from src.ml.reliability import calculate_value_edge, meets_data_threshold


@app.get("/api/dashboard")
def get_dashboard_data():
    try:
        # 1. Fetch live odds
        api_key = os.getenv("ODDS_API_KEY", "DEMO_KEY")
        raw_odds = fetch_premier_league_odds(api_key=api_key)

        # 2. Fetch real xG data
        xg_stats = fetch_current_xg_stats()

        # 3. Normalize and merge
        # Normalizer
        canonical_teams = list(xg_stats.keys()) if xg_stats else []
        normalizer = TeamNormalizer(canonical_teams)

        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))

            # Apply real xG if found, else raise Exception (No mock data allowed)
            if not home_norm or home_norm not in xg_stats:
                raise ValueError(f"Real xG data not found for home team: {match.get('home_team')}")
            if not away_norm or away_norm not in xg_stats:
                raise ValueError(f"Real xG data not found for away team: {match.get('away_team')}")

            match["home_xg"] = xg_stats[home_norm].get("xg_for_avg")
            match["away_xg"] = xg_stats[away_norm].get("xg_for_avg")

        # 4. Run ML Inference
        predictions = predict_matches(raw_odds, model_dir="models")

        # 5. Merge results
        dashboard_data = []
        suggestions = []
        for idx, match in enumerate(raw_odds):
            pred = predictions[idx] if idx < len(predictions) else {}

            home_prob = pred.get("prob_home_win", 0.0)
            home_odds = 2.0

            bookmakers = match.get("bookmakers", [])
            if bookmakers and len(bookmakers) > 0:
                markets = bookmakers[0].get("markets", [])
                if markets and len(markets) > 0:
                    outcomes = markets[0].get("outcomes", [])
                    for outcome in outcomes:
                        if outcome.get("name") == match.get("home_team"):
                            home_odds = outcome.get("price", 2.0)
                            break

            edge = calculate_value_edge(home_prob, home_odds)

            match_obj = {
                "id": idx,
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "prob_home_win": home_prob,
                "prob_draw": pred.get("prob_draw", 0.0),
                "prob_away_win": pred.get("prob_away_win", 0.0),
                "home_odds": home_odds,
                "home_edge": edge,
            }
            dashboard_data.append(match_obj)

            home_norm = normalizer.normalize(match.get("home_team", ""))
            if edge > 0.10 and meets_data_threshold(home_norm, xg_stats):
                suggestions.append(
                    {
                        "market": "1X2 Home Win",
                        "match": f"{match.get('home_team')} vs {match.get('away_team')}",
                        "confidence": f"{home_prob * 100:.0f}%",
                        "edge": f"{edge * 100:.1f}%",
                        "odds": home_odds,
                        "reasoning": "High value edge detected against bookmaker implied probability.",
                    }
                )

        return {"matches": dashboard_data, "suggestions": suggestions}
    except Exception as e:
        return [{"error": str(e)}]


import time


@app.get("/api/health/audit")
def get_audit_log():
    # 1. RAG Engine Status
    doc_count = 0
    try:
        if global_index and hasattr(global_index.vector_store, 'client'):
            doc_count = global_index.vector_store.client.get_collection("betwise_news").count()
    except Exception:
        pass

    rag_status = {
        "status": "Healthy" if global_index else "Offline",
        "total_documents": doc_count,
        "last_news_indexed": "Latest from Data Lake" if global_index else "None",
    }

    # 2. ML Engine Status
    model_path = "models/winner_model.joblib"
    ml_status = {
        "status": "Healthy" if os.path.exists(model_path) else "Offline",
        "model_last_trained": time.ctime(os.path.getmtime(model_path))
        if os.path.exists(model_path)
        else "Never",
        "sources_used": ["football-data.co.uk", "Understat xG", "Clubelo"],
    }

    # 3. Ingestion Engine Status
    ingestion_status = {
        "status": "Operational",
        "last_odds_fetch": "Live via API",
        "last_xg_fetch": "Live via Playwright",
        "normalization_warnings": [],  # Would be populated from a DB log in production
    }

    return {
        "rag_engine": rag_status,
        "ml_engine": ml_status,
        "ingestion_engine": ingestion_status,
    }


@app.get("/")
def read_root():
    return {"status": "ok", "message": "BetWise API is running"}
