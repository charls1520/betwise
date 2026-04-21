# UI Enhancements, Collapsible Menus, and Complete Match Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the backend to send dynamic match time (UTC-5) and league data, and update the frontend to display full team names, match time, dynamic league tags, and implement collapsible left navigation and right chat menus.

**Architecture:** Backend FastAPI endpoint `/api/dashboard` will be modified to parse `commence_time` and `sport_title` from raw JSON files. The React frontend will receive these new fields in `MatchData` and map them into the `DashboardPanel`. `App.tsx` will hold the `isNavOpen` and `isChatOpen` states to toggle CSS classes on the sidebars for fluid hiding/showing.

**Tech Stack:** FastAPI, React, TailwindCSS, TypeScript.

---

### Task 1: Update Backend Endpoint Data Extraction

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: Modify `/api/dashboard` to parse match_time and league**
Update the match object extraction in `get_dashboard_data` to include `match_time` (converting to UTC-5 if possible or passing as string to be formatted in frontend) and `league` from `sport_title`.

```python
            # In get_dashboard_data, around line 316 of backend/src/main.py
            match_obj = {
                "id": idx,
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "prob_home_win": home_prob,
                "prob_draw": pred.get("prob_draw", 0.0),
                "prob_away_win": pred.get("prob_away_win", 0.0),
                "home_odds": home_odds,
                "home_edge": edge,
                # New fields:
                "match_time": match.get("commence_time", "TBA"),
                "league": match.get("sport_title", "PREMIER LEAGUE"),
            }
```

- [ ] **Step 2: Commit backend changes**
```bash
git add backend/src/main.py
git commit -m "feat(backend): add match_time and league to dashboard payload"
```

### Task 2: Update Frontend MatchData Type

**Files:**
- Modify: `frontend/src/components/DashboardPanel.tsx`

- [ ] **Step 1: Update `MatchData` interface**
Add `match_time` and `league` to the `MatchData` interface.

```typescript
// frontend/src/components/DashboardPanel.tsx
interface MatchData {
  id: number;
  home_team: string;
  away_team: string;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  home_odds: number;
  home_edge: number;
  match_time?: string;
  league?: string;
  error?: string;
}
```

- [ ] **Step 2: Commit type changes**
```bash
git add frontend/src/components/DashboardPanel.tsx
git commit -m "feat(frontend): update MatchData interface with match_time and league"
```

### Task 3: Update DashboardPanel Match UI

**Files:**
- Modify: `frontend/src/components/DashboardPanel.tsx`

- [ ] **Step 1: Create a time formatter utility function**
Create a small helper inside `DashboardPanel.tsx` to format UTC time to UTC-5 (Bogota) time.

```typescript
// Add inside DashboardPanel.tsx (before the component)
const formatToUTC5 = (utcTimeString: string | undefined) => {
  if (!utcTimeString || utcTimeString === "TBA") return "TBA";
  try {
    const date = new Date(utcTimeString);
    return date.toLocaleString("es-CO", {
      timeZone: "America/Bogota",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
    });
  } catch (e) {
    return utcTimeString;
  }
};
```

- [ ] **Step 2: Update Match Cards to show full names, dynamic league, and time**
Remove the `.substring(0, 3).toUpperCase()` from team names. Replace "PREMIER LEAGUE" with `match.league`. Add the formatted time.

```tsx
// Inside DashboardPanel.tsx map iteration:
                <div className="flex items-center justify-between mb-6">
                  <div className="flex flex-col">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-sm text-white">{match.home_team}</span>
                      <span className="text-[#9eabc8] text-xs font-bold">VS</span>
                      <span className="font-bold text-sm text-white">{match.away_team}</span>
                    </div>
                    <span className="text-[#9eabc8] text-[10px] mt-1">{formatToUTC5(match.match_time)}</span>
                  </div>
                  <span className="text-[10px] font-bold text-[#6bff8f] bg-[#6bff8f]/10 px-2 py-1 rounded">{match.league || "PREMIER LEAGUE"}</span>
                </div>
```

- [ ] **Step 3: Commit UI changes**
```bash
git add frontend/src/components/DashboardPanel.tsx
git commit -m "feat(frontend): display full team names, match time in UTC-5, and dynamic league"
```

### Task 4: Implement Collapsible Sidebars in Layout

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/DashboardPanel.tsx`
- Modify: `frontend/src/components/ChatPanel.tsx`

- [ ] **Step 1: Add state to `App.tsx`**
```tsx
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
```

- [ ] **Step 2: Add toggle buttons in `App.tsx` Header**
Next to the Logo, add a hamburger button for the left nav. Next to the notifications, add a chat toggle button.

```tsx
          <div className="flex items-center gap-4">
            <button onClick={() => setIsNavOpen(!isNavOpen)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors">
              <span className="material-symbols-outlined">menu</span>
            </button>
            <span className="text-2xl font-bold tracking-tighter text-[#6bff8f] uppercase font-['Space_Grotesk']">THE KINETIC VAULT</span>
// ...
            <div className="flex items-center gap-3">
              <button onClick={() => setIsChatOpen(!isChatOpen)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors" title="Toggle Chat">
                <span className="material-symbols-outlined">chat</span>
              </button>
```

- [ ] **Step 3: Update Left Sidebar classes in `App.tsx`**
Change the `<aside>` tags to use the `isNavOpen` state for translating.
```tsx
        <aside className={`fixed left-0 top-16 h-[calc(100vh-64px)] w-64 bg-[#02132b] flex-col py-6 overflow-y-auto transition-transform duration-300 z-40 flex ${isNavOpen ? 'translate-x-0' : '-translate-x-full'}`}>
```

- [ ] **Step 4: Update Right Sidebar (`ChatPanel.tsx`) via props**
Modify `ChatPanel` to receive `isOpen`.
```tsx
// frontend/src/components/ChatPanel.tsx
export default function ChatPanel({ isOpen }: { isOpen: boolean }) {
// ...
    <aside className={`fixed right-0 top-16 h-[calc(100vh-64px)] w-80 bg-[#102645]/90 backdrop-blur-2xl border-l border-white/5 flex-col shadow-[-10px_0px_30px_rgba(0,0,0,0.5)] transition-transform duration-300 z-40 flex ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
```
Update `App.tsx` to pass the prop:
`<ChatPanel isOpen={isChatOpen} />`

- [ ] **Step 5: Adjust `DashboardPanel` margin via props**
Modify `DashboardPanel.tsx` component definition to receive the state. Note that if loading is true, we still render the main wrapper.
```tsx
// frontend/src/components/DashboardPanel.tsx
export default function DashboardPanel({ isNavOpen, isChatOpen }: { isNavOpen?: boolean, isChatOpen?: boolean }) {
// ...
  if (loading) return <main className={`flex-grow overflow-y-auto px-6 py-8 text-[#6bff8f] transition-all duration-300 ${isNavOpen ? 'ml-64' : 'ml-0'} ${isChatOpen ? 'mr-80' : 'mr-0'}`}>Cargando analíticas...</main>;
// ...
  <main className={`flex-grow overflow-y-auto px-6 py-8 transition-all duration-300 ${isNavOpen ? 'ml-64' : 'ml-0'} ${isChatOpen ? 'mr-80' : 'mr-0'}`}>
```
Update `App.tsx`:
`<DashboardPanel isNavOpen={isNavOpen} isChatOpen={isChatOpen} />`

- [ ] **Step 6: Commit layout changes**
```bash
git add frontend/src/App.tsx frontend/src/components/DashboardPanel.tsx frontend/src/components/ChatPanel.tsx
git commit -m "feat(frontend): implement collapsible sidebars and dynamic main panel width"
```