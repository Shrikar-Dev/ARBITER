import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.razorpay_client import get_razorpay_client, fetch_payment_link

def verify_live_razorpay_link():
    try:
        client = get_razorpay_client()
        res = client.payment_link.all()
        links = res.get("payment_links", [])
        
        if not links:
            print("[WARNING] No payment links found in Razorpay account.")
            print("\nLink verification: NEEDS REVIEW")
            return
            
        link = links[0]
        link_id = link.get("id")
        short_url = link.get("short_url")
        status = link.get("status")
        amount = link.get("amount")
        currency = link.get("currency", "INR")
        description = link.get("description")
        
        print("--- Live Razorpay Payment Link Verification ---")
        print(f"Razorpay Link ID:      {link_id}")
        print(f"Razorpay Short URL:    {short_url}")
        print(f"Status from Razorpay:  '{status}'")
        print(f"Amount:                RS {amount/100:,.2f} ({amount} paise)")
        print(f"Description:           {description}")
        print("------------------------------------------------")
        
        # Verify via fetch_payment_link API wrapper
        fetch_res = fetch_payment_link(link_id)
        if not fetch_res.get("success"):
            print(f"[FAIL] Error fetching link from Razorpay API: {fetch_res.get('error')}")
            print("\nLink verification: NEEDS REVIEW")
            return
            
        verified_link = fetch_res.get("link", {})
        verified_status = verified_link.get("status")
        
        if verified_status in ("created", "issued", "paid", "partially_paid"):
            print(f"\n[CONFIRMED] Razorpay API link '{link_id}' is active and valid (status: '{verified_status}').")
            print("\nLink verification: PASS")
        else:
            print(f"\n[WARNING] Link status is '{verified_status}'!")
            print("\nLink verification: NEEDS REVIEW")
            
    except Exception as e:
        print(f"\n[FAIL] Exception during link verification: {e}")
        print("Link verification: NEEDS REVIEW")

if __name__ == "__main__":
    verify_live_razorpay_link()
