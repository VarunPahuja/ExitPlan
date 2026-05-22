"""
Migration runner — executes 001_initial_schema.sql against the Supabase
Postgres database using a direct psycopg2 connection, then verifies the
connection via the Supabase Python client.

Requires DATABASE_URL in backend/.env (direct Postgres URI from Supabase
dashboard: Settings > Database > Connection String).
"""

import io
import os
import re
import sys
from pathlib import Path

# Force UTF-8 output so status symbols render on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# Load backend/.env regardless of working directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

try:
    import psycopg2
    import psycopg2.errors
except ImportError:
    print("[FAIL] psycopg2-binary not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Add backend/ to path so db.supabase can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

MIGRATION_FILE = Path(__file__).parent / "migrations" / "001_initial_schema.sql"

TABLES = [
    "countries",
    "users",
    "country_scores",
    "policy_chunks",
    "policy_changes",
    "user_alerts",
    "outcomes",
]


def split_statements(sql: str) -> list[str]:
    """Split a SQL file into individual executable statements, stripping line comments."""
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    raw = "\n".join(lines)
    return [s.strip() for s in raw.split(";") if s.strip()]


def run():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[FAIL] DATABASE_URL is not set in backend/.env")
        print("       Get it from: Supabase dashboard > Settings > Database > Connection String (URI)")
        sys.exit(1)

    print("\n[....] Connecting to database...")
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        print("[ OK ] Connected.\n")
    except psycopg2.OperationalError as e:
        print(f"[FAIL] Connection failed: {e}")
        sys.exit(1)

    sql = MIGRATION_FILE.read_text(encoding="utf-8")
    statements = split_statements(sql)

    tables_done: list[str] = []
    warnings: list[str] = []

    for stmt in statements:
        create_table = re.search(r"CREATE\s+TABLE\s+(\w+)", stmt, re.IGNORECASE)
        create_ext   = re.search(r"CREATE\s+EXTENSION\s+(?:IF NOT EXISTS\s+)?(\w+)", stmt, re.IGNORECASE)
        create_idx   = re.search(r"CREATE\s+INDEX\s+(?:IF NOT EXISTS\s+)?(\w+)", stmt, re.IGNORECASE)
        insert_into  = re.search(r"INSERT\s+INTO\s+(\w+)", stmt, re.IGNORECASE)

        try:
            cur.execute(stmt)

            if create_ext:
                print(f"[ OK ] extension '{create_ext.group(1)}' enabled")
            elif create_table:
                name = create_table.group(1)
                tables_done.append(name)
                print(f"[ OK ] {name} created")
            elif insert_into:
                print(f"[ OK ] {insert_into.group(1)} seeded")
            elif create_idx:
                print(f"[ OK ] index '{create_idx.group(1)}' created")

        except psycopg2.errors.DuplicateTable:
            name = create_table.group(1) if create_table else "table"
            msg = f"[SKIP] {name} already exists"
            print(msg)
            warnings.append(msg)
            conn.rollback()

        except psycopg2.errors.DuplicateObject:
            label = (
                create_ext.group(1) if create_ext
                else create_idx.group(1) if create_idx
                else "object"
            )
            msg = f"[SKIP] '{label}' already exists"
            print(msg)
            warnings.append(msg)
            conn.rollback()

        except Exception as e:
            preview = stmt[:80].replace("\n", " ")
            print(f"[FAIL] Error on: {preview}...")
            print(f"       {type(e).__name__}: {e}")
            cur.close()
            conn.close()
            sys.exit(1)

    cur.close()
    conn.close()

    # Verify via Supabase Python client
    print("\n[....] Verifying connection via Supabase client...")
    try:
        from db.client import test_connection
        ok = test_connection()
        if ok:
            print("[ OK ] test_connection() passed — countries table is reachable\n")
        else:
            print("[WARN] test_connection() returned False — check SUPABASE_URL / SUPABASE_SERVICE_KEY\n")
    except Exception as e:
        print(f"[WARN] Could not run test_connection(): {e}\n")

    # Summary
    missing = [t for t in TABLES if t not in tables_done]
    if warnings:
        print(f"[INFO] {len(warnings)} statement(s) skipped (already existed).")
    if missing:
        print(f"[INFO] Tables not created this run (likely pre-existing): {', '.join(missing)}")
    print("[ OK ] Migration complete.\n")


if __name__ == "__main__":
    run()
