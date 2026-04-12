# UI Redesign and Gemma LLM Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the LLM backend to use Gemma4:26b, and overhaul the React frontend with a modern dark mode Bento Box layout inspired by Stitch.

**Architecture:** Python backend config update for LlamaIndex. React component extraction and restyling using Tailwind utility classes provided by the Stitch HTML reference.

**Tech Stack:** React, Tailwind CSS, LlamaIndex, Python.

---

### Task 1: Update LlamaIndex Configuration to Gemma

**Files:**
- Modify: `backend/src/rag/config.py`
- Modify: `backend/tests/rag/test_config.py`

- [ ] **Step 1: Write the failing test**

Modify `backend/tests/rag/test_config.py` to change the expected model name:
```python
# backend/tests/rag/test_config.py
from src.rag.config import init_llama_index
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

def test_init_llama_index():
    init_llama_index()
    
    assert isinstance(Settings.embed_model, HuggingFaceEmbedding)
    assert Settings.embed_model.model_name == "BAAI/bge-small-en-v1.5"
    
    assert isinstance(Settings.llm, Ollama)
    # The model should now be gemma4:26b
    assert Settings.llm.model == "gemma4:26b"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_config.py -v`
Expected: FAIL (AssertionError: 'llama3' == 'gemma4:26b')

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/rag/config.py` to use `gemma4:26b`:
```python
# backend/src/rag/config.py
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

def init_llama_index():
    """Initializes global LlamaIndex settings for embeddings and LLM."""
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    # Updated to use gemma4:26b per new spec
    Settings.llm = Ollama(model="gemma4:26b", request_timeout=120.0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/rag/config.py backend/tests/rag/test_config.py
git commit -m "refactor(rag): upgrade local LLM model from llama3 to gemma4:26b"
```

### Task 2: Setup Tailwind Theme and Global Styles

**Files:**
- Modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Update tailwind.config.js**

Modify `frontend/tailwind.config.js` to match the Stitch design tokens:
```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "outline": "#687690",
        "tertiary": "#47c4ff",
        "surface-variant": "#102645",
        "outline-variant": "#3b4861",
        "surface-container-high": "#0b203d",
        "on-surface": "#dbe6ff",
        "primary-container": "#0abc56",
        "background": "#010e24",
        "surface-bright": "#152c4e",
        "primary": "#6bff8f",
        "on-surface-variant": "#9eabc8",
        "surface-container-low": "#02132b",
        "surface-container": "#061934",
      },
      fontFamily: {
        headline: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"],
      }
    },
  },
  plugins: [],
}
```

- [ ] **Step 2: Update index.css**

Modify `frontend/src/index.css` to add the fonts and dark mode base:
```css
/* frontend/src/index.css */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Manrope', sans-serif;
  background-color: #010e24;
  color: #dbe6ff;
  margin: 0;
}

h1, h2, h3, .font-headline {
  font-family: 'Space Grotesk', sans-serif;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3b4861; border-radius: 10px; }
```

- [ ] **Step 3: Update index.html to enforce dark mode class**

Modify `frontend/index.html` to add `class="dark"` to the `<html>` tag:
```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BetWise Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "style(frontend): apply dark mode theme and kinetic vault typography"
```

### Task 3: Redesign Dashboard Panel (Main View)

**Files:**
- Modify: `frontend/src/components/DashboardPanel.tsx`

- [ ] **Step 1: Update DashboardPanel.tsx**

Replace `frontend/src/components/DashboardPanel.tsx` with the new design:
```tsx
// frontend/src/components/DashboardPanel.tsx
import { useEffect, useState } from 'react';

interface MatchData {
  id: number;
  home_team: string;
  away_team: string;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  error?: string;
}

export default function DashboardPanel() {
  const [matches, setMatches] = useState<MatchData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard')
      .then(res => res.json())
      .then(data => {
        setMatches(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="flex-grow px-6 py-8 text-primary">Loading analytics...</div>;

  return (
    <main className="flex-grow overflow-y-auto px-6 py-8 bg-background">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary">sensors</span>
        <h2 className="text-2xl font-headline font-bold uppercase tracking-tight text-white">Live AI Fixtures</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {matches.map((match) => (
          match.error ? (
             <div key="err" className="text-red-500">Error: {match.error}</div>
          ) : (
            <div key={match.id} className="bg-surface-container-high rounded-xl p-6 relative overflow-hidden group border border-white/5">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-sm text-white uppercase">{match.home_team.substring(0, 3)}</span>
                  <span className="text-on-surface-variant text-xs font-bold">VS</span>
                  <span className="font-bold text-sm text-white uppercase">{match.away_team.substring(0, 3)}</span>
                </div>
                <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-1 rounded uppercase">PREMIER LEAGUE</span>
              </div>
              
              <div className="space-y-3">
                <p className="text-[10px] font-black text-on-surface-variant uppercase">AI 1X2 Probabilities</p>
                <div className="flex gap-2">
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">1 (HOME)</span>
                    <span className="font-headline font-bold text-xs text-primary">{(match.prob_home_win * 100).toFixed(1)}%</span>
                  </button>
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">X (DRAW)</span>
                    <span className="font-headline font-bold text-xs text-white">{(match.prob_draw * 100).toFixed(1)}%</span>
                  </button>
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">2 (AWAY)</span>
                    <span className="font-headline font-bold text-xs text-white">{(match.prob_away_win * 100).toFixed(1)}%</span>
                  </button>
                </div>
              </div>
            </div>
          )
        ))}
        {matches.length === 0 && <p className="text-on-surface-variant">No matches found in the datalake.</p>}
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/DashboardPanel.tsx
git commit -m "feat(frontend): redesign dashboard panel to match kinetic vault UI"
```

### Task 4: Redesign Chat Panel (Sidebar)

**Files:**
- Modify: `frontend/src/components/ChatPanel.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update App.tsx wrapper**

Modify `frontend/src/App.tsx`:
```tsx
import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';

function App() {
  return (
    <div className="flex w-full h-screen bg-background overflow-hidden">
      <DashboardPanel />
      <ChatPanel />
    </div>
  );
}

export default App;
```

- [ ] **Step 2: Update ChatPanel.tsx**

Replace `frontend/src/components/ChatPanel.tsx` with the styled version:
```tsx
// frontend/src/components/ChatPanel.tsx
import { useState } from 'react';
import type { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "System online. I am your Soccer AI Analyst. What matches are we analyzing today?"
    }
  ]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content, match_id: 1 })
      });
      const data = await response.json();
      
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: data.response,
        sources: data.sources
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now().toString(), role: "bot", content: "Error connecting to the AI engine." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="w-80 h-screen bg-surface-container-high/90 backdrop-blur-2xl border-l border-white/5 flex flex-col flex-shrink-0 shadow-[-10px_0px_30px_rgba(0,0,0,0.5)]">
      {/* Header */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-bold text-tertiary uppercase font-headline flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">smart_toy</span>
            AI ANALYST
          </span>
          <span className="flex items-center gap-1 text-[10px] text-primary font-bold">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
            ACTIVE
          </span>
        </div>
        <p className="text-[10px] text-on-surface-variant font-medium">BetWise RAG Engine powered by Gemma</p>
      </div>
      
      {/* Chat Area */}
      <div className="flex-grow overflow-y-auto p-4 space-y-6">
        {messages.map(msg => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            
            {/* Avatar */}
            <div className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 border ${msg.role === 'user' ? 'bg-surface-bright border-outline-variant' : 'bg-primary/20 border-primary/20'}`}>
              <span className={`material-symbols-outlined text-sm ${msg.role === 'user' ? 'text-white' : 'text-primary'}`}>
                {msg.role === 'user' ? 'person' : 'precision_manufacturing'}
              </span>
            </div>

            {/* Message Bubble */}
            <div className={`${msg.role === 'user' ? 'bg-surface-bright rounded-tr-none' : 'bg-surface-container rounded-tl-none'} rounded-lg p-3 max-w-[80%] border border-white/5`}>
              <p className={`text-[10px] font-bold mb-1 uppercase ${msg.role === 'user' ? 'text-white' : 'text-tertiary'}`}>
                {msg.role === 'user' ? 'YOU' : 'KINETIC AI'}
              </p>
              <p className="text-xs text-on-surface leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              
              {/* Rich Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.sources.map((src, idx) => (
                    <div key={idx} className="bg-black/20 border border-primary/20 rounded p-2">
                      <p className="text-[8px] text-primary font-bold uppercase mb-1">{src.type} Context</p>
                      <p className="text-[10px] text-white font-bold">{src.title}</p>
                      {src.snippet && <p className="text-[9px] text-on-surface-variant mt-1 line-clamp-2">{src.snippet}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
             <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/20">
              <span className="material-symbols-outlined text-primary text-sm animate-spin">autorenew</span>
            </div>
            <div className="bg-surface-container rounded-lg rounded-tl-none p-3 border border-white/5">
              <p className="text-xs text-on-surface-variant animate-pulse">Running inference...</p>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/5 bg-background/50">
        <div className="relative group focus-within:ring-1 ring-primary rounded-lg">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder="Ask AI Analyst..." 
            disabled={loading}
            className="w-full bg-surface-container border-none focus:ring-0 rounded-lg text-sm py-3 pl-4 pr-12 text-on-surface placeholder-on-surface-variant/50 outline-none"
          />
          <button 
            onClick={handleSend} 
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-primary hover:scale-110 transition-transform disabled:opacity-50"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatPanel.tsx frontend/src/App.tsx
git commit -m "feat(frontend): redesign chat sidebar to kinetic vault style"
```
````