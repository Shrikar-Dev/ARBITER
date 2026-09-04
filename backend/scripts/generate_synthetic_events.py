import os
import sys
import random
from datetime import datetime, timedelta, timezone

# Add parent directory to sys.path so backend imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.client import get_supabase
from models.failure_taxonomy import FAILURE_CATEGORIES

FIRST_NAMES = ["Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Kavya", "Aditya", "Neha", "Arjun", "Pooja", "Siddharth", "Meera", "Karan", "Tanvi"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Iyer", "Gupta", "Singh", "Joshi", "Nair", "Kulkarni", "Deshmukh", "Chopra", "Rao", "Mehta", "Bhat"]
DOMAINS = ["gmail.com", "yahoo.co.in", "outlook.com", "hotmail.com"]

EDGE_CASES = [
    {
        # Large amount + odd hour + card decline — rules engine says suggest_alt_method, but AI flags fraud-risk / no_action
        "amount": 1487500,  # ₹14,875 in paise
        "failure_reason_code": "card_auth_decline",
        "created_at_hour_offset": -1,
        "note": "high value + odd hour + card decline = plausible fraud signal"
    },
    {
        # Tiny amount insufficient_funds — rules engine says retry_delayed 4h, AI may shorten to retry_now
        "amount": 55000,  # ₹550
        "failure_reason_code": "insufficient_funds",
        "created_at_hour_offset": -3,
        "note": "small amount, low risk either way — AI may shorten delay"
    },
    {
        # Very large amount + 3ds_drop — rules engine says retry_now in 5 min, AI recommends more delay
        "amount": 1350000,  # ₹13,500
        "failure_reason_code": "3ds_drop",
        "created_at_hour_offset": -2,
        "note": "high value 3DS drop — AI may recommend more delay/caution"
    },
    {
        # bank_server_error at huge amount — rules engine says retry_delayed 30 min, AI urges faster retry_now
        "amount": 1200000,  # ₹12,000
        "failure_reason_code": "bank_server_error",
        "created_at_hour_offset": -4,
        "note": "high value + not customer's fault — AI may urge faster retry"
    },
    {
        # Near-round threshold insufficient_funds late night — rules engine says retry_delayed 4h, AI flags for manual review / no_action
        "amount": 1499900,  # ₹14,999
        "failure_reason_code": "insufficient_funds",
        "created_at_hour_offset": -1,
        "note": "near-round high amount, late night — AI may flag for review"
    },
    {
        # upi_timeout at low amount — testing AI confidence calibration
        "amount": 52000,  # ₹520
        "failure_reason_code": "upi_timeout",
        "created_at_hour_offset": -5,
        "note": "low stakes — good for testing AI confidence calibration, not just action"
    },
]

def generate_synthetic_events():
    supabase = get_supabase()
    
    categories = list(FAILURE_CATEGORIES.keys())
    events_to_create = []
    
    now = datetime.now(timezone.utc)
    
    # 40 baseline events: 8 of each category
    for idx, category in enumerate(categories * 8):
        tax_info = FAILURE_CATEGORIES[category]
        
        # Random amount between 500 and 15000 rupees -> stored in paise (amount * 100)
        rupees = random.randint(500, 15000)
        amount_paise = rupees * 100
        
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        num = random.randint(10, 99)
        domain = random.choice(DOMAINS)
        email = f"{first.lower()}.{last.lower()}{num}@{domain}"
        phone = f"+91 {random.randint(7000000000, 9999999999)}"
        
        # Spread across last 6 hours
        time_offset_minutes = (idx / 40.0) * 360 + random.randint(-5, 5)
        time_offset_minutes = max(0, min(360, time_offset_minutes))
        event_time = now - timedelta(minutes=time_offset_minutes)
        
        events_to_create.append({
            "razorpay_payment_id": f"pay_syn_{random.randint(10000000, 99999999)}",
            "razorpay_order_id": f"order_syn_{random.randint(10000000, 99999999)}",
            "amount": amount_paise,
            "currency": "INR",
            "failure_reason_code": category,
            "failure_description": tax_info["description"],
            "customer_email": email,
            "customer_phone": phone,
            "event_source": "synthetic",
            "created_at": event_time.isoformat()
        })

    # Add 6 deliberate edge case events
    for ec in EDGE_CASES:
        category = ec["failure_reason_code"]
        tax_info = FAILURE_CATEGORIES[category]
        
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        num = random.randint(10, 99)
        domain = random.choice(DOMAINS)
        email = f"{first.lower()}.{last.lower()}{num}@{domain}"
        phone = f"+91 {random.randint(7000000000, 9999999999)}"
        
        event_time = now + timedelta(hours=ec["created_at_hour_offset"])
        
        events_to_create.append({
            "razorpay_payment_id": f"pay_edge_{random.randint(10000000, 99999999)}",
            "razorpay_order_id": f"order_edge_{random.randint(10000000, 99999999)}",
            "amount": ec["amount"],
            "currency": "INR",
            "failure_reason_code": category,
            "failure_description": tax_info["description"],
            "customer_email": email,
            "customer_phone": phone,
            "event_source": "synthetic",
            "created_at": event_time.isoformat()
        })

    # Sort events by created_at ascending before inserting
    events_to_create.sort(key=lambda x: x["created_at"])
    
    response = supabase.table("payment_events").insert(events_to_create).execute()
    
    inserted_count = len(response.data) if response.data else 0
    print(f"Inserted {inserted_count} synthetic payment events (40 baseline + {len(EDGE_CASES)} edge cases) across 5 failure categories.")

if __name__ == "__main__":
    generate_synthetic_events()
