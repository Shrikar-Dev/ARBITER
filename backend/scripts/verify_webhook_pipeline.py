import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.client import get_supabase
from routes.dashboard import parse_ai_rationale

def verify_webhook_pipeline():
    supabase = get_supabase()
    
    # 1. Fetch payment_event where event_source = 'razorpay_webhook'
    events_res = supabase.table("payment_events").select("*").eq("event_source", "razorpay_webhook").order("created_at", desc=True).limit(1).execute()
    events = events_res.data or []
    
    if not events:
        print("[WARNING] No payment_event found with event_source = 'razorpay_webhook'!")
        print("\nPipeline verification: NEEDS REVIEW - see warnings above")
        return
        
    event = events[0]
    event_id = event["id"]
    pay_id = event.get("razorpay_payment_id")
    
    print(f"--- Pipeline Verification for Webhook Event {pay_id} ({event_id}) ---")
    print(f"Amount:              RS {(event.get('amount') or 0)/100:,.2f}")
    print(f"Failure Reason Code: {event.get('failure_reason_code')}")
    print(f"Failure Description: {event.get('failure_description')}")
    print("----------------------------------------------------------------------")
    
    warnings = []
    
    # 2. Fetch failure_classifications
    class_res = supabase.table("failure_classifications").select("*").eq("payment_event_id", event_id).execute()
    classifications = class_res.data or []
    
    if len(classifications) < 2:
        warnings.append(f"[WARNING] Expected 2 classification rows (rules + AI), found {len(classifications)}!")
        
    rules_class = next((c for c in classifications if c.get("classified_by") == "rules_engine"), {})
    ai_class = next((c for c in classifications if c.get("classified_by") in ("ai_agent", "ai_fallback")), {})
    
    if not rules_class:
        warnings.append("[WARNING] Missing rules_engine classification row!")
    else:
        print("\n[Rules Engine Classification]")
        print(f"  Category:     {rules_class.get('category')}")
        print(f"  Classified By:{rules_class.get('classified_by')}")
        print(f"  Rationale:    {rules_class.get('rationale')}")
        
    if not ai_class:
        warnings.append("[WARNING] Missing AI agent classification row!")
    else:
        c_by = ai_class.get("classified_by")
        print("\n[AI Agent Classification]")
        print(f"  Category:     {ai_class.get('category')}")
        print(f"  Classified By:{c_by}")
        print(f"  Confidence:   {ai_class.get('confidence')}")
        
        main_rat, notes, act_type, delay = parse_ai_rationale(ai_class.get("rationale"))
        safe_rat = main_rat.encode('ascii', 'replace').decode()
        safe_notes = notes.encode('ascii', 'replace').decode() if notes else ""
        print(f"  Rationale:    {safe_rat}")
        if safe_notes:
            print(f"  Nuance Notes: {safe_notes}")
        if act_type:
            print(f"  AI Recommended Action: {act_type} (delay: {delay})")
            
        if c_by == "ai_fallback":
            warnings.append("[WARNING] AI classification used 'ai_fallback' (Gemini API call failed silently)!")
            
    # 3. Fetch recovery_actions
    action_res = supabase.table("recovery_actions").select("*").eq("payment_event_id", event_id).execute()
    actions = action_res.data or []
    
    if not actions:
        warnings.append("[WARNING] No recovery_actions row found for this event!")
    else:
        action = actions[0]
        print("\n[Recovery Action]")
        print(f"  Action Type:  {action.get('action_type')}")
        print(f"  Delay (min):  {action.get('action_delay_minutes')}")
        print(f"  Executed:     {action.get('executed')}")
        print(f"  Executed At:  {action.get('executed_at')}")
        print(f"  Payment Link: {action.get('razorpay_payment_link_url') or action.get('razorpay_payment_link_id') or 'N/A'}")
        
    print("----------------------------------------------------------------------")
    
    if warnings:
        print("\nWarnings Flagged:")
        for w in warnings:
            print(f"  {w}")
        print("\nPipeline verification: NEEDS REVIEW - see warnings above")
    else:
        print("\nPipeline verification: PASS")

if __name__ == "__main__":
    verify_webhook_pipeline()
