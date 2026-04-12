# BetWise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the foundational Python-First architecture for BetWise, including a FastAPI backend, relational database schema, and a React (Vite) frontend to display a dashboard.

**Architecture:** A monolithic Python API that serves data and handles ML/RAG logic, paired with a React SPA frontend.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy, pytest, Node.js, React, Vite, TypeScript.

---

### Task 1: Setup Backend Environment and Healthcheck

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/src/main.py`
- Create: `backend/tests/test_main.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "BetWise API is running"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_main.py -v`
Expected: FAIL (No module named 'src.main' or file not found)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BetWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "BetWise API is running"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: setup fastapi backend and healthcheck"
```

### Task 2: Initialize Database Models (Relational)

**Files:**
- Create: `backend/src/database.py`
- Create: `backend/src/models.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_models.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Team

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_create_team():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    new_team = Team(name="Arsenal FC", canonical_name="Arsenal")
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    assert new_team.id is not None
    assert new_team.canonical_name == "Arsenal"
    
    db.close()
    Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_models.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./betwise.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

```python
# backend/src/models.py
from sqlalchemy import Column, Integer, String
from src.database import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    canonical_name = Column(String, index=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/database.py backend/src/models.py backend/tests/test_models.py
git commit -m "feat: add initial database models for teams"
```

### Task 3: Setup Frontend React App

**Files:**
- Create: `frontend/` (via Vite)

- [ ] **Step 1: Scaffold the app**

Run: `cd BetWise && npm create vite@latest frontend -- --template react-ts`

- [ ] **Step 2: Install dependencies**

Run: `cd frontend && npm install`

- [ ] **Step 3: Connect Frontend to Backend Healthcheck**

Modify: `frontend/src/App.tsx`
```tsx
import { useEffect, useState } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...')

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setApiStatus(data.message))
      .catch(() => setApiStatus('API Offline'))
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>BetWise Dashboard</h1>
      <p>Status: {apiStatus}</p>
    </div>
  )
}

export default App
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: initialize react frontend connected to api"
```

### Task 4: Update Documentation

**Files:**
- Modify: `docs/MASTER-PLAN.md`
- Modify: `docs/SPEC.md`
- Modify: `README.md`

- [ ] **Step 1: Update SPEC.md**

Reflect that the initial Python API and React Frontend scaffolds are complete, and SQLite is being used for development.

- [ ] **Step 2: Create README.md execution instructions**

```markdown
# BetWise

## Cómo ejecutar

Para levantar el proyecto completo (requiere tener Node y Python instalados):

Abre dos terminales:
1. Backend: `cd backend && pip install -r requirements.txt && uvicorn src.main:app --reload`
2. Frontend: `cd frontend && npm install && npm run dev`
```

- [ ] **Step 3: Update MASTER-PLAN.md**

Mark "Definir la idea con brainstorming" as Complete, and add new next steps: "Implementar motor de scraping" and "Configurar LlamaIndex".

- [ ] **Step 4: Commit**

```bash
git add docs/ README.md
git commit -m "docs: update specs and execution instructions"
```