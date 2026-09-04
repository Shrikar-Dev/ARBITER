import os
import logging
import razorpay
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Uses razorpay.Utility.verify_webhook_signature() to verify a request genuinely
    came from Razorpay, using RAZORPAY_WEBHOOK_SECRET from .env.
    Returns True/False. Never raises.
    """
    if not signature_header:
        return False
        
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    if not secret:
        logger.warning("RAZORPAY_WEBHOOK_SECRET not set in environment.")
        return False
        
    try:
        key_id = os.getenv("RAZORPAY_KEY_ID", "dummy_key")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET", "dummy_secret")
        client = razorpay.Client(auth=(key_id, key_secret))
        
        body_str = payload_body.decode("utf-8") if isinstance(payload_body, bytes) else str(payload_body)
        client.utility.verify_webhook_signature(body_str, signature_header, secret)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception as e:
        logger.error(f"Error during webhook signature verification: {e}")
        return False
