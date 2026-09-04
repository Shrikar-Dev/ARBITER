import time
import logging
from datetime import datetime, timezone
from db.client import get_supabase
from services.action_executor import execute_recovery_action

logger = logging.getLogger(__name__)

def get_due_delayed_actions(force: bool = False) -> list:
    """
    Query recovery_actions where:
    - executed = false
    - action_type = 'retry_delayed'
    - action_delay_minutes IS NOT NULL

    If force is False:
      Filters in Python for rows where (now - created_at).total_seconds() / 60 >= action_delay_minutes
    If force is True:
      Ignores the time delay check for testing/demo purposes.
    """
    supabase = get_supabase()
    now = datetime.now(timezone.utc)

    # Fetch executed=false, action_type='retry_delayed' joined with payment_events
    res = supabase.table("recovery_actions").select("*, payment_events(*)").eq("executed", False).eq("action_type", "retry_delayed").execute()
    actions = res.data or []

    due_list = []
    for act in actions:
        delay = act.get("action_delay_minutes")
        if delay is None:
            continue

        if force:
            # FOR DEMO/TESTING ONLY: bypass delay check if force=True
            due_list.append(act)
            continue

        created_str = act.get("created_at")
        if not created_str:
            continue

        try:
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            elapsed_minutes = (now - created_at).total_seconds() / 60.0
            if elapsed_minutes >= float(delay):
                due_list.append(act)
        except Exception as e:
            logger.warning(f"Error parsing created_at for action {act.get('id')}: {e}")
            due_list.append(act)

    return due_list

def process_due_delayed_actions(force: bool = False) -> dict:
    """
    1. Call get_due_delayed_actions(force=force)
    2. For each due action, call execute_recovery_action(action, payment_event)
    3. Collect results
    4. Return summary: {"checked": <count due>, "executed": <count success>, "failed": <count error>}
    """
    due_actions = get_due_delayed_actions(force=force)
    
    executed_count = 0
    failed_count = 0
    
    for idx, act in enumerate(due_actions):
        payment_event = act.get("payment_events") or {}
        res = execute_recovery_action(act, payment_event)
        
        if res.get("success"):
            executed_count += 1
        else:
            failed_count += 1
            
        if idx < len(due_actions) - 1:
            time.sleep(1.0)
            
    return {
        "checked": len(due_actions),
        "executed": executed_count,
        "failed": failed_count
    }

def execute_pending_actions() -> dict:
    """
    Executes all recovery_actions where executed=false and (action_delay_minutes is null or 0).
    Adds timing info (duration_seconds).
    """
    start_time = time.time()
    supabase = get_supabase()
    
    actions_res = supabase.table("recovery_actions").select("*, payment_events(*)").eq("executed", False).execute()
    actions = actions_res.data or []
    
    # Filter immediate / non-delayed actions
    pending = [a for a in actions if not a.get("action_delay_minutes")]
    
    executed_count = 0
    failed_count = 0
    results = []
    
    for idx, act in enumerate(pending):
        event = act.get("payment_events") or {}
        res = execute_recovery_action(act, event)
        if res.get("success"):
            executed_count += 1
        else:
            failed_count += 1
        results.append(res)
        if idx < len(pending) - 1:
            time.sleep(2.0)
        
    duration = round(time.time() - start_time, 2)
    return {
        "attempted": len(pending),
        "succeeded": executed_count,
        "failed": failed_count,
        "duration_seconds": duration,
        "details": results
    }
