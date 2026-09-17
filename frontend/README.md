# CodeReview AI — Frontend

The React + TypeScript frontend for [CodeReview AI](../README.md). Provides a polished, interactive UI for submitting code reviews, tracking multi-agent pipeline progress, and exploring structured findings.

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 6 | Type safety |
| Vite | 8 | Build tool & dev server |
| Tailwind CSS | 4 | Utility-first styling |
| DaisyUI | 5 | Component library |
| Framer Motion | 13 | Animations & transitions |
| React Router | 7 | Client-side routing |
| react-icons | 5 | Icon library |

---

## Project Structure

```
src/
├── pages/
│   ├── Home.tsx           # Landing page with review history list
│   ├── NewReview.tsx      # Review submission page
│   ├── ReviewResults.tsx  # Detailed results view with findings
│   └── Evaluation.tsx     # Evaluation / pipeline metrics page
│
├── components/
│   ├── Navbar.tsx         # Top navigation bar
│   ├── ReviewForm.tsx     # Code & repository submission form
│   ├── FindingCard.tsx    # Individual finding card display
│   ├── SeverityBadge.tsx  # Colour-coded severity badge
│   ├── AgentProgress.tsx  # Live agent step progress indicator
│   └── AgentTrajectory.tsx# Step-by-step agent trace viewer
│
├── services/
│   └── api.ts             # API client (fetch wrappers for the Django backend)
│
├── types/                 # Shared TypeScript interfaces
├── App.tsx                # Router setup & layout shell
└── main.tsx               # React entry point
```

---

## Routes

| Path | Page | Description |
|---|---|---|
| `/` | `Home` | Lists all past reviews with status and quick stats |
| `/new` | `NewReview` | Submit code or a GitHub repo URL for review |
| `/review/:id` | `ReviewResults` | Full review detail: findings, summary, agent trace |
| `/evaluation` | `Evaluation` | Pipeline evaluation metrics |

---

## Getting Started

### Prerequisites
- Node.js 18+
- The Django backend running at `http://127.0.0.1:8000/` (see [backend setup](../README.md#backend-setup))

### Installation

```bash
# From the project root
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173/`.

> **Proxy:** The Vite dev server proxies all `/api` requests to `http://127.0.0.1:8000`, so you don't need to configure CORS or change API URLs during development.

### Other Scripts

```bash
# Type-check & build for production
npm run build

# Preview the production build locally
npm run preview

# Run ESLint
npm run lint
```

---

## Environment Variables

For production deployments (e.g. Vercel), set the following environment variable:

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the deployed Django backend (e.g. `https://your-backend.onrender.com`) |

When `VITE_API_URL` is not set, the API client defaults to relative paths (works with the Vite dev proxy).

---

## Deployment

This frontend is deployed on **Vercel**. The `vercel.json` at the project root rewrites all routes to `index.html` to support client-side routing with React Router.

```json
// vercel.json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

To deploy:
1. Connect your GitHub repository to Vercel.
2. Set the **Root Directory** to `frontend`.
3. Add the `VITE_API_URL` environment variable pointing to your Render backend.
4. Deploy — Vercel will run `npm run build` automatically.
