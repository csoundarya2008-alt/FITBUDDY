"""
schemas.py
----------
Pydantic models used to validate incoming request data.
"""

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str
    # NOTE: user_id is intentionally NOT part of the input — the server
    # auto-assigns it in sequence (1, 2, 3 ...) when the user is created.
    age: int = Field(gt=0, lt=120)
    weight: float = Field(gt=0)
    goal: str
    intensity: str  # "Low", "Medium", "High"


class FeedbackRequest(BaseModel):
    user_id: int
    feedback: str


class WorkoutRequest(BaseModel):
    goal: str
    intensity: str
