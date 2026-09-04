import json
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from db.client import get_supabase
from services.webhook_verifier import verify_webhook_signature
from services.error_mapper import map_razorpay_error_to_category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    """
    Razorpay webhook listener.
    1. Reads raw bytes body & X-Razorpay-Signature header.
    2. Verifies HMAC SHA256 signature using verify_webhook_signature() (returns 400 if invalid).
    3. Checks event type (silently returns 200 for non-payment.failed events).
    4. For payment.failed events, extracts payment details, maps error category via map_razorpay_error_to_category(),
       and inserts into payment_events with event_source='razorpay_webhook'.
    5. Fast HTTP 200 OK JSONResponse.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "") or request.headers.get("x-razorpay-signature", "")

    if not verify_webhook_signature(raw_body, signature):
        logger.error("Unauthorized webhook request: Invalid or missing X-Razorpay-Signature header.")
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    try:
        payload = json.loads(raw_body.decode("utf-8") if isinstance(raw_body, bytes) else str(raw_body))
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON body: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

    event_type = payload.get("event")
    logger.info(f"Received Razorpay webhook event: {event_type}")

    if event_type != "payment.failed":
        return JSONResponse(status_code=200, content={"status": "ignored", "event": event_type})

    try:
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        amount = entity.get("amount")
        email = entity.get("email")
        phone = entity.get("contact")
        error_reason = entity.get("error_reason", "")
        error_description = entity.get("error_description", "")
        razorpay_payment_id = entity.get("id")
        order_id = entity.get("order_id")

        category = map_razorpay_error_to_category(error_reason, error_description)

        # Determine event source: test ping vs real webhook failure
        if not amount or amount == 0 or email == "customer@example.com":
            event_source = "razorpay_test_ping"
        else:
            event_source = "razorpay_webhook"

        supabase = get_supabase()
        supabase.table("payment_events").insert({
            "amount": amount,
            "currency": entity.get("currency", "INR"),
            "customer_email": email,
            "customer_phone": phone,
            "failure_reason_code": category,
            "failure_description": error_description or error_reason or "Payment failed",
            "event_source": event_source,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": order_id
        }).execute()

        logger.info(f"Inserted Razorpay payment.failed event '{razorpay_payment_id}' into payment_events with source '{event_source}'.")
        return JSONResponse(status_code=200, content={"status": "received", "event_source": event_source})

    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")
        return JSONResponse(status_code=400, content={"error": f"Failed to process payload: {str(e)}"})
