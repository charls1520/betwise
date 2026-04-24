import os
import glob
import json
import re
import time
import datetime
import zoneinfo
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from src.ml.inference import predict_matches
from src.ml.reliability import calculate_value_edge, meets_data_threshold
from src.ingestion.normalizer import TeamNormalizer
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index, query_index
from llama_index.core import Document
from src.ingestion.scheduler import start_scheduler
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger()

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
            date_str = fpath.split(os.sep)[-2] if os.sep in fpath else fpath.split('/')[-2]
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for article in data.get("articles", []):
                        text = f"Noticia [Publicada el {date_str}]: {article.get('title')}\nResumen: {article.get('summary')}"
                        docs.append(Document(text=text, metadata={"source": "bbc_news"}))
                except Exception:
                    pass
        
        # Look for odds json files
        odds_files = glob.glob(f"{raw_dir}/**/odds_*.json", recursive=True)
        for fpath in odds_files:
            date_str = fpath.split(os.sep)[-2] if os.sep in fpath else fpath.split('/')[-2]
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for match in data.get("matches", []):
                        commence = match.get('commence_time', 'Unknown')
                        text = f"Partido [Generado el {date_str}]: {match.get('home_team')} vs {match.get('away_team')} a jugarse el {commence}."
                        docs.append(Document(text=text, metadata={"source": "odds"}))
                except Exception:
                    pass

    if not docs:
        docs.append(Document(text="System online. Waiting for first data scrape."))
    return docs


try:
    logger.info("Building RAG index from real data...")
    global_index = build_index(load_real_documents())
    logger.info("RAG index built successfully.")
except Exception as e:
    logger.error(f"Failed to build RAG index: {e}")
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

        xg_stats = {}
        xg_files = glob.glob(f"{raw_dir}/**/xg_*.json", recursive=True)
        if xg_files:
            latest_xg = sorted(xg_files, key=os.path.getmtime)[-1]
            with open(latest_xg, "r", encoding="utf-8") as f:
                xg_stats = json.load(f)

        elo_stats = {}
        elo_files = glob.glob(f"{raw_dir}/**/elo_*.json", recursive=True)
        if elo_files:
            latest_elo = sorted(elo_files, key=os.path.getmtime)[-1]
            with open(latest_elo, "r", encoding="utf-8") as f:
                elo_stats = json.load(f).get("stats", {})

        canonical_teams = list(xg_stats.keys()) if xg_stats else []
        normalizer = TeamNormalizer(canonical_teams)

        valid_odds = []
        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))

            if home_norm and home_norm in xg_stats and away_norm and away_norm in xg_stats:
                match["home_xg"] = xg_stats[home_norm].get("xg_for_avg")
                match["away_xg"] = xg_stats[away_norm].get("xg_for_avg")
                match["home_elo"] = elo_stats.get(home_norm, elo_stats.get(match.get("home_team"), 1500.0))
                match["away_elo"] = elo_stats.get(away_norm, elo_stats.get(match.get("away_team"), 1500.0))
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
        logger.error(f"Error in ML suggestions: {e}")
        return []


@app.post("/api/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    if not global_index:
        return ChatResponse(response="RAG Index no inicializado.", sources=[])

    try:
        import src.rag.pipeline as pipeline
        
        # 1. Date Context
        tz = zoneinfo.ZoneInfo("America/Bogota")
        now_utc5 = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S UTC-5")
        
        # 2. Load latest dashboard data
        dashboard_data = get_dashboard_data()
        matches = dashboard_data.get("matches", [])
        suggestions = dashboard_data.get("suggestions", [])
        
        upcoming_matches_text = "Partidos de las próximas 48 horas:\n"
        if matches and not (len(matches) > 0 and matches[0].get("error")):
            for m in matches:
                upcoming_matches_text += f"- {m.get('league', 'Desconocida')} | {m.get('home_team')} vs {m.get('away_team')} (Hora: {m.get('match_time')}) | Cuota Local: {m.get('home_odds')} | Prob. ML Local: {m.get('prob_home_win', 0)*100:.1f}%\n"
        else:
            upcoming_matches_text += "No hay partidos programados en las próximas 48 horas o hubo un error.\n"
            
        ml_text = "Apuestas de Valor Sugeridas (Edge > 10%):\n"
        if suggestions:
            for s in suggestions:
                ml_text += f"- {s['match']} | Confianza {s['confidence']} | Cuota {s['odds']} | Edge: {s['edge']}\n"
        else:
            ml_text += "Ninguna apuesta matemática supera el umbral de valor del 10% hoy.\n"
        
        # 3. Build Super Prompt
        prompt = f"""Actúas como un experto asesor de apuestas deportivas (Fútbol Europeo).
Hoy es la siguiente fecha y hora: {now_utc5}

Tienes acceso COMPLETO a tu memoria (base de datos RAG) para ver el historial y contexto de noticias, pero TAMBIÉN tienes la siguiente información en tiempo real de los partidos que SÍ se jugarán en las próximas 48 horas, proveniente de nuestro modelo predictivo:

{upcoming_matches_text}

{ml_text}

Pregunta del usuario: {request.message}

INSTRUCCIONES CRÍTICAS:
1. Responde a la pregunta del usuario considerando la FECHA DE HOY.
2. Si el usuario pide sugerencias de apuestas para los "próximos partidos" o "hoy/mañana", recomiéndale basado ÚNICAMENTE en la lista de "Partidos de las próximas 48 horas" y las "Apuestas de Valor Sugeridas".
3. Si el usuario menciona un partido que NO está en la lista de próximas 48 horas (por ejemplo "Barcelona vs Celta Vigo" y no está arriba), infórmale amablemente que ese partido no se juega en las próximas 48 horas o que es un partido del pasado (puedes buscar su resultado/noticias en tu memoria RAG si te pregunta contexto, pero NO inventes cuotas).
4. Explica siempre el "Value Edge" (margen de valor matemático). No inventes cuotas o partidos falsos.
"""
        answer = pipeline.query_index(global_index, prompt)
        
        return ChatResponse(
            response=str(answer),
            sources=[
                SourceModel(type="news", title="RAG & Dashboard Context", snippet="Queried local DB and ML Engine")
            ],
        )
    except Exception as e:
        return ChatResponse(response=f"Error querying RAG: {e}", sources=[])


@app.get("/api/dashboard")
def get_dashboard_data():
    try:
        raw_dir = "data/raw"
        if not os.path.exists(raw_dir):
            return {"matches": [], "suggestions": []}
            
        odds_files = glob.glob(f"{raw_dir}/**/odds_*.json", recursive=True)
        if not odds_files:
            return {"matches": [], "suggestions": []}
            
        latest_file = sorted(odds_files, key=os.path.getmtime)[-1]
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_odds = data.get("matches", [])

        if not raw_odds:
            return {"matches": [], "suggestions": []}

        xg_stats = {}
        xg_files = glob.glob(f"{raw_dir}/**/xg_*.json", recursive=True)
        if xg_files:
            latest_xg = sorted(xg_files, key=os.path.getmtime)[-1]
            with open(latest_xg, "r", encoding="utf-8") as f:
                xg_stats = json.load(f)
                
        elo_stats = {}
        elo_files = glob.glob(f"{raw_dir}/**/elo_*.json", recursive=True)
        if elo_files:
            latest_elo = sorted(elo_files, key=os.path.getmtime)[-1]
            with open(latest_elo, "r", encoding="utf-8") as f:
                elo_stats = json.load(f).get("stats", {})

        canonical_teams = list(xg_stats.keys()) if xg_stats else []
        normalizer = TeamNormalizer(canonical_teams)

        valid_odds = []
        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))

            # Instead of failing on exception, just skip matches we can't find data for
            if home_norm and home_norm in xg_stats and away_norm and away_norm in xg_stats:
                match["home_xg"] = xg_stats[home_norm].get("xg_for_avg")
                match["away_xg"] = xg_stats[away_norm].get("xg_for_avg")
                
                # Add Elo ratings if available, default to average 1500 if missing
                match["home_elo"] = elo_stats.get(home_norm, elo_stats.get(match.get("home_team"), 1500.0))
                match["away_elo"] = elo_stats.get(away_norm, elo_stats.get(match.get("away_team"), 1500.0))
                
                valid_odds.append(match)

        # 4. Run ML Inference
        predictions = predict_matches(valid_odds, model_dir="models") if valid_odds else []

        # 5. Merge results
        dashboard_data = []
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

            match_obj = {
                "id": idx,
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "prob_home_win": home_prob,
                "prob_draw": pred.get("prob_draw", 0.0),
                "prob_away_win": pred.get("prob_away_win", 0.0),
                "home_odds": home_odds,
                "home_edge": edge,
                "match_time": match.get("commence_time", "TBA"),
                "league": match.get("sport_title", "PREMIER LEAGUE"),
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
        logger.error(f"Dashboard Error: {e}")
        return [{"error": str(e)}]


from src.utils.audit_logger import get_unmatched_teams

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

    # 4. Audit Anomalies
    audit_status = {
        "unmatched_teams": get_unmatched_teams()
    }

    return {
        "rag_engine": rag_status,
        "ml_engine": ml_status,
        "ingestion_engine": ingestion_status,
        "data_audit": audit_status,
    }


@app.get("/")
def read_root():
    return {"status": "ok", "message": "BetWise API is running"}

