"""
Compat stub — real logic lives in db.client.

This file must NOT import from db.client at module level.  It exists only so
that the path backend/db/ can stay in the Python package without breaking
anything.  Import from db.client directly instead.
"""
