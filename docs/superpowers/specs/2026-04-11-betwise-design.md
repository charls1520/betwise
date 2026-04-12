# BetWise - ML & RAG Sports Betting Assistant Design

## 1. Overview and UX
BetWise is a hybrid web application focusing initially on the **Premier League**.
* **Dashboard:** Displays upcoming matches with pre-calculated, high-value predictions across multiple markets (goals, asian handicap, cards, corners).
* **Match Detail & RAG Chat:** Clicking a match opens a detailed view featuring an AI chat interface. Users can ask complex contextual questions (e.g., "How does the star striker's injury affect the corner line?") and get answers backed by up-to-date data and news.

## 2. Architecture (Python-First)
The system uses a unified Python backend to handle both web serving and heavy data/ML processing, paired with a modern frontend.
* **Backend & AI Engine:** FastAPI (Python). Manages API routes, data ingestion cron jobs, ML model inference, and the RAG pipeline.
* **Frontend:** React + TypeScript (Vite). A lightweight SPA for the dashboard and chat interface.
* **Database (Relational):** PostgreSQL or SQLite for structured data (matches, teams, canonical names, historical stats, odds).
* **Database (Vector):** ChromaDB (or similar) for storing embeddings of unstructured text (news, injury reports).

## 3. Core Components & Data Flow
The system operates on a **daily batch update** strategy to manage API limits and system load.

### 3.1 Data Ingestion (Daily Cron)
* Scrapes/fetches data from free APIs and reliable sports sites.
* **Structured Data:** Historical stats, league standings, current odds for various markets.
* **Unstructured Data:** Recent news, injury reports, manager press conferences.

### 3.2 Data Normalization Engine
* **Crucial Step:** Uses string similarity libraries (e.g., `thefuzz` / `FuzzyWuzzy`) to map various team name formats (e.g., "Man Utd", "Manchester United FC") from different sources into a single canonical ID in the relational database.

### 3.3 ML Prediction Engine (Structured)
* A lightweight statistical model (e.g., Logistic Regression, XGBoost, or Random Forest using `scikit-learn`).
* Takes structured data (recent form, H2H, stats) and outputs probabilities for predefined markets. These populate the main Dashboard.

### 3.4 RAG Engine (Unstructured)
* Uses **LlamaIndex** (or LightRAG).
* Unstructured text is chunked, embedded, and stored in the Vector DB.
* When a user asks a question in the chat, the RAG engine retrieves relevant recent news and stats to provide context-aware answers.

## 4. Error Handling and Constraints
* **Rate Limiting:** Scrapers will include delays and retries with exponential backoff to avoid IP bans.
* **Data Unavailability:** If recent news or odds are unavailable for a specific match, the UI will gracefully degrade, showing only historical ML predictions and notifying the user of missing context.
* **Scope:** Restricted to the English Premier League for v1 to ensure high accuracy in the normalization and prediction engines before scaling.