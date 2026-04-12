# System Health & Audit Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a transparent health and audit panel in the React frontend that displays real-time metadata about the ML and RAG engines.

**Architecture:** Create a `/api/health/audit` endpoint in FastAPI that aggregates information from ChromaDB, OS file timestamps, and the Data Lake. In React, add a modal component triggered by the top navigation bar to display this JSON.

**Tech Stack:** Python 3.10+, FastAPI, React, Tailwind CSS.

---

### Task 1: Create Backend Audit Endpoint

**Files:**
- Modify: `backend/src/main.py`
- Modify: `backend/tests/test_main.py`

- [ ] **Step 1: Write the failing test**

Modify `backend/tests/test_main.py`:
```python
def test_audit_endpoint():
    response = client.get("/api/health/audit")
    assert response.status_code == 200
    data = response.json()
    assert "rag_engine" in data
    assert "ml_engine" in data
    assert "ingestion_engine" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py::test_audit_endpoint -v`
Expected: FAIL (404 Not Found)

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/main.py`:
```python
import time

@app.get("/api/health/audit")
def get_audit_log():
    # 1. RAG Engine Status
    rag_status = {
        "status": "Healthy" if global_index else "Offline",
        "total_documents": len(global_index.docstore.docs) if global_index else 0,
        "last_news_indexed": "Latest from Data Lake" if global_index else "None"
    }
    
    # 2. ML Engine Status
    model_path = "models/winner_model.joblib"
    ml_status = {
        "status": "Healthy" if os.path.exists(model_path) else "Offline",
        "model_last_trained": time.ctime(os.path.getmtime(model_path)) if os.path.exists(model_path) else "Never",
        "sources_used": ["football-data.co.uk (E0.csv)"]
    }
    
    # 3. Ingestion Engine Status
    ingestion_status = {
        "status": "Operational",
        "last_odds_fetch": "Live via API",
        "last_xg_fetch": "Live via Playwright",
        "normalization_warnings": [] # Would be populated from a DB log in production
    }
    
    return {
        "rag_engine": rag_status,
        "ml_engine": ml_status,
        "ingestion_engine": ingestion_status
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/test_main.py::test_audit_endpoint -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/main.py backend/tests/test_main.py
git commit -m "feat(api): add health and audit endpoint for system transparency"
```

### Task 2: Create Audit Modal Component in Frontend

**Files:**
- Create: `frontend/src/components/AuditModal.tsx`

- [ ] **Step 1: Create Component Implementation**

Create `frontend/src/components/AuditModal.tsx`:
```tsx
import { useEffect, useState } from 'react';

interface AuditModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AuditData {
  rag_engine: { status: string; total_documents: number; last_news_indexed: string };
  ml_engine: { status: string; model_last_trained: string; sources_used: string[] };
  ingestion_engine: { status: string; last_odds_fetch: string; last_xg_fetch: string; normalization_warnings: string[] };
}

export default function AuditModal({ isOpen, onClose }: AuditModalProps) {
  const [data, setData] = useState<AuditData | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetch('http://localhost:8000/api/health/audit')
        .then(res => res.json())
        .then(setData)
        .catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#0b203d] border border-[#3b4861] rounded-xl w-[500px] shadow-2xl overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-[#3b4861]">
          <h2 className="text-[#6bff8f] font-['Space_Grotesk'] font-bold flex items-center gap-2">
            <span className="material-symbols-outlined">analytics</span>
            System Health & Audit Log
          </h2>
          <button onClick={onClose} className="text-[#9eabc8] hover:text-white">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {!data ? <p className="text-white text-center">Loading audit data...</p> : (
            <>
              {/* ML Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">Machine Learning Engine</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Status:</span> {data.ml_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Last Trained:</span> {data.ml_engine.model_last_trained}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Sources:</span> {data.ml_engine.sources_used.join(", ")}</p>
                </div>
              </div>
              
              {/* RAG Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">RAG Context Engine</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Status:</span> {data.rag_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Chunks Indexed:</span> {data.rag_engine.total_documents}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Latest News:</span> {data.rag_engine.last_news_indexed}</p>
                </div>
              </div>

              {/* Ingestion Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">Ingestion Engine</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Status:</span> {data.ingestion_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Odds Data:</span> {data.ingestion_engine.last_odds_fetch}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">xG Data:</span> {data.ingestion_engine.last_xg_fetch}</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AuditModal.tsx
git commit -m "feat(frontend): create system audit modal component"
```

### Task 3: Connect Audit Modal to App Layout

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add State and render modal**

Modify `frontend/src/App.tsx`:
```tsx
import { useState } from 'react';
import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';
import AuditModal from './components/AuditModal';

function App() {
  const [isAuditOpen, setIsAuditOpen] = useState(false);

  return (
    <div className="flex bg-[#010e24] h-screen overflow-hidden text-[#dbe6ff] font-['Manrope']">
      <header className="fixed top-0 w-full z-50 bg-[#102645]/80 backdrop-blur-xl shadow-2xl shadow-black/40">
        <div className="flex justify-between items-center px-6 h-16 w-full max-w-screen-2xl mx-auto">
          <div className="flex items-center gap-8">
            <span className="text-2xl font-bold tracking-tighter text-[#6bff8f] uppercase font-['Space_Grotesk']">THE KINETIC VAULT</span>
            <nav className="hidden md:flex gap-6">
              <a className="text-[#6bff8f] border-b-2 border-[#6bff8f] pb-1 font-['Space_Grotesk'] tracking-tight" href="#">FÚTBOL</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">PARTIDOS EN VIVO</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">ANÁLISIS IA</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">PROMOS</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative bg-[#0b203d] px-4 py-2 rounded-lg hidden lg:flex items-center gap-2">
              <span className="material-symbols-outlined text-[#9eabc8] text-sm">search</span>
              <input className="bg-transparent border-none focus:ring-0 text-sm p-0 w-48 text-[#dbe6ff] outline-none" placeholder="Buscar ligas..." type="text" />
            </div>
            <div className="flex items-center gap-3">
              <button className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <button onClick={() => setIsAuditOpen(true)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors" title="System Audit">
                <span className="material-symbols-outlined">analytics</span>
              </button>
              <div className="h-8 w-8 rounded-full overflow-hidden bg-[#152c4e] flex items-center justify-center">
                <span className="material-symbols-outlined text-sm text-white">person</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* App Layout Container */}
      <div className="flex pt-16 h-screen w-full">
        {/* Sidebar Left: Soccer Navigation */}
        <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-64 bg-[#02132b] flex-col py-6 overflow-y-auto hidden xl:flex">
          <div className="px-6 mb-8">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg font-black text-[#6bff8f] font-['Space_Grotesk']">CENTRO DE FÚTBOL</span>
              <div className="bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] px-1.5 py-0.5 rounded font-bold uppercase">AI PRO</div>
            </div>
            <p className="text-[10px] text-[#9eabc8] font-bold tracking-widest">FILTROS TÁCTICOS</p>
          </div>
          <nav className="flex-grow space-y-1">
            <a className="flex items-center gap-3 bg-[#0b203d] text-[#6bff8f] rounded-r-full py-3 px-6 border-l-4 border-[#6bff8f] translate-x-1 transition-transform" href="#">
              <span className="material-symbols-outlined">sensors</span>
              <span className="font-medium">Partidos en Vivo</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">today</span>
              <span className="font-medium">Jornada de Hoy</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">upcoming</span>
              <span className="font-medium">Próximos Eventos</span>
            </a>
            <div className="pt-6 px-6 pb-2">
              <p className="text-[10px] text-[#9eabc8] font-bold tracking-widest uppercase">Ligas Élite</p>
            </div>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">emoji_events</span>
              <span className="font-medium">Champions League</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">sports_soccer</span>
              <span className="font-medium">Premier League</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">flag</span>
              <span className="font-medium">La Liga</span>
            </a>
          </nav>
          <div className="px-6 mt-auto">
            <button className="w-full bg-gradient-to-r from-[#6bff8f] to-[#0abc56] text-[#002c0f] font-extrabold py-4 rounded-lg shadow-lg shadow-[#6bff8f]/20 hover:scale-95 duration-150 ease-in-out uppercase text-xs tracking-tighter">
              CREADOR DE TICKETS INSTANTÁNEO
            </button>
          </div>
        </aside>

        <DashboardPanel />
        <ChatPanel />
      </div>
      
      <AuditModal isOpen={isAuditOpen} onClose={() => setIsAuditOpen(false)} />
    </div>
  );
}

export default App;
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): integrate audit modal into top navigation bar"
```
````