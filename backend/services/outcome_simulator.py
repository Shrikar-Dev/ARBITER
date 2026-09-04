import random
import logging
from datetime import datetime, timezone
from db.client import get_supabase

logger = logging.getLogger(__name__)

# Success probabilities for deterministic outcome simulation
# NOTE: This simulates what WOULD happen if recovery actions were executed.
# In Block 4, part of this will be replaced with real Razorpay test-mode actions.
ACTION_SUCCESS_PROBABILITIES = {
    "retry_now": 0.70,
    "retry_delayed": 0.55,
    "suggest_alt_method": 0.45,
    "no_action": 0.00
}

def simulate_outcomes() -> dict:
    """
    For every recovery_action that doesn't yet have an outcome record:
    - Determine success/failure based on action_type probability rules.
    - Insert result into outcomes table.
    """
    supabase = get_supabase()
    
    # 1. Fetch already simulated recovery_action_ids
    existing_outcomes_res = supabase.table("outcomes").select("recovery_action_id").execute()
    simulated_action_ids = {row["recovery_action_id"] for row in (existing_outcomes_res.data or [])}
    
    # 2. Fetch all recovery_actions with joined payment_events for amount
    actions_res = supabase.table("recovery_actions").select("*, payment_events(amount)").execute()
    all_actions = actions_res.data or []
    
    # Filter pending actions that haven't been simulated yet
    pending_actions = [a for a in all_actions if a["id"] not in simulated_action_ids]
    
    if not pending_actions:
        return {
            "status": "success",
            "message": "No pending recovery actions to simulate",
            "simulated_count": 0,
            "recovered_count": 0,
            "failed_count": 0,
            "total_recovered_amount_paise": 0
        }
        
    simulated_count = 0
    recovered_count = 0
    failed_count = 0
    total_recovered_amount = 0
    
    outcomes_to_insert = []
    
    for action in pending_actions:
        action_id = action["id"]
        action_type = action["action_type"]
        payment_event = action.get("payment_events") or {}
        event_amount = payment_event.get("amount", 0)
        
        prob = ACTION_SUCCESS_PROBABILITIES.get(action_type, 0.0)
        is_recovered = random.random() < prob
        
        now_iso = datetime.now(timezone.utc).isoformat()
        
        if is_recovered:
            recovered_count += 1
            total_recovered_amount += event_amount
            outcomes_to_insert.append({
                "recovery_action_id": action_id,
                "recovered": True,
                "recovered_amount": event_amount,
                "recovered_at": now_iso
            })
        else:
            failed_count += 1
            outcomes_to_insert.append({
                "recovery_action_id": action_id,
                "recovered": False,
                "recovered_amount": None,
                "recovered_at": None
            })
            
        simulated_count += 1
        
    if outcomes_to_insert:
        supabase.table("outcomes").insert(outcomes_to_insert).execute()
        
    return {
        "status": "success",
        "simulated_count": simulated_count,
        "recovered_count": recovered_count,
        "failed_count": failed_count,
        "total_recovered_amount_paise": total_recovered_amount,
        "total_recovered_amount_rupees": total_recovered_amount / 100
    }
