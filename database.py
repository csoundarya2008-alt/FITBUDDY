"""
database.py
------------
SQLAlchemy models and DB helper functions for FitBuddy.
Uses SQLite for simple local persistence (fitbuddy.db).
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "fitbuddy.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # auto-assigned: 1, 2, 3 ...
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)

    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)

    user = relationship("User", back_populates="plans")


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------
def save_user(name: str, age: int, weight: float, goal: str, intensity: str) -> int:
    """
    Creates a new user. The ID is NOT supplied by the caller — the database
    assigns it automatically in sequence (1, 2, 3, ...).

    Returns:
        int: the newly assigned user_id.
    """
    db = SessionLocal()
    try:
        user = User(
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    finally:
        db.close()


def get_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Plan helpers
# ---------------------------------------------------------------------------
def save_plan(user_id: int, plan: str, nutrition_tip: str = None):
    db = SessionLocal()
    try:
        existing = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if existing:
            existing.original_plan = plan
            if nutrition_tip is not None:
                existing.nutrition_tip = nutrition_tip
        else:
            workout = WorkoutPlan(
                user_id=user_id, original_plan=plan, nutrition_tip=nutrition_tip
            )
            db.add(workout)
        db.commit()
    finally:
        db.close()


def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()
    finally:
        db.close()


def get_original_plan(user_id: int):
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None
    finally:
        db.close()


def get_plan_record(user_id: int):
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    finally:
        db.close()


def get_all_users_with_plans():
    """Returns a list of dicts combining user info with their plan(s)."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        result = []
        for user in users:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).first()
            result.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "age": user.age,
                    "weight": user.weight,
                    "goal": user.goal,
                    "intensity": user.intensity,
                    "original_plan": plan.original_plan if plan else "N/A",
                    "updated_plan": (plan.updated_plan if plan and plan.updated_plan else "Not updated"),
                    "nutrition_tip": plan.nutrition_tip if plan else "N/A",
                }
            )
        return result
    finally:
        db.close()


def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()
