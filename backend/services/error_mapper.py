import logging

logger = logging.getLogger(__name__)

def map_razorpay_error_to_category(error_reason: str, error_description: str) -> str:
    """
    Maps Razorpay's error_reason/error_description strings to taxonomy categories:
    - "timeout" or "upi" -> "upi_timeout"
    - "insufficient" or "balance" -> "insufficient_funds"  
    - "authentication" or "declined" or "card" -> "card_auth_decline"
    - "3ds" or "otp" or "secure" -> "3ds_drop"
    - "server" or "gateway" or "bank_error" -> "bank_server_error"
    - anything else -> "unknown"

    Check both fields, case-insensitive. Return first match; default "unknown" if nothing matches.
    """
    reason = str(error_reason or "").lower()
    desc = str(error_description or "").lower()
    combined = f"{reason} {desc}"

    if "timeout" in combined or "upi" in combined:
        return "upi_timeout"
    if "insufficient" in combined or "balance" in combined:
        return "insufficient_funds"
    if "authentication" in combined or "declined" in combined or "card" in combined:
        return "card_auth_decline"
    if "3ds" in combined or "otp" in combined or "secure" in combined:
        return "3ds_drop"
    if "server" in combined or "gateway" in combined or "bank_error" in combined:
        return "bank_server_error"

    return "unknown"
