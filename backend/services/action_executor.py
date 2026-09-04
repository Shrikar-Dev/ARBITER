import logging
from datetime import datetime, timezone
from db.client import get_supabase
from db.execution_store import update_action_execution
from services.razorpay_client import create_payment_link

logger = logging.getLogger(__name__)

def execute_recovery_action(recovery_action: dict, payment_event: dict) -> dict:
    """
    Takes a recovery_action row (action_type, action_delay_minutes, executed=false)
    and a payment_event row, and executes it in Razorpay test mode.

    - retry_now / retry_delayed: create a real payment link immediately via create_payment_link().
    - suggest_alt_method: create_payment_link() tagged as alt method.
    - no_action: do nothing external, mark executed=true, executed_at=now.

    On success: update recovery_actions row -> executed=true, executed_at=now,
      razorpay_payment_link_id, razorpay_short_url
    On failure: update recovery_actions row -> executed=false, execution_error

    Returns {"action_type": ..., "success": bool, "link_url": str or None, "error": str or None}.
    """
    supabase = get_supabase()
    action_id = recovery_action["id"]
    action_type = recovery_action.get("action_type", "no_action")
    
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Handle no_action
    if action_type == "no_action":
        update_data = {
            "executed": True,
            "executed_at": now_iso,
            "razorpay_payment_link_id": None,
            "razorpay_short_url": None,
            "execution_error": None
        }
        try:
            supabase.table("recovery_actions").update(update_data).eq("id", action_id).execute()
        except Exception as e:
            logger.warning(f"Update failed ({e}), falling back to base update.")
            supabase.table("recovery_actions").update({
                "executed": True,
                "executed_at": now_iso
            }).eq("id", action_id).execute()
            
        return {
            "action_type": action_type,
            "success": True,
            "link_url": None,
            "error": None
        }
        
    # 2. Handle retry_now, retry_delayed, suggest_alt_method
    amount = payment_event.get("amount", 10000)
    email = payment_event.get("customer_email") or "customer@example.com"
    phone = payment_event.get("customer_phone") or "+919876543210"
    reason = payment_event.get("failure_description") or payment_event.get("failure_reason_code") or "Payment failure"
    
    if action_type == "suggest_alt_method":
        description = f"Alternative payment method suggested — {reason}"
    else:
        description = f"Payment retry for order — {reason}"
        
    res = create_payment_link(
        amount_paise=amount,
        customer_email=email,
        customer_phone=phone,
        description=description
    )
    
    if res.get("success"):
        link_id = res.get("link_id")
        short_url = res.get("short_url")
        
        update_data = {
            "executed": True,
            "executed_at": now_iso,
            "razorpay_payment_link_id": link_id,
            "razorpay_short_url": short_url,
            "execution_error": None
        }
        
        update_action_execution(action_id, update_data)
        
        try:
            supabase.table("recovery_actions").update(update_data).eq("id", action_id).execute()
        except Exception as e:
            logger.warning(f"Full update failed ({e}), falling back to base update.")
            supabase.table("recovery_actions").update({
                "executed": True,
                "executed_at": now_iso
            }).eq("id", action_id).execute()
            
        return {
            "action_type": action_type,
            "success": True,
            "link_url": short_url,
            "error": None
        }
    else:
        err_msg = res.get("error", "Unknown Razorpay error")
        update_data = {
            "executed": False,
            "execution_error": err_msg
        }
        
        update_action_execution(action_id, update_data)
        
        try:
            supabase.table("recovery_actions").update(update_data).eq("id", action_id).execute()
        except Exception:
            pass
            
        return {
            "action_type": action_type,
            "success": False,
            "link_url": None,
            "error": err_msg
        }
