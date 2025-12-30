from datetime import date as date_type

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import DashboardItem, Vote, User, Preferences
from schemas import DashboardResponse, DashboardItemResponse
from integrations.coingecko import fetch_prices_usd
from integrations.cryptopanic import fetch_market_news


router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ITEM_TYPES = ["news", "prices", "ai", "meme"]


def build_stub_payload(item_type: str):
    if item_type == "news":
        return {
            "title": "Stub news headline",
            "source": "stub",
            "url": "https://example.com",
            "summary": "Replace with CryptoPanic/real news",
        }
    if item_type == "prices":
        return {
            "note": "This should be replaced by CoinGecko.",
        }
    if item_type == "ai":
        return {"text": "Stub AI insight. Replace with LLM insight on Day 3."}
    if item_type == "meme":
        return {
            "imageUrl": "https://i.imgflip.com/30b1gx.jpg",
            "caption": "Stub meme. Replace with dynamic meme on Day 3.",
        }
    return {"note": "unknown type"}


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
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

    existing_types = {i.item_type for i in items}
    created_any = False

    # Load user preferences once (for prices and later for other sections)
    prefs = (
        db.query(Preferences)
        .filter(Preferences.user_id == current_user.id)
        .first()
    )
    user_assets = (prefs.assets if prefs and prefs.assets else ["BTC", "ETH"])

    for t in ITEM_TYPES:
        if t in existing_types:
            continue

        payload = None

        if t == "prices":
            # Real data from CoinGecko
            payload = await fetch_prices_usd(user_assets)
        elif t == "news":
            payload = await fetch_market_news(user_assets)
        else:
            # still stubbed for now
            payload = build_stub_payload(t)

        db.add(
            DashboardItem(
                user_id=current_user.id,
                date=today,
                item_type=t,
                payload=payload,
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

    # Votes
    item_ids = [i.id for i in items]
    votes_map = {}
    if item_ids:
        vote_rows = (
            db.query(Vote)
            .filter(Vote.user_id == current_user.id, Vote.dashboard_item_id.in_(item_ids))
            .all()
        )
        votes_map = {v.dashboard_item_id: v.value for v in vote_rows}

    # Stable ordering
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
                user_vote=votes_map.get(i.id),
            )
        )

    return DashboardResponse(date=today, items=response_items)
