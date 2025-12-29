from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import Vote, DashboardItem, User
from schemas import VoteRequest, VoteResponse

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("", response_model=VoteResponse)
def upsert_vote(
    payload: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.value not in (-1, 1):
        raise HTTPException(status_code=422, detail="Vote value must be -1 or 1")

    item = db.query(DashboardItem).filter(DashboardItem.id == payload.dashboard_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Dashboard item not found")

    # Optional: prevent voting on someone else's dashboard item
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to vote on this item")

    vote = (
        db.query(Vote)
        .filter(Vote.user_id == current_user.id, Vote.dashboard_item_id == payload.dashboard_item_id)
        .first()
    )

    if not vote:
        vote = Vote(user_id=current_user.id, dashboard_item_id=payload.dashboard_item_id, value=payload.value)
        db.add(vote)
    else:
        vote.value = payload.value

    db.commit()
    db.refresh(vote)

    return VoteResponse(dashboard_item_id=vote.dashboard_item_id, value=vote.value)
