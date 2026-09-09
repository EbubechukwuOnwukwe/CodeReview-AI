# CodeReview AI

An AI-powered code review system that uses a multi-agent pipeline to analyze source code for bugs, security vulnerabilities, performance issues, and requirement violations. Paste code directly or point it at a GitHub repository — the system produces a structured, verified report with severity-graded findings.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Project Structure](#project-structure)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Tech Stack](#tech-stack)

---

## Overview

CodeReview AI accepts source code (or a GitHub repository URL) together with optional project requirements, then runs it through a four-stage AI agent pipeline:

1. **Requirements Agent** — extracts structured functional, security, and acceptance requirements from the user's description.
2. **Reviewer Agent** — splits the codebase into chunks and reviews each one for findings.
3. **Verifier Agent** — independently verifies every finding against the source code to eliminate false positives.
4. **Summary Agent** — synthesises all verified findings into a final structured report.

Results are stored in a Django/SQLite database and exposed over a REST API consumed by a React + TypeScript frontend.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                         │
│          React 19 + TypeScript + Vite + Tailwind        │
│                                                         │
│  Home ──► ReviewForm ──► ReviewResults ──► Evaluation   │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Django 6 Backend                     │
│              Django REST Framework · Jazzmin            │
│                                                         │
│  POST /api/reviews/        →  Create & run review       │
│  GET  /api/reviews/        →  List reviews              │
│  GET  /api/reviews/{id}/   →  Review detail             │
│  POST /api/reviews/{id}/retry/  →  Re-run failed review │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Multi-Agent Orchestrator                │
│                                                         │
│  RequirementsAgent                                      │
│       ↓                                                 │
│  ReviewerAgent  (per chunk, rate-limited)               │
│       ↓                                                 │
│  VerificationAgent  (per finding)                       │
│       ↓                                                 │
│  SummaryAgent                                           │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
              Groq API  (structured JSON output)
```

---

## Agent Pipeline

### 1 · Requirements Agent
- Reads the user-supplied requirements text.
- Outputs a `RequirementsSchema`: functional requirements, security requirements, constraints, and acceptance criteria.
- Runs **once** per review (not per chunk).

### 2 · Reviewer Agent
- The `CodeChunker` splits the full codebase into token-friendly chunks (respecting file boundaries and natural code blocks).
- Each chunk is reviewed independently by the Reviewer Agent.
- Produces `FindingSchema` objects: `title`, `severity`, `category`, `file_path`, `line_number`, `evidence`, `explanation`, `suggested_fix`, `confidence`.
- Severity levels: `critical` · `high` · `medium` · `low` · `info`
- Categories: `security` · `correctness` · `performance` · `reliability` · `maintainability` · `code_quality` · `requirements`

### 3 · Verification Agent
- Each finding from Step 2 is re-evaluated in isolation against the relevant code chunk.
- Returns `verification_status` (`verified` / `rejected`), a corrected severity, and a reason.
- Only **verified** findings are included in the final report.

### 4 · Summary Agent
- Consumes all verified findings and the requirements analysis.
- Produces a `SummarySchema`: `overall_summary`, `risk_level`, `priority_actions`, `severity_summary`, and `recommendations`.

---

## Project Structure

```
CodeReview AI/
├── backend/
│   ├── agents/
│   │   ├── base.py               # BaseAgent — wraps LLMService
│   │   ├── code_chunker.py       # Splits code into reviewable chunks
│   │   ├── orchestrator.py       # Pipeline coordinator
│   │   ├── requirements_agent.py # Step 1: requirements extraction
│   │   ├── reviewer_agent.py     # Step 2: per-chunk code review
│   │   ├── verifier_agent.py     # Step 3: finding verification
│   │   ├── summary_agent.py      # Step 4: final report generation
│   │   └── schemas.py            # Pydantic response schemas
│   │
│   ├── config/
│   │   ├── settings.py           # Django settings
│   │   └── urls.py               # Root URL configuration
│   │
│   ├── integrations/
│   │   ├── groq.py               # Groq API client + rate limiter
│   │   ├── llm.py                # LLMService abstraction layer
│   │   └── github.py             # GitHub file fetching service
│   │
│   ├── reviews/
│   │   ├── models.py             # Review, Finding, AgentTrajectory
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # ReviewViewSet (CRUD + retry)
│   │   └── urls.py               # Router registration
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                      # Secret keys and config (not committed)
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Home.tsx           # Landing page + review list
    │   │   ├── NewReview.tsx      # Review submission page
    │   │   ├── ReviewResults.tsx  # Detailed results view
    │   │   └── Evaluation.tsx     # Evaluation / metrics page
    │   │
    │   ├── components/
    │   │   ├── Navbar.tsx         # Top navigation bar
    │   │   ├── ReviewForm.tsx     # Code submission form
    │   │   ├── FindingCard.tsx    # Individual finding display
    │   │   ├── SeverityBadge.tsx  # Severity colour badge
    │   │   ├── AgentProgress.tsx  # Live agent step progress
    │   │   └── AgentTrajectory.tsx# Agent step-by-step trace
    │   │
    │   ├── services/
    │   │   └── api.ts             # Axios API client
    │   │
    │   ├── types/                 # TypeScript interfaces
    │   ├── App.tsx                # Router setup
    │   └── main.tsx               # React entry point
    │
    ├── index.html
    ├── vite.config.ts
    └── package.json
```

---

## Backend Setup

### Prerequisites
- Python 3.11+
- A [Groq API key](https://console.groq.com/)

### Installation

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser (optional — for the /admin panel)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.  
The admin panel (powered by Jazzmin) is at `http://127.0.0.1:8000/admin/`.

---

## Frontend Setup

### Prerequisites
- Node.js 18+

### Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173/`.

> **Note:** The Vite dev server is pre-configured to proxy `/api` requests to `http://127.0.0.1:8000`, so both servers must be running simultaneously.

---

## Environment Variables

Create a `.env` file inside the `backend/` directory. The following variables are supported:

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Your Groq API key |
| `GROQ_MODEL` | ❌ | `openai/gpt-oss-120b` | Model identifier on the Groq API |
| `GROQ_TPM_LIMIT` | ❌ | `8000` | Groq tokens-per-minute hard limit |
| `GROQ_SAFE_TPM_LIMIT` | ❌ | `6500` | Safety margin for the built-in rate limiter |
| `GROQ_MAX_OUTPUT_TOKENS` | ❌ | `1200` | Maximum tokens per LLM response |
| `GROQ_RESERVED_OUTPUT_TOKENS` | ❌ | `800` | Output tokens reserved when estimating request size |
| `GITHUB_TOKEN` | ❌ | — | GitHub personal access token (for private repos or higher rate limits) |
| `SECRET_KEY` | ✅ | insecure dev key | Django secret key |
| `DEBUG` | ❌ | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | ❌ | `127.0.0.1,localhost` | Comma-separated list of allowed hosts |

**Example `.env`:**
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=openai/gpt-oss-120b

```

---

## API Reference

All endpoints are prefixed with `/api/reviews/`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reviews/` | List all reviews (ordered by newest first) |
| `POST` | `/api/reviews/` | Create and run a new code review |
| `GET` | `/api/reviews/{id}/` | Retrieve a single review with all findings |
| `PUT` | `/api/reviews/{id}/` | Update a review |
| `DELETE` | `/api/reviews/{id}/` | Delete a review |
| `POST` | `/api/reviews/{id}/retry/` | Re-run a failed or completed review |

### POST `/api/reviews/` — Request Body

```json
{
  "code": "// your source code here",
  "repository_url": "https://github.com/user/repo",
  "requirements": "This app should authenticate users securely...",
  "language": "TypeScript"
}
```

- `code` and `repository_url` are mutually exclusive. Provide one or the other.
- `requirements` is optional. A generic best-practices prompt is used if omitted.
- `language` is optional. Auto-detected from file extensions when a repository URL is provided.

### Response Shape

```json
{
  "id": 26,
  "status": "completed",
  "language": "TypeScript",
  "repository_url": "https://github.com/user/repo",
  "requirements": "...",
  "final_report": {
    "overall_summary": "...",
    "risk_level": "high",
    "priority_actions": ["...", "..."],
    "severity_summary": { "critical": 1, "high": 3, "medium": 4, "low": 2, "info": 0 },
    "recommendations": [{ "id": 1, "action": "...", "priority": "high", "reason": "..." }]
  },
  "findings": [
    {
      "id": 1,
      "title": "SQL Injection Risk",
      "severity": "critical",
      "category": "security",
      "file_path": "src/db/queries.ts",
      "line_number": 42,
      "evidence": "db.query(`SELECT * FROM users WHERE id = ${userId}`)",
      "explanation": "User input is interpolated directly into a raw SQL query...",
      "suggested_fix": "Use parameterised queries: db.query('SELECT * FROM users WHERE id = $1', [userId])",
      "confidence": 0.97,
      "verification_status": "verified",
      "verification_reason": "Confirmed: no sanitisation occurs before the query is executed."
    }
  ],
  "trajectories": [],
  "created_at": "2026-09-09T21:00:00Z",
  "started_at": "2026-09-09T21:00:01Z",
  "completed_at": "2026-09-09T21:03:45Z",
  "error_message": null
}
```

---

## Data Models

### `Review`
| Field | Type | Description |
|---|---|---|
| `id` | int | Auto-generated primary key |
| `repository_url` | URL (nullable) | Optional GitHub repository URL |
| `code` | text | Full source code under review |
| `requirements` | text | User-supplied requirements / intent |
| `language` | str | Detected or supplied programming language |
| `status` | enum | `pending` · `running` · `completed` · `failed` |
| `final_report` | JSON | Structured summary from the Summary Agent |
| `error_message` | text | Human-readable failure message if status is `failed` |
| `created_at` | datetime | When the review was submitted |
| `started_at` | datetime | When the agent pipeline began |
| `completed_at` | datetime | When the pipeline finished |

### `Finding`
| Field | Type | Description |
|---|---|---|
| `review` | FK → Review | Parent review |
| `title` | str | Short description of the finding |
| `severity` | enum | `critical` · `high` · `medium` · `low` · `info` |
| `category` | str | `security` · `correctness` · `performance` · etc. |
| `file_path` | str | File the finding relates to |
| `line_number` | int (nullable) | Line number if known |
| `evidence` | text | Relevant code excerpt |
| `explanation` | text | Detailed description of the problem |
| `suggested_fix` | text | Recommended remediation |
| `confidence` | float | Agent confidence score (0.0 – 1.0) |
| `verification_status` | enum | `pending` · `verified` · `rejected` |
| `verification_reason` | text | Why the verifier accepted or rejected the finding |

### `AgentTrajectory`
| Field | Type | Description |
|---|---|---|
| `review` | FK → Review | Parent review |
| `agent_name` | str | Name of the agent that ran this step |
| `step` | int | Execution order within the pipeline |
| `input_data` | JSON | Data sent to the agent |
| `output_data` | JSON | Data returned by the agent |
| `status` | enum | `started` · `completed` · `failed` |
| `error_message` | text | Error detail if the step failed |

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| Django | 6.1 | Web framework |
| Django REST Framework | 3.18 | REST API |
| django-jazzmin | 3.0 | Admin UI theme |
| django-cors-headers | 4.9 | CORS support |
| Pydantic | 2.13 | Schema validation for agent outputs |
| openai (SDK) | latest | Groq API client (OpenAI-compatible) |
| python-dotenv | 1.2 | Environment variable loading |
| SQLite | — | Default development database |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 6 | Type safety |
| Vite | 8 | Build tool & dev server |
| Tailwind CSS | 4 | Utility-first styling |
| DaisyUI | 5 | Component library |
| Framer Motion | 13 | Animations |
| React Router | 7 | Client-side routing |
| react-icons | 5 | Icon library |

---

## Notes

- **Rate Limiting:** The Groq integration includes a built-in token-per-minute (TPM) rate limiter that automatically sleeps between requests to stay within the configured `GROQ_SAFE_TPM_LIMIT`. No external queue is required.
- **GitHub Integration:** When a `repository_url` is provided, the backend fetches source files via the GitHub API, respects per-file and total size caps, and auto-detects the dominant language from file extensions.
- **Chunking:** The `CodeChunker` respects file boundaries and attempts to keep chunks within the safe TPM budget so that no single request exceeds the Groq API limits.
- **Admin Panel:** All models are registered in Django Admin with the Jazzmin theme, enabling full CRUD access and review management at `/admin/`.
