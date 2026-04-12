# Reliability & Suggestion Engine Design

## 1. Overview
This specification details the **Reliability & Suggestion Engine** for BetWise.
To ensure high-quality betting suggestions and eliminate mock data, we are introducing strict rules before any match prediction is elevated to a "Suggested Bet" on the Dashboard. Additionally, the RAG engine will be formally initialized with the actual upcoming match data and scraped news.

## 2. The Three Pillars of Quality

### 2.1 Strict Data Completeness (Tolerance Zero)
*   **Rule:** A team must have at least 10 historical matches in the Understat dataset for the current or previous season.
*   **Action:** If a newly promoted team lacks sufficient xG data, the ML engine will refuse to calculate probabilities for that match, marking it as `insufficient_data`.

### 2.2 The "Value Edge" Filter
*   **Rule:** Mathematical value must exist. We convert the bookmaker's decimal odds into an implied probability (e.g., Odds of 2.00 = 50% probability).
*   **Action:** A bet is only considered a candidate if our ML model's calculated probability is at least **10% higher** than the bookmaker's implied probability. If the ML says 65% but the bookie implies 60%, it's discarded (only a 5% edge). If ML says 65% and bookie implies 50%, it passes the edge filter.

### 2.3 Cross-Validation (ML + RAG Consensus)
*   **Rule:** Even if the ML model finds a mathematical edge, the RAG engine (Gemma) acts as the final auditor.
*   **Action:** Before a suggestion is finalized, the system queries the local RAG engine: *"Are there any critical injuries or negative news for [Team] today?"*
*   If the RAG engine detects key player absences or managerial crises in the scraped news, the suggestion is vetoed or downgraded in confidence, preventing blind statistical bets.

## 4. RAG Initialization & Chat Integration
*   The `init_llama_index` process will be updated. Instead of a dummy "Welcome" document, the backend will actively load:
    1.  The structured JSON of the upcoming fixtures (so the bot knows who is playing).
    2.  The scraped RSS news files from the Data Lake.
*   This ensures that when a user asks "Who is playing today?" or "Any injuries?", the Gemma LLM has the exact context to answer truthfully.

## 5. Dashboard Suggestions (Frontend)
*   The 3 top cards ("AI Betting Suggestions") on the React Dashboard will be connected to a new property in the `/api/dashboard` response called `suggestions`.
*   Only matches that pass all three pillars of quality will be populated in this array.
*   If no matches pass the strict filters today, the UI will explicitly state: *"No high-value bets found today. Protect your bankroll."*