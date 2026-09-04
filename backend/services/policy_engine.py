from models.failure_taxonomy import FAILURE_CATEGORIES

def classify_and_decide(payment_event: dict) -> dict:
    """
    Takes a payment_event record, matches its failure_reason_code against
    the FAILURE_CATEGORIES taxonomy, and returns a decision.
    """
    code = payment_event.get("failure_reason_code")
    
    if code in FAILURE_CATEGORIES:
        tax_info = FAILURE_CATEGORIES[code]
        return {
            "category": code,
            "confidence": 1.0,
            "rationale": tax_info.get("rationale", f"Matched to '{code}': {tax_info['description']}"),
            "classified_by": "rules_engine",
            "action_type": tax_info["default_action"],
            "action_delay_minutes": tax_info["default_delay_minutes"]
        }
    else:
        return {
            "category": "unknown",
            "confidence": 0.0,
            "rationale": "Failure reason not recognized, flagging for manual review.",
            "classified_by": "rules_engine",
            "action_type": "no_action",
            "action_delay_minutes": None
        }
