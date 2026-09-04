import os
import sys
import time
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.client import get_supabase
from services.razorpay_client import fetch_payment_link

def verify_forced_execution():
    time.sleep(2)
    supabase = get_supabase()
    event_id = "2c1b3903-0d9e-436c-9c20-7ffda87bc980"
    
    print("--- PRE-STEP: Resetting executed=False for RS 9,381 delayed action ---")
    supabase.table("recovery_actions").update({"executed": False, "executed_at": None}).eq("payment_event_id", event_id).execute()
    
    print("--- TASK 1: Triggering POST /actions/process-due?force=true ---")
    url = "http://localhost:8000/actions/process-due?force=true"
    
    try:
        r = httpx.post(url, timeout=60.0)
        print("HTTP Status Code:", r.status_code)
        print("Raw Response Output:")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"[FAIL] HTTP POST request failed: {e}")
        print("\nForce-execution verification: NEEDS REVIEW")
        return

    print("\n--- TASK 2: Querying recovery_actions for RS 9,381 event ---")
    supabase = get_supabase()
    
    # Event ID for pay_test_12664416 (amount 938100)
    event_id = "2c1b3903-0d9e-436c-9c20-7ffda87bc980"
    res = supabase.table("recovery_actions").select("*").eq("payment_event_id", event_id).execute()
    actions = res.data or []
    
    if not actions:
        print("[WARNING] No recovery_actions row found for RS 9,381 event!")
        print("\nForce-execution verification: NEEDS REVIEW")
        return
        
    act = actions[0]
    from db.execution_store import get_action_execution
    store_data = get_action_execution(act.get("id"))
    executed = act.get("executed") if act.get("executed") is not None else store_data.get("executed")
    executed_at = act.get("executed_at") or store_data.get("executed_at")
    link_url = act.get("razorpay_short_url") or act.get("razorpay_payment_link_url") or store_data.get("razorpay_short_url")
    link_id = act.get("razorpay_payment_link_id") or store_data.get("razorpay_payment_link_id")
    exec_err = act.get("execution_error") or store_data.get("execution_error")
    
    print(f"Action ID:             {act.get('id')}")
    print(f"Action Type:           {act.get('action_type')}")
    print(f"Executed:              {executed}")
    print(f"Executed At:           {executed_at}")
    print(f"Razorpay Link URL:     {link_url}")
    print(f"Razorpay Link ID:      {link_id}")
    print(f"Execution Error:       {exec_err}")
    print("---------------------------------------------------------------")
    
    if exec_err:
        print(f"\n[FAIL] Execution error reported: {exec_err}")
        print("\nForce-execution verification: NEEDS REVIEW")
        return
        
    if not executed:
        print("\n[FAIL] Action was NOT marked executed=True!")
        print("\nForce-execution verification: NEEDS REVIEW")
        return
        
    print("\n--- TASK 4: Independently verifying link directly via Razorpay API ---")
    if not link_id:
        print("[WARNING] razorpay_payment_link_id is missing from database row!")
        print("\nForce-execution verification: NEEDS REVIEW")
        return
        
    api_res = fetch_payment_link(link_id)
    if not api_res.get("success"):
        print(f"[FAIL] Error querying Razorpay API for link '{link_id}': {api_res.get('error')}")
        print("\nForce-execution verification: NEEDS REVIEW")
        return
        
    link_data = api_res.get("link", {})
    api_status = link_data.get("status")
    api_url = link_data.get("short_url")
    
    print(f"Razorpay API Status:   '{api_status}'")
    print(f"Razorpay API Short URL:{api_url}")
    print("---------------------------------------------------------------")
    
    if api_status in ("created", "issued"):
        print(f"\n[SUCCESS] Confirmed live Razorpay test payment link active: {api_url}")
        print(f"\nForce-execution verification: PASS (Real Link: {api_url})")
    else:
        print(f"\n[WARNING] Link status from Razorpay API is '{api_status}' (expected 'created')")
        print("\nForce-execution verification: NEEDS REVIEW")

if __name__ == "__main__":
    verify_forced_execution()
