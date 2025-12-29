from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import Preferences, User
from schemas import PreferencesUpsertRequest, PreferencesResponse

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.query(Preferences).filter(Preferences.user_id == current_user.id).first()
    if not prefs:
        # 404 is clearer for flow control.
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Preferences not set")

    return PreferencesResponse(
        assets=prefs.assets,
        investor_type=prefs.investor_type,
        content_types=prefs.content_types,
    )


@router.post("", response_model=PreferencesResponse, status_code=status.HTTP_200_OK)
def upsert_preferences(
    payload: PreferencesUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.query(Preferences).filter(Preferences.user_id == current_user.id).first()

    if not prefs:
        prefs = Preferences(
            user_id=current_user.id,
            assets=payload.assets,
            investor_type=payload.investor_type,
            content_types=payload.content_types,
        )
        db.add(prefs)
    else:
        prefs.assets = payload.assets
        prefs.investor_type = payload.investor_type
        prefs.content_types = payload.content_types

    db.commit()
    db.refresh(prefs)

    return PreferencesResponse(
        assets=prefs.assets,
        investor_type=prefs.investor_type,
        content_types=prefs.content_types,
    )
