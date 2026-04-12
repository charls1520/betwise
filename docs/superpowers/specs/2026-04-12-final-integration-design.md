# Final Integration Design

## 1. Overview
This specification details the **Final Integration** of all BetWise components (Scraping, Normalization, ML Inference, RAG, and Frontend) into a cohesive V1 product. 
The objective is to expose a single unified API endpoint for the frontend dashboard and seamlessly connect the RAG engine to the chat interface.

## 2. API Architecture

### 2.1 Unified Dashboard Endpoint (`/api/dashboard`)
*   **Approach:** "All-in-One" Endpoint.
*   **Behavior:** When requested by the React frontend, this endpoint will orchestrate the data flow dynamically:
    1.  **Data Retrieval:** Check for today's scraped odds. If missing, it can optionally trigger the Odds API client.
    2.  **ML Inference:** Pass the scraped matches through the trained ML models (1X2 and Over/Under) via the `inference` module.
    3.  **Payload Generation:** Combine the real bookmaker odds with the ML-calculated probabilities and return a comprehensive JSON list.
*   **Pros for V1:** Drastically simplifies the frontend state management (React only needs one `useEffect` call).
*   **Fallback:** If the ML models are not yet fully trained on historical data, the endpoint will safely return the scraped odds with `null` or default probabilities to prevent crashing the UI.

### 2.2 Live Chat Endpoint (`/api/chat`)
*   **Behavior:** Replace the current "mock" response with a real call to the LlamaIndex RAG pipeline.
*   **Integration:** 
    1. The endpoint receives the user's query and the `match_id`.
    2. It invokes `query_index()` (from the RAG module).
    3. It formats the LLM's text response and extracts the source nodes (metadata) to build the `Rich Source Cards` expected by the frontend.

## 3. Frontend Updates
*   **Dashboard Panel:** Update the static "Arsenal vs Chelsea" hardcoded UI to map over the array returned by `/api/dashboard`, rendering a card for each upcoming match.
*   **State Management:** The chat interface will automatically inject the context of the currently selected match into the prompt sent to `/api/chat`.

## 4. Bootstrapping (The "Cold Start" Problem)
To ensure the application runs smoothly right out of the box:
*   A bootstrap script (`scripts/setup_dev.py`) should be created to:
    1. Run the initial scraping (News + Odds).
    2. Build the initial ChromaDB index.
    3. Train a dummy baseline ML model so the inference pipeline doesn't fail on first boot.