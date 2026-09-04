import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.action_scheduler import execute_pending_actions

res = execute_pending_actions()
print("=== RE-RUN EXECUTE-PENDING RESULT ===")
print("Attempted:       ", res.get("attempted"))
print("Succeeded:       ", res.get("succeeded"))
print("Failed:          ", res.get("failed"))
print("Duration (sec):  ", res.get("duration_seconds"))
print("\nDetails:")
for idx, d in enumerate(res.get("details", []), 1):
    print(f"  #{idx} action={d.get('action_type')} success={d.get('success')} url={d.get('link_url')} err={d.get('error')}")
