from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import DashboardItem, User

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed_item")
def seed_item(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = DashboardItem(
        user_id=current_user.id,
        date=date.today(),
        item_type="news",
        payload={"title": "Seed item", "source": "dev", "url": "https://example.com"},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id}
