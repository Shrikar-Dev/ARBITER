import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.environ.get("SUPABASE_URL")
_SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase() -> Client:
    """
    Return an authenticated Supabase client.

    Uses the service-role key so the backend can bypass Row Level Security
    when reading and writing data. Never expose this key to the frontend.
    """
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment. "
            "Copy backend/.env.example to backend/.env and fill in your values."
        )
    return create_client(_SUPABASE_URL, _SUPABASE_KEY)
