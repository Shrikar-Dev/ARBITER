import os
import re
import time
import logging
import razorpay
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = None

def get_razorpay_client():
    global _client
    if _client is None:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not key_id or not key_secret:
            raise RuntimeError("RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET not set in environment.")
        _client = razorpay.Client(auth=(key_id, key_secret))
    return _client

def clean_contact_number(phone: str) -> str:
    """Ensures phone number complies with Razorpay format (no recurring digits)."""
    if not phone:
        return "+919876543210"
    digits = re.sub(r"\D", "", phone)
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) < 10 or digits.count(digits[0]) >= 8:
        return "+919876543210"
    return f"+91{digits}"

def create_payment_link(amount_paise: int, customer_email: str, customer_phone: str, description: str) -> dict:
    """
    Creates a Razorpay test-mode payment link.
    Returns {"success": True, "link_id": ..., "short_url": ...} on success
    Returns {"success": False, "error": <message>} on failure — never raises.
    """
    try:
        client = get_razorpay_client()
        
        email = customer_email or "customer@example.com"
        phone = clean_contact_number(customer_phone)
        name = email.split("@")[0].replace(".", " ").title()
        
        payload = {
            "amount": int(amount_paise),
            "currency": "INR",
            "accept_partial": False,
            "description": description or "Payment Failure Recovery Nudge",
            "customer": {
                "name": name,
                "email": email,
                "contact": phone
            },
            "notify": {
                "sms": False,
                "email": False
            },
            "reminder_enable": False
        }
        
        response = client.payment_link.create(payload)
        return {
            "success": True,
            "link_id": response.get("id"),
            "short_url": response.get("short_url")
        }
    except Exception as e:
        err_msg = str(e)
        if "limit" in err_msg.lower() and "reached" in err_msg.lower():
            err_msg = "Razorpay test-mode payment link quota exhausted (30 link limit reached for this account)"
            
        logger.error(f"Razorpay payment_link.create failed: {err_msg}")
        return {
            "success": False,
            "error": err_msg
        }

def fetch_payment(payment_id: str) -> dict:
    """
    Fetches a payment's current status from Razorpay.
    Returns {"success": True, "payment": ...} on success
    Returns {"success": False, "error": <message>} on failure — never raises.
    """
    try:
        client = get_razorpay_client()
        response = client.payment.fetch(payment_id)
        return {
            "success": True,
            "payment": response
        }
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Razorpay payment.fetch failed: {err_msg}")
        return {
            "success": False,
            "error": err_msg
        }

def fetch_payment_link(link_id: str) -> dict:
    """
    Fetches a payment link's status directly from Razorpay API.
    Returns {"success": True, "link": response} on success.
    Returns {"success": False, "error": msg} on failure — never raises.
    """
    try:
        client = get_razorpay_client()
        response = client.payment_link.fetch(link_id)
        return {
            "success": True,
            "link": response
        }
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Razorpay payment_link.fetch failed: {err_msg}")
        return {
            "success": False,
            "error": err_msg
        }

def verify_webhook_signature(body_bytes: bytes, signature: str, secret: str) -> bool:
    """Verifies HMAC SHA256 webhook signature using Razorpay SDK Utility."""
    try:
        client = get_razorpay_client()
        body_str = body_bytes.decode("utf-8") if isinstance(body_bytes, bytes) else str(body_bytes)
        client.utility.verify_webhook_signature(body_str, signature, secret)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception as e:
        logger.error(f"Webhook signature verification error: {e}")
        return False
