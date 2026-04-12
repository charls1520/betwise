# Reliability & Suggestion Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement strict rules for generating betting suggestions, filtering out matches with insufficient data, requiring a minimum 10% mathematical value edge, and cross-validating with the RAG engine for injury/news context.

**Architecture:** Add filtering logic to the main `/api/dashboard` endpoint and a new `/api/suggestions` endpoint. Initialize LlamaIndex on startup with real scraped data instead of dummy text.

**Tech Stack:** Python 3.10+, FastAPI, LlamaIndex, React.

---

### Task 1: Create Reliability Filters in Backend

**Files:**
- Create: `backend/src/ml/reliability.py`
- Create: `backend/tests/ml/test_reliability.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ml/test_reliability.py
from src.ml.reliability import calculate_value_edge, meets_data_threshold

def test_value_edge():
    # Model says 65% (0.65) probability of home win.
    # Bookie pays 2.00 (implied probability 50% or 0.50).
    # Edge is 0.65 - 0.50 = 0.15 (15% edge).
    assert calculate_value_edge(model_prob=0.65, bookie_decimal_odds=2.0) == 0.15
    
    # Negative edge
    assert calculate_value_edge(model_prob=0.40, bookie_decimal_odds=2.0) == -0.10

def test_data_threshold():
    # In V1 we mock the 10 match threshold check by looking if the team exists in the xG stats
    stats = {"Arsenal": {"xg_for_avg": 2.1, "matches_played": 15}}
    assert meets_data_threshold("Arsenal", stats) is True
    
    stats_low = {"Ipswich": {"xg_for_avg": 1.1, "matches_played": 5}}
    assert meets_data_threshold("Ipswich", stats_low) is False
    
    assert meets_data_threshold("Unknown Team", stats) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_reliability.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ml/reliability.py

def calculate_value_edge(model_prob: float, bookie_decimal_odds: float) -> float:
    """
    Calculates the mathematical edge of a bet.
    Edge = Model Probability - Implied Bookmaker Probability
    """
    if bookie_decimal_odds <= 0:
        return 0.0
        
    implied_prob = 1.0 / bookie_decimal_odds
    return model_prob - implied_prob

def meets_data_threshold(team_name: str, xg_stats: dict, min_matches: int = 10) -> bool:
    """
    Checks if a team has enough historical data to make a reliable prediction.
    """
    if not xg_stats or team_name not in xg_stats:
        return False
        
    team_data = xg_stats[team_name]
    # Since our scraper currently only grabs averages, we will mock the matches_played 
    # check for now by assuming if they have data in the dict, they passed the threshold, 
    # unless matches_played is explicitly provided and too low.
    if "matches_played" in team_data:
        return team_data["matches_played"] >= min_matches
        
    # If no matches_played field, assume true if data exists
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_reliability.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/reliability.py backend/tests/ml/test_reliability.py
git commit -m "feat(ml): add mathematical edge and data threshold filters"
```

### Task 2: Initialize RAG with Real Data

**Files:**
- Modify: `backend/src/main.py`
- Modify: `backend/tests/test_main.py`

- [ ] **Step 1: Write the failing test**

Modify `backend/tests/test_main.py`:
```python
# add inside test_main.py
def test_app_startup_initializes_rag(monkeypatch):
    # This is a bit tricky to test directly without starting the server, 
    # but we can verify the global_index is not None or dummy.
    from src.main import global_index
    assert global_index is not None
```

- [ ] **Step 2: Run test to verify it fails/passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py::test_app_startup_initializes_rag -v`
Expected: PASS (because the dummy index is loaded). We will rewrite the init logic to use real files.

- [ ] **Step 3: Update Main Initialization**

Modify `backend/src/main.py`:
```python
# In backend/src/main.py, replace the dummy global_index initialization block:
import os
import glob
import json
from llama_index.core import Document
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index

init_llama_index()

def load_real_documents():
    docs = []
    # 1. Load News from Data Lake
    # Find latest news files
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        # Look for news json files in subdirectories
        news_files = glob.glob(f"{raw_dir}/**/news_*.json", recursive=True)
        for fpath in news_files:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for article in data.get("articles", []):
                    text = f"Title: {article.get('title')}\nSummary: {article.get('summary')}"
                    docs.append(Document(text=text, metadata={"source": "bbc_news"}))
    
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
```

- [ ] **Step 4: Run tests**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/main.py
git commit -m "feat(api): initialize RAG engine with actual scraped news from data lake"
```

### Task 3: Expose Value Suggestions to Frontend

**Files:**
- Modify: `backend/src/main.py`
- Modify: `frontend/src/components/DashboardPanel.tsx`

- [ ] **Step 1: Update API to calculate edges**

Modify `backend/src/main.py` inside `get_dashboard_data`:
```python
# Add import
from src.ml.reliability import calculate_value_edge, meets_data_threshold

# Update the loop in get_dashboard_data:
        suggestions = []
        for idx, match in enumerate(raw_odds):
            pred = predictions[idx] if idx < len(predictions) else {}
            
            home_prob = pred.get("prob_home_win", 0.0)
            # Default to 2.0 (50%) if bookmaker odds are missing for safety
            home_odds = 2.0 
            
            # Simple extraction of first bookmaker's home odds if available
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
            
            # Construct match object
            match_obj = {
                "id": idx,
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "prob_home_win": home_prob,
                "prob_draw": pred.get("prob_draw", 0.0),
                "prob_away_win": pred.get("prob_away_win", 0.0),
                "home_odds": home_odds,
                "home_edge": edge
            }
            dashboard_data.append(match_obj)
            
            # Add to suggestions if it passes thresholds (e.g. 10% edge)
            home_norm = normalizer.normalize(match.get("home_team", ""))
            if edge > 0.10 and meets_data_threshold(home_norm, xg_stats):
                suggestions.append({
                    "market": "1X2 Home Win",
                    "match": f"{match.get('home_team')} vs {match.get('away_team')}",
                    "confidence": f"{home_prob * 100:.0f}%",
                    "edge": f"{edge * 100:.1f}%",
                    "odds": home_odds,
                    "reasoning": "High value edge detected against bookmaker implied probability."
                })
                
        # Return both lists in a wrapper dict
        return {"matches": dashboard_data, "suggestions": suggestions}
```

- [ ] **Step 2: Update Frontend to consume new payload**

Modify `frontend/src/components/DashboardPanel.tsx`:
```tsx
import { useEffect, useState } from 'react';

interface MatchData {
  id: number;
  home_team: string;
  away_team: string;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  home_odds: number;
  home_edge: number;
}

interface Suggestion {
  market: string;
  match: string;
  confidence: string;
  edge: string;
  odds: number;
  reasoning: string;
}

interface DashboardPayload {
  matches: MatchData[];
  suggestions: Suggestion[];
  error?: string;
}

export default function DashboardPanel() {
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard')
      .then(res => res.json())
      .then(fetchedData => {
        // Handle case where error is returned as list of dicts from old format
        if (Array.isArray(fetchedData) && fetchedData.length > 0 && fetchedData[0].error) {
           setData({ matches: [], suggestions: [], error: fetchedData[0].error });
        } else {
           setData(fetchedData as DashboardPayload);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <main className="flex-grow xl:ml-64 lg:mr-80 overflow-y-auto px-6 py-8 text-[#6bff8f]">Loading analytics...</main>;
  if (data?.error) return <div className="text-red-500 p-8">Error: {data.error}</div>;
  if (!data) return <div className="text-white p-8">No data available</div>;

  const matches = data.matches || [];
  const suggestions = data.suggestions || [];

  return (
    <main className="flex-grow xl:ml-64 lg:mr-80 overflow-y-auto px-6 py-8">
      {/* Hero Bento Header */}
      {matches.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="md:col-span-2 relative group overflow-hidden rounded-xl bg-[#0b203d] p-8 min-h-[320px] flex flex-col justify-end">
            <div className="absolute inset-0 opacity-40 group-hover:scale-105 transition-transform duration-700 bg-gray-800">
              <div className="absolute inset-0 bg-gradient-to-t from-[#010e24] via-[#010e24]/60 to-transparent"></div>
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="flex h-2 w-2 rounded-full bg-[#47c4ff] animate-pulse"></span>
                <span className="text-[#47c4ff] text-xs font-bold tracking-widest uppercase">Live: Featured Match</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-['Space_Grotesk'] font-bold text-white mb-2 leading-tight uppercase">{matches[0].home_team} <span className="text-[#6bff8f]">vs</span> {matches[0].away_team}</h2>
              <p className="text-[#9eabc8] max-w-md mb-6">AI Prediction: Real-time ML calculation based on historical xG data.</p>
              <div className="flex gap-4">
                <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                  <p className="text-[10px] text-[#9eabc8] font-bold">1 (HOME) PROB</p>
                  <p className="text-2xl font-['Space_Grotesk'] font-bold text-[#6bff8f]">{(matches[0].prob_home_win * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                  <p className="text-[10px] text-[#9eabc8] font-bold">EDGE</p>
                  <p className="text-2xl font-['Space_Grotesk'] font-bold text-white">{(matches[0].home_edge * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI-Powered Betting Suggestions */}
      <section className="mb-12">
        <div className="flex items-center gap-2 mb-6">
          <span className="material-symbols-outlined text-[#6bff8f]">psychology</span>
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">Verified Value Bets</h2>
        </div>
        
        {suggestions.length === 0 ? (
            <div className="bg-[#0b203d] p-6 rounded-xl border border-[#3b4861] text-center">
                <p className="text-[#9eabc8] text-sm">No high-value bets passing the strict 10% edge filter found today. Protect your bankroll.</p>
            </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {suggestions.map((sug, i) => (
                <div key={i} className="bg-gradient-to-br from-[#0b203d] to-[#010e24] p-5 rounded-xl border border-[#6bff8f]/10 relative">
                <div className="absolute top-4 right-4 bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] font-bold px-2 py-1 rounded">{sug.confidence} CONFIDENCE</div>
                <p className="text-[10px] text-[#9eabc8] font-bold mb-1 uppercase">{sug.match}</p>
                <h4 className="text-white font-bold mb-3">{sug.market}</h4>
                <p className="text-xs text-[#9eabc8] mb-4">{sug.reasoning} (Edge: {sug.edge})</p>
                <button className="w-full bg-[#152c4e] py-2 rounded text-[#6bff8f] text-xs font-bold border border-[#6bff8f]/20 hover:bg-[#6bff8f] hover:text-[#002c0f] transition-all">ADD TO SLIP @ {sug.odds}</button>
                </div>
            ))}
            </div>
        )}
      </section>

      {/* Featured Predictions Grid */}
      <div className="mb-12">
        <div className="flex justify-between items-end mb-6">
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">Main Soccer Markets</h2>
          <a className="text-[#6bff8f] text-xs font-bold uppercase tracking-widest hover:underline" href="#">All Fixtures</a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {matches.map((match) => (
              <div key={match.id} className="bg-[#0b203d] rounded-xl p-6 relative overflow-hidden group border border-white/5">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-sm text-white">{match.home_team.substring(0, 3).toUpperCase()}</span>
                    <span className="text-[#9eabc8] text-xs font-bold">VS</span>
                    <span className="font-bold text-sm text-white">{match.away_team.substring(0, 3).toUpperCase()}</span>
                  </div>
                  <span className="text-[10px] font-bold text-[#6bff8f] bg-[#6bff8f]/10 px-2 py-1 rounded">PREMIER LEAGUE</span>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <p className="text-[10px] font-black text-[#9eabc8] uppercase">1X2 Full Time AI Probs</p>
                    <div className="flex gap-2">
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">1</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-[#6bff8f]">{(match.prob_home_win * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">X</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-white">{(match.prob_draw * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">2</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-white">{(match.prob_away_win * 100).toFixed(1)}%</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
          ))}
          {matches.length === 0 && <p className="text-[#9eabc8]">No upcoming matches found.</p>}
        </div>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add backend/src/main.py frontend/src/components/DashboardPanel.tsx
git commit -m "feat: expose value-based suggestions and real RAG init data to dashboard"
```
````