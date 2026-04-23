# Frontend & Infra Hardcodes Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate hardcoded fallback URLs in the React frontend and default passwords in Docker Compose, relying entirely on `.env` variables for configuration.

**Architecture:** We will replace the fallback "http://localhost:8080" in the frontend components with an empty string (or relative path `/api`) to properly route through proxies or use the domain origin. For Docker Compose, we will remove the `:-betwise_password` defaults.

**Tech Stack:** React (Vite), TypeScript, Docker Compose

---

### Task 1: Remove Hardcoded API URLs in Frontend

**Files:**
- Modify: `frontend/src/components/DashboardPanel.tsx:54`
- Modify: `frontend/src/components/ChatPanel.tsx:25`
- Modify: `frontend/src/components/AuditModal.tsx:18`

- [ ] **Step 1: Modify DashboardPanel.tsx**

```typescript
// In frontend/src/components/DashboardPanel.tsx
// Find: const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
// Replace with:
    const apiUrl = import.meta.env.VITE_API_URL || '';
```

- [ ] **Step 2: Modify ChatPanel.tsx**

```typescript
// In frontend/src/components/ChatPanel.tsx
// Find: const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
// Replace with:
      const apiUrl = import.meta.env.VITE_API_URL || '';
```

- [ ] **Step 3: Modify AuditModal.tsx**

```typescript
// In frontend/src/components/AuditModal.tsx
// Find: const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
// Replace with:
    const apiUrl = import.meta.env.VITE_API_URL || '';
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/DashboardPanel.tsx frontend/src/components/ChatPanel.tsx frontend/src/components/AuditModal.tsx
git commit -m "refactor(frontend): remove hardcoded localhost API URLs"
```

---

### Task 2: Clean Up Docker Compose Defaults

**Files:**
- Modify: `docker-compose.yml`
- Modify: `.env.example`

- [ ] **Step 1: Remove defaults from postgres variables in docker-compose.yml**

```yaml
# In docker-compose.yml, modify these lines to remove the default :-betwise_password
# Change POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-betwise_password} to:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

# Change the DATABASE_URL to:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Change VITE_API_URL: ${VITE_API_URL:-http://localhost:8080} to:
      - VITE_API_URL=${VITE_API_URL}
```

- [ ] **Step 2: Verify .env.example contains all required variables**

```bash
# Add missing postgres vars to .env.example (or create it if not present at root)
cat << 'EOF' >> .env.example

# Infra
POSTGRES_USER=betwise_user
POSTGRES_PASSWORD=tu_password_fuerte
POSTGRES_DB=betwise_db
VITE_API_URL=http://localhost:8080
EOF
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "chore(infra): remove default passwords and URLs from docker-compose"
```