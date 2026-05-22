"""
Supabase client singleton.

Exposes two clients:
  - anon_client()  — uses SUPABASE_ANON_KEY; for public/user-scoped operations.
  - admin_client() — uses SUPABASE_SERVICE_KEY; bypasses RLS; for server-side
                     work (scrapers, Celery workers, migrations).

Both are initialised lazily on first access.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_anon: Client | None = None
_admin: Client | None = None


def anon_client() -> Client:
    """Return the anon-key Supabase client (lazy init)."""
    global _anon
    if _anon is None:
        _anon = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_ANON_KEY"],
        )
    return _anon


def admin_client() -> Client:
    """Return the service-key Supabase client (lazy init, bypasses RLS)."""
    global _admin
    if _admin is None:
        _admin = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _admin


def test_connection() -> bool:
    """Query the countries table via the admin client. Returns True if rows come back."""
    try:
        result = admin_client().table("countries").select("code").execute()
        return bool(result.data)
    except Exception:
        return False
