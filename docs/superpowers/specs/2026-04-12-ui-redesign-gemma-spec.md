# UI Redesign and Gemma LLM Integration Spec (v2)

## 1. Overview
This specification details the redesign of the BetWise Frontend Dashboard and the upgrade of the local RAG LLM engine.
The design heavily borrows from the "The Kinetic Vault" Stitch project, featuring a premium dark mode, neon accents, and a dense, data-rich Bento Box layout.

## 2. LLM Engine Upgrade (RAG)
* **Model Switch:** The LlamaIndex global configuration (`src/rag/config.py`) will be updated.
* **New Model:** `gemma4:26b`.
* **Provider:** Local Ollama instance.
* **Reasoning:** Taking advantage of a pre-installed, high-parameter model for vastly superior reasoning and contextual analysis of sports data compared to the baseline Llama3 8B.

## 3. Frontend Redesign (Stitch Inspiration)

### 3.1 Color Palette & Typography
* **Backgrounds:** Deep navy/black (`#010e24`, `#102645`).
* **Accents:** Neon Green (`#6bff8f`) for primary actions/values, Electric Blue (`#47c4ff`) for AI/RAG indicators.
* **Typography:** `Space Grotesk` (Headings/Numbers) and `Manrope` (Body/Data).

### 3.2 Layout Structure
* **Top Navigation:** Fixed header with branding and search.
* **Left Sidebar (Optional for Desktop):** League navigation and quick filters.
* **Main Feed (Center):**
    * **Hero Component:** Highlights the biggest upcoming match with a stadium background and the primary AI prediction.
    * **AI Suggestions Row:** Horizontal cards showing high-confidence bets (e.g., "94% CONFIDENCE: Over 9.5 Corners").
    * **Main Markets Grid:** Detailed cards for upcoming matches showing odds buttons for 1X2, Goals, and Cards.
* **Right Sidebar (RAG Chat):** Fixed "SOCCER AI ANALYST" panel.

### 3.3 Rich Chat Components
* The chat will feature a technical aesthetic.
* When the RAG engine returns statistical forecasts, they will be rendered as distinct "terminal-style" sub-cards within the chat bubble, using the primary neon colors.

## 4. Implementation Strategy
We will extract the HTML structure and Tailwind classes from the downloaded Stitch design (`stitch_design.html`) and convert them into modular React components (`Hero.tsx`, `MatchCard.tsx`, `SuggestionCard.tsx`, etc.) within our Vite setup, hooking them up to our existing `/api/dashboard` and `/api/chat` endpoints.