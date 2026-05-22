"""
Quick smoke test — verifies that SUPABASE_URL + SUPABASE_SERVICE_KEY are
correct and that the countries table exists and has data.

Run from anywhere:
    python backend/db/test_connection.py
"""

import sys
from pathlib import Path

# Python automatically prepends the script's directory to sys.path.
# backend/db/supabase.py would shadow the installed supabase package if
# backend/db/ stays on the path, so remove it before any imports.
_script_dir = str(Path(__file__).resolve().parent)
sys.path = [p for p in sys.path if Path(p).resolve() != Path(_script_dir).resolve()]
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.client import admin_client, test_connection


def main():
    print("Testing Supabase connection...")

    ok = test_connection()
    if not ok:
        print("[FAIL] test_connection() returned False")
        print("       Check SUPABASE_URL and SUPABASE_SERVICE_KEY in backend/.env")
        sys.exit(1)

    result = admin_client().table("countries").select("code, name").order("name").execute()
    print(f"[ OK ] Connected. {len(result.data)} countries found:")
    for r in result.data:
        print(f"       {r['code']}  {r['name']}")


if __name__ == "__main__":
    main()
