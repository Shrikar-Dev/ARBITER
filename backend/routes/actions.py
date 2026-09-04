from fastapi import APIRouter, HTTPException
from db.client import get_supabase
from services.action_executor import execute_recovery_action
from services.action_scheduler import execute_pending_actions, process_due_delayed_actions

router = APIRouter(prefix="/actions", tags=["actions"])

@router.post("/execute-pending")
async def trigger_execute_pending():
    """Executes all immediate (non-delayed) pending recovery actions in Razorpay test mode."""
    return execute_pending_actions()

@router.post("/process-due")
async def trigger_process_due(force: bool = False):
    """
    Executes all delayed recovery actions whose scheduled delay has passed.
    Pass ?force=true to bypass the delay check for testing/demo purposes.
    """
    return process_due_delayed_actions(force=force)

@router.post("/execute/{recovery_action_id}")
async def trigger_execute_single_action(recovery_action_id: str):
    """
    Fetches a single recovery_action + its linked payment_event,
    calls execute_recovery_action(), and returns the dict result.
    """
    supabase = get_supabase()
    res = supabase.table("recovery_actions").select("*, payment_events(*)").eq("id", recovery_action_id).execute()
    data = res.data or []
    if not data:
        raise HTTPException(status_code=404, detail=f"Recovery action {recovery_action_id} not found")
        
    action_row = data[0]
    payment_event = action_row.get("payment_events") or {}
    
    return execute_recovery_action(action_row, payment_event)
