# Frontend Chat Interface Design

## 1. Overview and Goal
This specification defines the design and architecture for the **Frontend Chat Interface** of BetWise.
The goal is to provide users with a Side-by-Side analytical dashboard where they can view match predictions (from the ML engine) alongside a contextual, rich-component chat powered by the LlamaIndex RAG engine.

## 2. Layout & UX Architecture
The application uses a **Side-by-Side** layout.
* **Left Panel (Match Context):** Displays the current selected Premier League match, the ML-calculated predictions, recent form, and current odds.
* **Right Panel (RAG Chat):** A persistent chat interface where the user converses with the Ollama LLM about the specific match.

### 2.1 Chat Interactions (Rich Components)
The chat will not be limited to text bubbles. When the RAG engine retrieves specific contexts (e.g., an injury report or a statistical anomaly), the backend will send structured metadata. The frontend will render these as **Rich Source Cards** embedded within or below the text response.
Example:
* **User:** "Is the main striker playing?"
* **Bot:** "Based on recent news, he is out with a knee injury."
* **Source Card (UI Element):** `[News Snippet: BBC Sport - 2 hrs ago - "Knee injury sidelines striker..."]`

## 3. Technology Stack & Styling
* **Framework:** React (Vite) with TypeScript (already scaffolded).
* **Styling Strategy:** **Tailwind CSS**. It provides utility classes for rapid, custom design without the bulk of a heavy component library, ensuring BetWise looks unique and modern.
* **State Management:** React Context API or Zustand (TBD during implementation) for managing the active match and chat history.
* **Communication:** Standard REST API calls (via `fetch` or `axios`) to the FastAPI backend endpoints (`/api/chat` and `/api/matches`). WebSocket integration is deferred for a future iteration unless streaming responses are prioritized.

## 4. API Interface Requirements
To support Rich Components, the backend RAG endpoint must return a structured JSON response instead of plain text.
Example payload:
```json
{
  "response": "Text answer from Ollama...",
  "sources": [
    {
      "type": "news",
      "title": "Injury Update",
      "url": "...",
      "snippet": "..."
    },
    {
      "type": "odds",
      "market": "Over 2.5 Goals",
      "value": "1.85"
    }
  ]
}
```