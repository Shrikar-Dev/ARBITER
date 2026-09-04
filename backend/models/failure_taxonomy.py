FAILURE_CATEGORIES = {
    "upi_timeout": {
        "description": "UPI payment timed out waiting for bank response",
        "default_action": "retry_now",
        "default_delay_minutes": 0,
        "rationale": "Matched to 'upi_timeout': UPI payments that timeout are usually resolved by immediate retry, as the bank connection issue is often momentary."
    },
    "insufficient_funds": {
        "description": "Payment declined due to insufficient balance",
        "default_action": "retry_delayed",
        "default_delay_minutes": 240,  # retry in 4 hours, funds may be added
        "rationale": "Matched to 'insufficient_funds': Retrying immediately will fail. Delaying retry by 4 hours allows time for the customer to add funds or for salary/credits to clear."
    },
    "card_auth_decline": {
        "description": "Card issuer declined authentication/authorization",
        "default_action": "suggest_alt_method",
        "default_delay_minutes": None,
        "rationale": "Matched to 'card_auth_decline': Card issuer explicitly declined authorization. Retrying the same card is unlikely to succeed; prompting the customer for an alternative payment method (e.g. UPI or Netbanking) is optimal."
    },
    "3ds_drop": {
        "description": "Customer dropped off during 3D Secure verification step",
        "default_action": "retry_now",
        "default_delay_minutes": 5,
        "rationale": "Matched to '3ds_drop': Customer abandoned the OTP/3DS screen. A quick prompt or retry nudge within 5 minutes catches the customer while intent is high."
    },
    "bank_server_error": {
        "description": "Bank server error, unrelated to customer",
        "default_action": "retry_delayed",
        "default_delay_minutes": 30,
        "rationale": "Matched to 'bank_server_error': Intermittent core banking issue detected. Retrying after 30 minutes gives the acquiring bank time to recover stability."
    }
}
