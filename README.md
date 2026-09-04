# Arbiter

An AI-powered payment failure recovery agent that classifies Razorpay payment failures in real time, selects the optimal recovery action (retry, delay, suggest alternative method), and measures the revenue impact of the AI-driven approach vs. doing nothing.

Arbiter ingests live Razorpay webhooks, runs failures through a classification and recovery pipeline, and surfaces the results in a real-time dashboard so you can see exactly how much revenue the agent is saving.

## Architecture

```
Frontend (Next.js) <-> Backend (FastAPI) <-> Supabase (Postgres)
```

## Stack

| Layer    | Tech                                      |
|----------|-------------------------------------------|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS |
| Backend  | FastAPI (Python) + Uvicorn               |
| Database | PostgreSQL via Supabase                   |
| Webhooks | Razorpay webhook → FastAPI               |
| AI       | Anthropic Claude (coming soon)            |

## Local Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- A Supabase project (free tier works)

---

### 1. Clone and enter the repo

```bash
git clone <your-repo-url>
cd recovery-copilot
```

---

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill in env vars
cp .env.example .env
# Edit .env and fill in your real values

# Run the dev server
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/health  (should return {"status":"ok"})
```

---

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and fill in env vars
cp .env.local.example .env.local
# Edit .env.local if your backend runs on a different port

# Run the dev server
npm run dev
# → http://localhost:3000
```

---

### 4. Database

Apply the schema to your Supabase project:

1. Open your Supabase project → **SQL Editor**
2. Paste the contents of `backend/db/schema.sql`
3. Run — all four tables will be created

---

## Deployment (coming soon)

- **Frontend** → Vercel (connect the `frontend/` directory)
- **Backend** → Railway (connect the `backend/` directory, set env vars)
