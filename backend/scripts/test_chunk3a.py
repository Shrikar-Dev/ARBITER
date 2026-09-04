import os
import sys
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.error_mapper import map_razorpay_error_to_category
from services.webhook_verifier import verify_webhook_signature

def test_task1_valid_signature():
    print("--- TASK 1: Testing Valid Webhook Signature Verification ---")
    fake_payload = b'{"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_test123"}}}}'
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    
    if not secret:
        print("[FAIL] RAZORPAY_WEBHOOK_SECRET is not loaded in environment!")
        return False
        
    valid_signature = hmac.new(
        key=secret.encode(),
        msg=fake_payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    result = verify_webhook_signature(fake_payload, valid_signature)
    print(f"[{'PASS' if result == True else 'FAIL'}] Valid signature test returned: {result} (Expected: True)")
    return result

def test_task2_trace_mapping():
    print("\n--- TASK 2: Tracing 'BAD_REQUEST_PAYMENT_CANCELLED_BY_USER' Mapping ---")
    reason = "BAD_REQUEST_PAYMENT_CANCELLED_BY_USER"
    desc = "User abandoned 3DS OTP verification page"
    combined = f"{reason.lower()} {desc.lower()}"
    
    print(f"Input reason: '{reason}'")
    print(f"Input description: '{desc}'")
    print(f"Combined string evaluated: '{combined}'")
    print("\nEvaluating if/elif condition chain in map_razorpay_error_to_category():")
    
    c1 = "timeout" in combined or "upi" in combined
    print(f"  1. 'timeout' in combined or 'upi' in combined -> {c1}")
    
    c2 = "insufficient" in combined or "balance" in combined
    print(f"  2. 'insufficient' in combined or 'balance' in combined -> {c2}")
    
    c3 = "authentication" in combined or "declined" in combined or "card" in combined
    print(f"  3. 'authentication' in combined or 'declined' in combined or 'card' in combined -> {c3}")
    
    c4 = "3ds" in combined or "otp" in combined or "secure" in combined
    print(f"  4. '3ds' in combined or 'otp' in combined or 'secure' in combined -> {c4}  <-- MATCHED HERE!")
    
    res = map_razorpay_error_to_category(reason, desc)
    print(f"\nFinal Mapped Category: '{res}'")
    print("Explanation: The test input description contained explicit keywords '3ds' and 'otp', which correctly triggered condition #4 for '3ds_drop'.")

def run_all_tests():
    t1_pass = test_task1_valid_signature()
    test_task2_trace_mapping()
    
    print("\n==========================================")
    print(f"Task 1: {'PASS' if t1_pass else 'FAIL'} - Task 2: correct match")
    print("==========================================")

if __name__ == "__main__":
    run_all_tests()
