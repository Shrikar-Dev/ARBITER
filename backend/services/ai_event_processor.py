import time
import logging
from db.client import get_supabase
from services.ai_classifier import classify_with_ai

logger = logging.getLogger(__name__)

def process_pending_events_with_ai() -> dict:
    """
    1. Fetch payment_events that have a rules_engine classification but NOT yet an ai_agent classification.
    2. For each, call classify_with_ai().
    3. Insert into failure_classifications with classified_by='ai_agent' immediately.
    4. Sleep 0.2s between calls.
    5. Return summary metrics.
    """
    supabase = get_supabase()

    # 1. Get all failure_classifications
    all_class_res = supabase.table("failure_classifications").select("*").execute()
    all_classifications = all_class_res.data or []

    rules_by_event = {}
    ai_classified_event_ids = set()

    for c in all_classifications:
        event_id = c["payment_event_id"]
        if c["classified_by"] == "rules_engine":
            rules_by_event[event_id] = c
        elif c["classified_by"] in ("ai_agent", "ai_fallback"):
            ai_classified_event_ids.add(event_id)

    # 2. Get payment_events that have rules_engine classification but no ai_agent classification
    target_event_ids = set(rules_by_event.keys()) - ai_classified_event_ids
    if not target_event_ids:
        return {
            "status": "success",
            "message": "No pending events requiring AI classification",
            "processed_count": 0,
            "avg_confidence": 0.0,
            "agreed_count": 0,
            "disagreed_count": 0,
            "fallback_count": 0
        }

    # Fetch details for target events
    events_res = supabase.table("payment_events").select("*").execute()
    all_events = events_res.data or []
    target_events = [e for e in all_events if e["id"] in target_event_ids]

    processed_count = 0
    total_confidence = 0.0
    agreed_count = 0
    disagreed_count = 0
    fallback_count = 0

    for idx, event in enumerate(target_events):
        event_id = event["id"]
        rules_class = rules_by_event.get(event_id, {})
        rules_cat = rules_class.get("category")

        # Call AI classifier
        ai_res = classify_with_ai(event, rules_engine_category=rules_cat)

        classified_by = ai_res.get("classified_by", "ai_agent")
        if classified_by == "ai_fallback":
            fallback_count += 1

        category = ai_res.get("category", "unknown")
        confidence = float(ai_res.get("confidence", 0.0))
        total_confidence += confidence

        # Check agreement with rules engine
        rules_cat = rules_class.get("category")
        if category == rules_cat:
            agreed_count += 1
        else:
            disagreed_count += 1

        # Format rationale string to bundle rationale + reasoning_notes + recommended_action
        rationale_text = ai_res.get("rationale", "")
        reasoning_notes = ai_res.get("reasoning_notes", "")
        recommended_action = ai_res.get("recommended_action", "retry_now")
        recommended_delay = ai_res.get("recommended_delay_minutes")

        full_rationale = f"{rationale_text}\n\n[AI Nuance: {reasoning_notes}]\n[Action: {recommended_action} | Delay: {recommended_delay}]"

        # Insert immediately into failure_classifications
        supabase.table("failure_classifications").insert({
            "payment_event_id": event_id,
            "category": category,
            "confidence": confidence,
            "rationale": full_rationale,
            "classified_by": classified_by
        }).execute()

        processed_count += 1

        if idx < len(target_events) - 1:
            time.sleep(0.2)

    avg_confidence = (total_confidence / processed_count) if processed_count > 0 else 0.0

    return {
        "status": "success",
        "processed_count": processed_count,
        "avg_confidence": round(avg_confidence, 2),
        "agreed_count": agreed_count,
        "disagreed_count": disagreed_count,
        "fallback_count": fallback_count
    }
