import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.webhooks import router as webhooks_router
from routes.events import router as events_router
from routes.dashboard import router as dashboard_router
from routes.actions import router as actions_router

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Arbiter API",
    description="AI-powered payment failure recovery backend.",
    version="0.1.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server to hit the API.
# In production (Railway) you will restrict this to your Vercel domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(webhooks_router)
app.include_router(events_router)
app.include_router(dashboard_router)
app.include_router(actions_router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """Liveness probe. Returns 200 OK when the service is up."""
    return {"status": "ok"}
