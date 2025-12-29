from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import Preferences, User
from schemas import MeResponse

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    has_prefs = (
        db.query(Preferences)
        .filter(Preferences.user_id == current_user.id)
        .first()
        is not None
    )

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        has_preferences=has_prefs,
    )
