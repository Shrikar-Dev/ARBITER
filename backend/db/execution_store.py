import os
import json
import logging

logger = logging.getLogger(__name__)

STORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "execution_store.json"))

def load_execution_store() -> dict:
    if not os.path.exists(STORE_PATH):
        return {}
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load execution store: {e}")
        return {}

def save_execution_store(store: dict):
    try:
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save execution store: {e}")

def update_action_execution(action_id: str, data: dict):
    store = load_execution_store()
    if action_id not in store:
        store[action_id] = {}
    store[action_id].update(data)
    save_execution_store(store)

def get_action_execution(action_id: str) -> dict:
    store = load_execution_store()
    return store.get(action_id, {})
