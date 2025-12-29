from datetime import date as date_type

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import DashboardItem, Vote, User
from schemas import DashboardResponse, DashboardItemResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ITEM_TYPES = ["news", "prices", "ai", "meme"]


def build_stub_payload(item_type: str):
    if item_type == "news":
        return {
            "title": "Stub news headline",
            "source": "stub",
            "url": "https://example.com",
            "summary": "Replace with CryptoPanic/real news on Day 3.",
        }
    if item_type == "prices":
        return {
            "BTC": 42000,
            "ETH": 2200,
            "note": "Replace with CoinGecko on Day 3.",
        }
    if item_type == "ai":
        return {
            "text": "Stub AI insight. Replace with LLM insight on Day 3.",
        }
    if item_type == "meme":
        return {
            "imageUrl": "https://i.imgflip.com/30b1gx.jpg",  # classic placeholder
            "caption": "Stub meme. Replace with JSON list / Reddit on Day 3.",
        }
    return {"note": "unknown type"}


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date_type.today()

    # Fetch existing items for today
    items = (
        db.query(DashboardItem)
        .filter(DashboardItem.user_id == current_user.id, DashboardItem.date == today)
        .all()
    )

    # If not all 4 exist, create missing ones
    existing_types = {i.item_type for i in items}
    created_any = False

    for t in ITEM_TYPES:
        if t not in existing_types:
            db.add(
                DashboardItem(
                    user_id=current_user.id,
                    date=today,
                    item_type=t,
                    payload=build_stub_payload(t),
                )
            )
            created_any = True

    if created_any:
        db.commit()
        items = (
            db.query(DashboardItem)
            .filter(DashboardItem.user_id == current_user.id, DashboardItem.date == today)
            .all()
        )

    # Fetch votes for these items (for this user)
    item_ids = [i.id for i in items]
    votes = {}
    if item_ids:
        vote_rows = (
            db.query(Vote)
            .filter(Vote.user_id == current_user.id, Vote.dashboard_item_id.in_(item_ids))
            .all()
        )
        votes = {v.dashboard_item_id: v.value for v in vote_rows}

    # Return in stable order: news, prices, ai, meme
    items_by_type = {i.item_type: i for i in items}
    response_items = []
    for t in ITEM_TYPES:
        i = items_by_type.get(t)
        if not i:
            continue
        response_items.append(
            DashboardItemResponse(
                id=i.id,
                item_type=i.item_type,
                payload=i.payload,
                user_vote=votes.get(i.id),
            )
        )

    return DashboardResponse(date=today, items=response_items)
