import os
import sys
import hmac
import hashlib
import json
import random
import httpx
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from services.razorpay_client import get_razorpay_client

WEBHOOK_URL = "http://localhost:8000/webhooks/razorpay"

def trigger_test_failure():
    """
    Simulates a real Razorpay test-mode payment failure.
    1. Creates a real Razorpay test order via Razorpay client SDK.
    2. Constructs a payment.failed webhook event payload.
    3. Signs the payload with RAZORPAY_WEBHOOK_SECRET (HMAC SHA256).
    4. Posts to http://localhost:8000/webhooks/razorpay.
    """
    key_id = os.getenv("RAZORPAY_KEY_ID")
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET") or "test_secret_key_123"
    
    # 1. Create a real Razorpay order in test mode
    client = get_razorpay_client()
    rupees = random.randint(1500, 9500)
    amount_paise = rupees * 100
    
    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"rcpt_{random.randint(1000, 9999)}",
        "notes": {"demo": "recovery_copilot_test_failure"}
    })
    
    order_id = order.get("id")
    pay_id = f"pay_test_{random.randint(10000000, 99999999)}"
    
    print(f"[SUCCESS] Created real Razorpay Test Order: {order_id} for RS {rupees:,.2f}")
    
    # 2. Construct payment.failed webhook body
    event_payload = {
        "entity": "event",
        "account_id": "acc_demo_test",
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": pay_id,
                    "entity": "payment",
                    "amount": amount_paise,
                    "currency": "INR",
                    "status": "failed",
                    "order_id": order_id,
                    "method": "upi",
                    "captured": False,
                    "description": "Subscription payment",
                    "email": "ananya.sharma99@gmail.com",
                    "contact": "+919876543210",
                    "error_code": "BAD_REQUEST_PAYMENT_TIMED_OUT",
                    "error_description": "UPI payment timed out waiting for bank gateway response",
                    "error_source": "bank",
                    "error_step": "payment_authentication",
                    "error_reason": "payment_timed_out",
                    "created_at": 1788357971
                }
            }
        },
        "created_at": 1788357971
    }
    
    body_bytes = json.dumps(event_payload).encode("utf-8")
    
    # 3. Compute HMAC SHA256 signature if secret exists
    signature = hmac.new(webhook_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature
    }
    
    # 4. Post to webhook endpoint
    print(f"Sending webhook to {WEBHOOK_URL} (Signature: {signature[:12]}...)...")
    try:
        r = httpx.post(WEBHOOK_URL, content=body_bytes, headers=headers, timeout=10)
        print(f"[OK] Webhook Response: HTTP {r.status_code} -> {r.text}")
        print(f"\nSUCCESS! Real Razorpay test failure event '{pay_id}' triggered end-to-end.")
        print(f"Check your dashboard at http://localhost:3000 to see the new event with badge 'Razorpay Webhook'.")
    except Exception as err:
        print(f"[ERROR] Failed to reach webhook endpoint: {err}")
        print("Make sure the backend server (uvicorn main:app --port 8000) is running!")

if __name__ == "__main__":
    trigger_test_failure()
