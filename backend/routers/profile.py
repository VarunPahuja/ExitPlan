"""
/profile router — CRUD for the authenticated user's immigration profile.

Stores nationality, education level, field of work, target visa type, and the
five priority weights (jobs / cost / safety / climate / language) that drive
the scoring engine.
"""

from fastapi import APIRouter, Depends, HTTPException

from db.client import admin_client
from models.user import ProfileResponse, ProfileUpdate
from services.auth import get_current_user, get_current_user_info

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user)):
    """Fetch the current user's profile."""
    result = admin_client().table("users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result.data[0]


@router.put("/", response_model=ProfileResponse)
async def upsert_profile(
    body: ProfileUpdate,
    user_info: dict = Depends(get_current_user_info),
):
    """Create or update the current user's profile."""
    row: dict = {"id": user_info["id"], "email": user_info["email"]}

    update_fields = body.model_dump(exclude_none=True)
    if "weights" in update_fields:
        # Serialize UserWeights to plain dict for the JSONB column
        update_fields["weights"] = body.weights.model_dump()
    row.update(update_fields)

    result = admin_client().table("users").upsert(row).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to upsert profile")
    return result.data[0]


@router.delete("/")
async def delete_profile(user_id: str = Depends(get_current_user)):
    """Delete the current user's profile and associated data."""
    return {"message": "profile delete — coming soon"}
