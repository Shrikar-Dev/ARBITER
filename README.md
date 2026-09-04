# ⚡ ARBITER

> **Autonomous AI-Powered Payment Failure Recovery Engine**  
> Classifies payment failures using a side-by-side **Rules Engine** and **AI Reasoning Agent**, autonomously executes optimal recovery actions in Razorpay Test Mode, and tracks revenue recovery in real time.

---

## 🌐 Live Production Deployments

| Component | Service | URL |
|---|---|---|
| **Frontend Dashboard & Landing** | Vercel | Connected to GitHub (`Shrikar-Dev/ARBITER`) |
| **Backend API** | Render | `https://arbiter-07wj.onrender.com` |
| **API Documentation (Swagger)** | Render | `https://arbiter-07wj.onrender.com/docs` |
| **Database** | Supabase | PostgreSQL Engine |

---

## 🌟 Overview

**Arbiter** is an intelligent payment failure recovery system built to solve payment drops in e-commerce and subscription platforms. Instead of relying solely on static rules or blindly retrying every failed transaction, Arbiter evaluates every failed payment using both a **deterministic Rules Engine** and a **contextual AI Reasoning Agent** side-by-side.

When a payment fails (via live Razorpay Webhooks or synthetic events), Arbiter:
1. **Classifies the Failure**: Categorizes the root cause (e.g., bank gateway timeout, insufficient funds, authentication failure, network drop).
2. **Evaluates Recovery Strategy**: Compares static policy recommendations against AI contextual reasoning (nuance factors, customer history, time-of-day dynamics).
3. **Executes Autonomous Actions**: Triggers immediate retries, schedules delayed retries, or generates live **Razorpay Payment Links** (`https://rzp.io/rzp/...`) in Razorpay Test Mode.
4. **Measures Revenue Recovery**: Calculates exact revenue recovered with Arbiter vs. a zero-recovery baseline.

---

## ✨ Key Features

- **Dual-Engine Side-by-Side Evaluation**: Compare static Rules Engine policies directly against AI Agent reasoning with confidence scores and "AI Nuance" callouts.
- **Autonomous Razorpay Integration**: Direct integration with Razorpay REST API for live payment link creation and payment status tracking.
- **Real-Time Webhook Handler**: Ingests `payment.failed` webhooks from Razorpay with HMAC SHA256 signature verification.
- **Delayed Retry Scheduler**: Manages delayed recovery actions and executes due actions via cron or manual triggers (`POST /actions/process-due`).
- **Glassmorphic Pitch-Black UI**: Custom dark glassmorphic dashboard built with Next.js 15, Tailwind CSS, and custom typography (**ARBITER** brand title in *Kola*, dashboard in *Nippo*).

---

## 🛠️ Architecture & Tech Stack

```
                               ┌─────────────────────────┐
                               │   Razorpay Webhooks /   │
                               │     Synthetic Events    │
                               └────────────┬────────────┘
                                            │
                                            ▼
┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│   Vercel Next.js 15    │ ──── │     Render FastAPI      │ ──── │  Supabase PostgreSQL   │
│ (Glassmorphic + Nippo) │      │  (Python + Uvicorn)     │      │   + Execution Store    │
└────────────────────────┘      └────────────┬────────────┘      └────────────────────────┘
                                             │
                                ┌────────────┴────────────┐
                                │   AI Reasoning Agent    │
                                │ (Google Gemini / Claude)│
                                └─────────────────────────┘
```

| Layer | Technology |
|---|---|
| **Frontend Host** | Vercel (Next.js 15 App Router, TypeScript, Tailwind CSS) |
| **Backend Host** | Render (FastAPI Python 3.11+, Uvicorn, Pydantic) |
| **Database** | PostgreSQL via Supabase + Local JSON Execution Store Fallback |
| **Payments** | Razorpay REST API (Payment Links & Webhooks) |
| **AI Agent** | Google Gemini API / Anthropic Claude API |

---

## 🚀 Getting Started (Local Development)

### Prerequisites

- **Node.js** 18+ & **npm**
- **Python** 3.11+
- **Razorpay** Test Account Key ID & Secret (`rzp_test_...`)
- **Supabase** Database URL & Service Role Key

---

### 1. Environment Setup

#### Backend (`backend/.env`)
Copy `backend/.env.example` to `backend/.env`:
```env
# Razorpay Test Credentials
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxx

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# AI Provider
GEMINI_API_KEY=your_gemini_api_key
```

#### Frontend (`frontend/.env.local`)
Copy `frontend/.env.local.example` to `frontend/.env.local`:
```env
# Production: Point to live Render backend
NEXT_PUBLIC_API_URL=https://arbiter-07wj.onrender.com

# Supabase Public Keys
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxxxxxxx
```

---

### 2. Backend Installation & Run

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available locally at `http://localhost:8000/docs`.

---

### 3. Frontend Installation & Run

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```
Dashboard will be live at `http://localhost:3000/dashboard` and Landing Page at `http://localhost:3000`.

---

### 4. Database Setup

1. Open your Supabase Project -> **SQL Editor**.
2. Run the script in `backend/db/schema.sql` to create `payment_events`, `rules_evaluations`, `ai_evaluations`, and `recovery_actions` tables.

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/summary` | Get total revenue recovered (with vs. without agent) and AI alignment counts |
| `GET` | `/dashboard/events` | Get all payment events merged with execution store details |
| `POST` | `/events/process-ai` | Run AI Reasoning Agent evaluation on unclassified events |
| `POST` | `/actions/execute-pending` | Execute pending actions (e.g. create Razorpay payment links) |
| `POST` | `/actions/process-due` | Execute due delayed actions (use `?force=true` for instant force) |
| `POST` | `/webhooks/razorpay` | Handle live Razorpay `payment.failed` webhooks |

---

## 🛡️ License

MIT License. Designed and developed for **ARBITER**.
