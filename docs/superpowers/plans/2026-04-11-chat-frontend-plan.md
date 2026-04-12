# Frontend Chat Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Side-by-Side analytical dashboard with a rich-component chat interface using Tailwind CSS, connected to the FastAPI backend.

**Architecture:** The React app is split into a main Dashboard (left) and a Chat Panel (right). The chat renders regular text bubbles and custom "Rich Source Cards" for metadata (odds, news).

**Tech Stack:** React, Vite, TypeScript, Tailwind CSS.

---

### Task 1: Install and Configure Tailwind CSS

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Install Tailwind CSS dependencies**

Run: `cd frontend && npm install -D tailwindcss@3.4 postcss autoprefixer`

- [ ] **Step 2: Initialize Tailwind config**

Run: `cd frontend && npx tailwindcss init -p`

- [ ] **Step 3: Configure Tailwind template paths**

Modify `frontend/tailwind.config.js` to replace its contents with:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 4: Add Tailwind directives to CSS**

Modify `frontend/src/index.css` to replace its contents with:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: sans-serif;
  background-color: #f3f4f6;
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "build(frontend): install and configure tailwind css v3.4"
```

### Task 2: Create Side-by-Side Layout Structure

**Files:**
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/components/DashboardPanel.tsx`
- Create: `frontend/src/components/ChatPanel.tsx`

- [ ] **Step 1: Create DashboardPanel component**

```tsx
// frontend/src/components/DashboardPanel.tsx
export default function DashboardPanel() {
  return (
    <div className="w-2/3 h-screen p-6 overflow-y-auto">
      <h2 className="text-2xl font-bold mb-4">Match Context</h2>
      <div className="bg-white p-4 rounded shadow">
        <h3 className="text-lg font-semibold">Arsenal vs Chelsea</h3>
        <p className="text-gray-600">Premier League - Matchday 30</p>
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Home Win</span>
            <span className="block text-xl font-bold">2.10</span>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Draw</span>
            <span className="block text-xl font-bold">3.40</span>
          </div>
          <div className="bg-red-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Away Win</span>
            <span className="block text-xl font-bold">3.60</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create ChatPanel component skeleton**

```tsx
// frontend/src/components/ChatPanel.tsx
export default function ChatPanel() {
  return (
    <div className="w-1/3 h-screen bg-white border-l flex flex-col">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-xl font-bold">BetWise Assistant</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        <p className="text-gray-500 text-center mt-10">Chat interface coming soon...</p>
      </div>
      <div className="p-4 border-t">
        <input 
          type="text" 
          placeholder="Ask about the match..." 
          className="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Update App.tsx to use layout**

Modify `frontend/src/App.tsx` to replace its contents with:
```tsx
import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';

function App() {
  return (
    <div className="flex w-full h-screen bg-gray-100">
      <DashboardPanel />
      <ChatPanel />
    </div>
  );
}

export default App;
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): add side-by-side layout for dashboard and chat"
```

### Task 3: Implement Rich Chat Interface

**Files:**
- Modify: `frontend/src/components/ChatPanel.tsx`
- Create: `frontend/src/types.ts`

- [ ] **Step 1: Define types**

```typescript
// frontend/src/types.ts
export interface Source {
  type: "news" | "odds";
  title?: string;
  snippet?: string;
  market?: string;
  value?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}
```

- [ ] **Step 2: Update ChatPanel with state and mock data rendering**

Modify `frontend/src/components/ChatPanel.tsx` to replace its contents with:
```tsx
// frontend/src/components/ChatPanel.tsx
import { useState } from 'react';
import { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "Hello! I'm ready to analyze the Arsenal vs Chelsea match. What would you like to know?"
    }
  ]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    // Mock bot response
    setTimeout(() => {
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: "Based on recent news, Arsenal's star striker is out with a knee injury. This might affect the Over 2.5 goals line.",
        sources: [
          { type: "news", title: "BBC Sport", snippet: "Knee injury sidelines striker for 3 weeks..." }
        ]
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1000);
  };

  return (
    <div className="w-1/3 h-screen bg-white border-l flex flex-col">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-xl font-bold">BetWise Assistant</h2>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {msg.content}
            </div>
            {msg.sources && msg.sources.map((src, idx) => (
              <div key={idx} className="mt-2 text-xs bg-yellow-50 border border-yellow-200 p-2 rounded w-full max-w-[85%]">
                <span className="font-bold">{src.title || src.market}</span>: {src.snippet || src.value}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="p-4 border-t flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about the match..." 
          className="flex-1 border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-4 py-2 rounded font-bold hover:bg-blue-700">
          Send
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): implement rich component chat UI with mock responses"
```

### Task 4: Setup Backend API Endpoint (Mocked)

**Files:**
- Modify: `backend/src/main.py`
- Modify: `backend/tests/test_main.py`

- [ ] **Step 1: Write failing test for chat endpoint**

Modify `backend/tests/test_main.py` to add:
```python
def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "Is the striker playing?", "match_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py -v`
Expected: FAIL (404 Not Found)

- [ ] **Step 3: Implement mock chat endpoint**

Modify `backend/src/main.py` to add:
```python
from pydantic import BaseModel
from typing import List, Optional

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
    # Mocked RAG response
    return ChatResponse(
        response=f"Received your query: '{request.message}'. The RAG pipeline is being integrated.",
        sources=[
            SourceModel(type="news", title="System", snippet="RAG backend integration pending.")
        ]
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat(backend): add mock /api/chat endpoint"
```