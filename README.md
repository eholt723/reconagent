---
title: ReconAgent
emoji: 🔍
colorFrom: cyan
colorTo: teal
sdk: docker
pinned: false
---

# AutoResearch Agent

An autonomous research agent that accepts a plain-text topic, dynamically plans and executes a multi-step web search strategy, reflects on whether the results are sufficient, and streams both its reasoning trace and a final structured report back to the browser in real time.

The key feature is the visible agent reasoning loop. The frontend displays every internal decision as it happens — what queries the agent planned, what it found, whether it judged the results sufficient or chose to refine and search again — before the final report appears. This is not a chatbot or a fixed RAG pipeline; the agent decides its own search strategy and self-corrects.

---

## How it works

The agent runs as a compiled LangGraph `StateGraph` with four nodes:

1. **Planner** — takes the user's topic and generates 3-5 targeted search queries using the LLM before executing anything
2. **Search** — runs each query against the Tavily Search API and collects results
3. **Reflection** — evaluates whether the results are sufficient to write a good report; if not, generates refined queries and loops back to Search (capped at 2 iterations)
4. **Synthesis** — deduplicates sources, aggregates all findings, and writes a structured markdown report

Each node emits typed SSE events (`planning`, `searching`, `reflecting`, `synthesizing`, `report`, `done`) as it runs. The frontend renders these progressively, giving a live view of the agent's reasoning before the final report appears.

Past research runs are stored in SQLite and retrievable via `/research/history`.

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph (StateGraph) |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Web search | Tavily Search API |
| Backend | FastAPI, Python 3.11+ |
| Streaming | Server-Sent Events via `StreamingResponse` |
| Database | SQLite via aiosqlite |
| Frontend | React 18, Vite, Tailwind CSS |
| Markdown rendering | react-markdown + remark-gfm |
| Deployment | Docker (multi-stage), Render free tier |

---

## Local development

### Prerequisites

- Python 3.11+
- Node 18+
- A [Groq API key](https://console.groq.com) (free tier)
- A [Tavily API key](https://app.tavily.com) (free tier, 1,000 searches/month)

### Setup

**1. Environment variables**

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

**2. Python environment**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**3. Frontend dependencies**

```bash
cd frontend && npm install && cd ..
```

### Running

Start the backend (terminal 1):

```bash
.venv/bin/uvicorn app.main:app --reload
```

Start the frontend (terminal 2):

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies all `/research/*` requests to the backend at port 8000.

---

## API

### `POST /research/stream`

Accepts a research topic and streams the full agent run as Server-Sent Events.

Request body:
```json
{ "topic": "your research topic" }
```

SSE event types:

| Type | Description |
|---|---|
| `planning` | Query planning step |
| `searching` | Web search execution |
| `reflecting` | Result evaluation / refinement decision |
| `synthesizing` | Report generation |
| `report` | Final markdown report content |
| `error` | Agent error message |
| `done` | Stream complete |

### `GET /research/history?limit=20`

Returns past research runs from SQLite.

---

## Project structure

```
reconagent/
├── app/
│   ├── agent/
│   │   ├── graph.py       # LangGraph StateGraph definition
│   │   ├── nodes.py       # Planner, Search, Reflection, Synthesis nodes
│   │   ├── prompts.py     # LLM prompt templates
│   │   └── state.py       # AgentState TypedDict
│   ├── db/
│   │   └── database.py    # SQLite helpers (aiosqlite)
│   ├── routes/
│   │   └── research.py    # /research/stream and /research/history
│   ├── config.py          # Pydantic settings (reads .env)
│   └── main.py            # FastAPI app, CORS, static file serving
├── frontend/
│   └── src/
│       ├── App.jsx                      # SSE fetch, top-level state
│       └── components/
│           ├── ResearchInput.jsx        # Topic input + Run/Stop
│           ├── TracePanel.jsx           # Live reasoning trace
│           └── ReportPanel.jsx          # Markdown report + copy
├── Dockerfile             # Multi-stage: Vite build -> FastAPI serve
├── render.yaml            # Render deployment config
└── requirements.txt
```

---

## Deployment (Render)

The `Dockerfile` uses a two-stage build: the first stage builds the React app with Vite, the second stage runs the FastAPI backend and serves the built frontend as static files from the same container.

To deploy on Render:

1. Push to GitHub
2. Create a new **Web Service** on Render, connect this repo, and set runtime to **Docker**
3. Add environment variables: `GROQ_API_KEY`, `TAVILY_API_KEY`
4. The `render.yaml` in this repo handles the rest, including a 1 GB persistent disk for SQLite at `/data`
