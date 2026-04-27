# Intelligent Chat ML Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the Machine Learning inference logic directly into the Chat Endpoint, and use the auto-healing normalizer to clean up user queries for accurate prompt generation without making external API calls.

**Architecture:** Refactor `get_dashboard_data()` to extract a common ML evaluation function. The `/api/chat` endpoint will call this function using local cached raw files to get current value edges. It will also use `TeamNormalizer` to normalize any team names found in the user's message before injecting everything into the RAG prompt.

**Tech Stack:** Python, FastAPI, LlamaIndex.

---

### Task 1: Refactor ML Evaluation Logic

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: Extract `get_latest_ml_suggestions` function**

Modify `backend/src/main.py`. Extract the logic from `get_dashboard_data()` that reads odds and evaluates them, but make it read from local files instead of calling `fetch_premier_league_odds` directly.

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/main.py
git commit -m "refactor: extract ml suggestions logic for reuse in chat"
```

---

### Task 2: Implement Intelligent Chat Endpoint

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: Rewrite `/api/chat` with Normalizer and ML Context**

In `backend/src/main.py`, replace the `chat_with_bot` function:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/main.py
git commit -m "feat(chat): inject live ML value edge and normalized user prompt into RAG"
```

---

### Task 3: Update Chat Tests

**Files:**
- Modify: `backend/tests/test_main.py`

- [ ] **Step 1: Mock new dependencies in chat tests**

Update the test to not call the real normalizer or ML in `/api/chat` during unit testing if needed, or ensure the current test accommodates the new prompt text. If `test_chat_endpoint` exists, ensure it works.

- [ ] **Step 2: Commit**

```bash
git add backend/tests/test_main.py
git commit -m "test: update chat endpoint tests for ML integration"
```
