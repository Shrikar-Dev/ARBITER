import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.client import get_supabase

def verify_webhook_row():
    supabase = get_supabase()
    
    # Query payment_events for the most recent row where event_source = 'razorpay_webhook'
    res = supabase.table("payment_events").select("*").eq("event_source", "razorpay_webhook").order("created_at", desc=True).limit(1).execute()
    data = res.data or []
    
    if not data:
        print("[WARNING] No payment_events row found with event_source = 'razorpay_webhook'!")
        print("Row verification: NEEDS REVIEW — see warnings above")
        return
        
    row = data[0]
    warnings = []
    
    amount_paise = row.get("amount") or 0
    email = row.get("customer_email")
    phone = row.get("customer_phone")
    reason_code = row.get("failure_reason_code")
    desc = row.get("failure_description")
    pay_id = row.get("razorpay_payment_id")
    created_at = row.get("created_at")
    
    print("--- Most Recent Webhook Event Row Verification ---")
    print(f"ID:                    {row.get('id')}")
    print(f"Razorpay Payment ID:   {pay_id}")
    print(f"Razorpay Order ID:     {row.get('razorpay_order_id')}")
    print(f"Amount (paise):        {amount_paise} (RS {amount_paise/100:,.2f})")
    print(f"Customer Email:        {email}")
    print(f"Customer Phone:        {phone}")
    print(f"Failure Reason Code:   {reason_code}")
    print(f"Failure Description:   {desc}")
    print(f"Event Source:          {row.get('event_source')}")
    print(f"Created At:            {created_at}")
    print("--------------------------------------------------")
    
    # Check for anomalies / warnings
    if not pay_id or pay_id == "pay_unknown":
        warnings.append("[WARNING] razorpay_payment_id is missing or set to dummy fallback!")
        
    if amount_paise <= 0:
        warnings.append(f"[WARNING] Invalid or zero amount: {amount_paise}")
        
    if not email:
        warnings.append("[WARNING] customer_email is null or empty!")
        
    if not phone:
        warnings.append("[WARNING] customer_phone is null or empty!")
        
    if not reason_code:
        warnings.append("[WARNING] failure_reason_code is null or empty!")
    elif reason_code == "unknown":
        warnings.append(f"[WARNING] failure_reason_code is 'unknown'. Raw description: '{desc}'")
        print(f"\n[INFO] Raw error payload details: description='{desc}'")
        
    if warnings:
        print("\nWarnings Flagged:")
        for w in warnings:
            print(f"  {w}")
        print("\nRow verification: NEEDS REVIEW - see warnings above")
    else:
        print("\nRow verification: PASS")

if __name__ == "__main__":
    verify_webhook_row()
