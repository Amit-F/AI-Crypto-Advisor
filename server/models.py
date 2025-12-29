from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    preferences = relationship("Preferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dashboard_items = relationship("DashboardItem", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")


class Preferences(Base):
    __tablename__ = "preferences"

    # one-to-one with users
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # store arrays as JSON for speed 
    assets = Column(JSON, nullable=False)         # e.g. ["BTC","ETH"]
    investor_type = Column(String(50), nullable=False)  # e.g. "HODLer"
    content_types = Column(JSON, nullable=False)  # e.g. ["Market News","Charts"]

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preferences")


class DashboardItem(Base):
    __tablename__ = "dashboard_items"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # ensures "daily" caching
    date = Column(Date, nullable=False, index=True)

    # one of: news, prices, ai, meme
    item_type = Column(String(20), nullable=False)

    # store actual content payload (news object, prices dict, insight text, meme URL, etc.)
    payload = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="dashboard_items")
    votes = relationship("Vote", back_populates="dashboard_item", cascade="all, delete-orphan")

    __table_args__ = (
        # at most one item per user per day per type (news/prices/ai/meme)
        UniqueConstraint("user_id", "date", "item_type", name="uq_user_date_itemtype"),
    )


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dashboard_item_id = Column(Integer, ForeignKey("dashboard_items.id", ondelete="CASCADE"), nullable=False, index=True)

    # +1 for thumbs up, -1 for thumbs down
    value = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="votes")
    dashboard_item = relationship("DashboardItem", back_populates="votes")

    __table_args__ = (
        # one vote per user per dashboard item (you can update it instead)
        UniqueConstraint("user_id", "dashboard_item_id", name="uq_user_dashboard_item_vote"),
    )
