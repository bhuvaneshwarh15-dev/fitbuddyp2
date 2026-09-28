from __future__ import annotations

from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(100))
    intensity: Mapped[str] = mapped_column(String(20))
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    if settings.database_url.startswith("sqlite:///./"):
        import os
        os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db: Session, *, user_id: str, username: str, age: int, weight: float, goal: str, intensity: str) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        user = User(
            user_id=user_id, username=username, age=age, weight=weight,
            goal=goal, intensity=intensity, original_plan="", nutrition_tip="",
        )
        db.add(user)
    else:
        user.username = username
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity
    db.commit()
    db.refresh(user)
    return user


def save_plan(db: Session, user: User, plan: str, nutrition_tip: str) -> User:
    user.original_plan = plan
    user.nutrition_tip = nutrition_tip
    user.updated_plan = None
    user.feedback = None
    db.commit()
    db.refresh(user)
    return user


def update_plan(db: Session, user: User, updated_plan: str, feedback: str) -> User:
    user.updated_plan = updated_plan
    user.feedback = feedback
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_original_plan(db: Session, user_id: str) -> str | None:
    user = get_user(db, user_id)
    return user.original_plan if user else None


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
