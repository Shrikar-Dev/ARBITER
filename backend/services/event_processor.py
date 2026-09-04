import logging
from db.client import get_supabase
from services.policy_engine import classify_and_decide

logger = logging.getLogger(__name__)

def process_pending_events() -> dict:
    """
    1. Fetch all payment_events that don't yet have a failure_classifications record.
    2. For each one, call classify_and_decide() from policy_engine.py.
    3. Insert the result into failure_classifications table.
    4. Based on the action_type returned, insert a corresponding record into recovery_actions table.
    5. Return a summary of processed events.
    """
    supabase = get_supabase()
    
    # 1. Get already classified event IDs
    classified_res = supabase.table("failure_classifications").select("payment_event_id").execute()
    classified_event_ids = {row["payment_event_id"] for row in (classified_res.data or [])}
    
    # 2. Fetch all payment_events
    events_res = supabase.table("payment_events").select("*").execute()
    all_events = events_res.data or []
    
    # Filter pending events
    pending_events = [e for e in all_events if e["id"] not in classified_event_ids]
    
    if not pending_events:
        return {
            "status": "success",
            "message": "No pending events to process",
            "processed_count": 0,
            "category_breakdown": {}
        }
    
    processed_count = 0
    category_breakdown = {}
    
    for event in pending_events:
        event_id = event["id"]
        decision = classify_and_decide(event)
        
        category = decision["category"]
        category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Insert into failure_classifications
        class_res = supabase.table("failure_classifications").insert({
            "payment_event_id": event_id,
            "category": category,
            "confidence": decision["confidence"],
            "rationale": decision["rationale"],
            "classified_by": decision["classified_by"]
        }).execute()
        
        if not class_res.data:
            logger.error(f"Failed to insert failure_classification for event {event_id}")
            continue
            
        classification_id = class_res.data[0]["id"]
        
        # Insert into recovery_actions
        supabase.table("recovery_actions").insert({
            "payment_event_id": event_id,
            "classification_id": classification_id,
            "action_type": decision["action_type"],
            "action_delay_minutes": decision["action_delay_minutes"],
            "executed": False
        }).execute()
        
        processed_count += 1
        
    return {
        "status": "success",
        "processed_count": processed_count,
        "category_breakdown": category_breakdown
    }
