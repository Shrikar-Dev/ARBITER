import re
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from db.client import get_supabase
from db.execution_store import get_action_execution
from models.failure_taxonomy import FAILURE_CATEGORIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def format_rupees(paise: int) -> str:
    rupees = (paise or 0) / 100
    return f"₹{rupees:,.0f}"

def format_action_label(action_type: str, delay_minutes: int = None) -> str:
    if not action_type or action_type == "no_action":
        return "No Action"
    if action_type == "retry_now":
        return "Retry Now"
    if action_type == "retry_delayed":
        if delay_minutes:
            if delay_minutes >= 60:
                hours = delay_minutes // 60
                return f"Retry Delayed ({hours}h)"
            return f"Retry Delayed ({delay_minutes}m)"
        return "Retry Delayed"
    if action_type == "suggest_alt_method":
        return "Suggest Alt Method"
    return action_type.replace("_", " ").title()

def parse_ai_rationale(raw_text: str):
    """Parses bundled AI rationale text into rationale, reasoning_notes, action_type, delay_minutes."""
    if not raw_text:
        return "", "", None, None

    notes_match = re.search(r"\[AI Nuance:\s*(.*?)\]", raw_text, re.DOTALL)
    action_match = re.search(r"\[Action:\s*(.*?)\s*\|\s*Delay:\s*(.*?)\]", raw_text)

    reasoning_notes = notes_match.group(1).strip() if notes_match else ""
    action_type = action_match.group(1).strip() if action_match else None
    
    delay_str = action_match.group(2).strip() if action_match else None
    delay_minutes = int(delay_str) if delay_str and delay_str != "None" else None

    # Clean main rationale
    main_rationale = raw_text.split("\n\n[AI Nuance:")[0].strip()

    return main_rationale, reasoning_notes, action_type, delay_minutes

@router.get("/summary")
async def get_dashboard_summary():
    """
    Returns high-level recovery metrics + AI comparison metrics:
    - revenue_recovered_with_agent
    - revenue_recovered_without_agent
    - total_events
    - events_by_category
    - ai_agreement_count
    - total_ai_classified
    """
    supabase = get_supabase()
    
    # 1. Total events count
    events_res = supabase.table("payment_events").select("id", count="exact").execute()
    total_events = events_res.count if events_res.count is not None else len(events_res.data or [])
    
    # 2. Events by category & AI agreement calculation
    class_res = supabase.table("failure_classifications").select("*").execute()
    all_classifications = class_res.data or []
    
    events_by_category = {}
    rules_by_event = {}
    ai_by_event = {}
    
    for row in all_classifications:
        cat = row["category"]
        c_by = row["classified_by"]
        e_id = row["payment_event_id"]
        
        if c_by == "rules_engine":
            events_by_category[cat] = events_by_category.get(cat, 0) + 1
            rules_by_event[e_id] = row
        elif c_by in ("ai_agent", "ai_fallback"):
            ai_by_event[e_id] = row
            
    ai_agreement_count = 0
    total_ai_classified = len(ai_by_event)
    
    for e_id, ai_row in ai_by_event.items():
        rules_row = rules_by_event.get(e_id)
        if rules_row:
            rules_cat = rules_row.get("category")
            rules_tax = FAILURE_CATEGORIES.get(rules_cat, {})
            rules_act = rules_tax.get("default_action")
            
            _, _, ai_act_type, _ = parse_ai_rationale(ai_row.get("rationale"))
            
            if ai_act_type and rules_act and ai_act_type == rules_act:
                ai_agreement_count += 1
            elif not ai_act_type and rules_cat == ai_row.get("category"):
                ai_agreement_count += 1
            
    # 3. Outcomes sum for revenue recovered with agent
    outcomes_res = supabase.table("outcomes").select("recovered, recovered_amount, recovery_actions(action_type)").execute()
    
    recovered_with_agent_paise = 0
    recovered_without_agent_paise = 0
    
    for row in (outcomes_res.data or []):
        if row.get("recovered"):
            amt = row.get("recovered_amount") or 0
            action_info = row.get("recovery_actions") or {}
            act_type = action_info.get("action_type") if isinstance(action_info, dict) else None
            
            if act_type and act_type != "no_action":
                recovered_with_agent_paise += amt
            else:
                recovered_without_agent_paise += amt
                
    return {
        "revenue_recovered_with_agent": recovered_with_agent_paise / 100,
        "revenue_recovered_without_agent": recovered_without_agent_paise / 100,
        "revenue_recovered_with_agent_formatted": format_rupees(recovered_with_agent_paise),
        "revenue_recovered_without_agent_formatted": format_rupees(recovered_without_agent_paise),
        "total_events": total_events,
        "events_by_category": events_by_category,
        "ai_agreement_count": ai_agreement_count,
        "total_ai_classified": total_ai_classified
    }

@router.get("/events")
async def get_dashboard_events():
    """
    Returns list of events joined with classifications, recovery actions, and outcomes.
    Includes execution status, Razorpay payment link URL, event_source.
    """
    supabase = get_supabase()
    
    events_res = supabase.table("payment_events").select(
        "*, failure_classifications(*), recovery_actions(*, outcomes(*))"
    ).order("created_at", desc=True).execute()
    
    raw_events = events_res.data or []
    formatted_list = []
    
    for item in raw_events:
        classifications = item.get("failure_classifications") or []
        
        rules_class = next((c for c in classifications if c.get("classified_by") == "rules_engine"), {})
        ai_class = next((c for c in classifications if c.get("classified_by") in ("ai_agent", "ai_fallback")), {})
        
        actions = item.get("recovery_actions") or []
        action = actions[0] if actions else {}
        action_id = action.get("id")
        
        if action_id:
            store_data = get_action_execution(action_id)
            if store_data:
                action = {**action, **store_data}
        
        outcomes = action.get("outcomes") or [] if action else []
        outcome = outcomes[0] if outcomes else {}
        
        action_type = action.get("action_type")
        delay_minutes = action.get("action_delay_minutes")
        
        # Rules engine payload
        rules_cat = rules_class.get("category")
        rules_tax = FAILURE_CATEGORIES.get(rules_cat, {})
        rules_action_type = rules_tax.get("default_action", action_type or "no_action")
        rules_delay = rules_tax.get("default_delay_minutes", delay_minutes)
        
        rules_payload = {
            "category": rules_cat or "unknown",
            "action": format_action_label(rules_action_type, rules_delay),
            "action_type": rules_action_type,
            "rationale": rules_class.get("rationale") or (rules_tax.get("rationale") if rules_tax else "Rules engine classification pending.")
        }
        
        # AI agent payload
        ai_payload = None
        agreement = True
        
        if ai_class:
            ai_main_rationale, ai_notes, ai_act_type, ai_delay = parse_ai_rationale(ai_class.get("rationale"))
            act_to_format = ai_act_type or rules_action_type
            delay_to_format = ai_delay if ai_delay is not None else rules_delay
            
            ai_payload = {
                "category": ai_class.get("category"),
                "action": format_action_label(act_to_format, delay_to_format),
                "action_type": act_to_format,
                "rationale": ai_main_rationale,
                "reasoning_notes": ai_notes or "Contextual nuances analyzed.",
                "confidence": ai_class.get("confidence", 0.90)
            }
            
            agreement = (rules_action_type == act_to_format)
            
        # Determine overall table status
        executed = action.get("executed", False)
        execution_err = action.get("execution_error")
        created_at_str = item.get("created_at")

        if execution_err:
            status = "failed"
            action_taken_str = format_action_label(action_type, delay_minutes)
        elif not action or not action_type:
            status = "pending"
            action_taken_str = "Pending Analysis"
        elif executed:
            action_taken_str = format_action_label(action_type, delay_minutes)
            if action_type == "no_action":
                status = "no action taken"
            elif outcome and outcome.get("recovered") is False:
                status = "failed"
            else:
                status = "recovered"
        else:
            action_taken_str = format_action_label(action_type, delay_minutes)
            if action_type == "no_action":
                status = "no action taken"
            elif action_type == "retry_delayed" and delay_minutes:
                is_due = False
                if created_at_str:
                    try:
                        created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        now_dt = datetime.now(timezone.utc)
                        elapsed_min = (now_dt - created_dt).total_seconds() / 60.0
                        if elapsed_min >= delay_minutes:
                            is_due = True
                    except Exception:
                        pass
                status = "pending" if is_due else "pending (delayed)"
            else:
                status = "pending"
                
        amount_paise = item.get("amount", 0)
        
        formatted_list.append({
            "id": item.get("id"),
            "razorpay_payment_id": item.get("razorpay_payment_id"),
            "time": item.get("created_at"),
            "amount": format_rupees(amount_paise),
            "amount_paise": amount_paise,
            "failure_reason": item.get("failure_description") or item.get("failure_reason_code") or "Unknown",
            "failure_reason_code": item.get("failure_reason_code"),
            "action_taken": action_taken_str,
            "action_type": action_type,
            "status": status,
            "customer_email": item.get("customer_email"),
            "customer_phone": item.get("customer_phone"),
            "event_source": item.get("event_source", "synthetic"),
            "executed": action.get("executed", False),
            "executed_at": action.get("executed_at"),
            "razorpay_payment_link_id": action.get("razorpay_payment_link_id"),
            "razorpay_payment_link_url": action.get("razorpay_short_url") or action.get("razorpay_payment_link_url"),
            "razorpay_short_url": action.get("razorpay_short_url") or action.get("razorpay_payment_link_url"),
            "execution_error": action.get("execution_error"),
            "rules_engine": rules_payload,
            "ai_agent": ai_payload,
            "agreement": agreement
        })
        
    return formatted_list
