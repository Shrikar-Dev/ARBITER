from fastapi import APIRouter
from services.event_processor import process_pending_events
from services.ai_event_processor import process_pending_events_with_ai
from services.outcome_simulator import simulate_outcomes

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/process")
async def trigger_process_events():
    """Triggers the deterministic classification and recovery decision pipeline for pending events."""
    return process_pending_events()

@router.post("/process-ai")
async def trigger_process_ai():
    """Triggers Gemini AI classification and contextual rationale generation alongside rules engine."""
    return process_pending_events_with_ai()

@router.post("/simulate-outcomes")
async def trigger_simulate_outcomes():
    """Simulates recovery outcomes (success/failure probabilities) for decided recovery actions."""
    return simulate_outcomes()
