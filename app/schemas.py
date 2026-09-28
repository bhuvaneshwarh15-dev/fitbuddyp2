from typing import Literal
from pydantic import BaseModel, Field, field_validator


Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, lt=500)
    goal: Goal
    intensity: Intensity

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Name is required")
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    feedback: str = Field(min_length=5, max_length=1000)


class Exercise(BaseModel):
    name: str
    sets: int = Field(ge=1, le=8)
    reps_or_duration: str
    rest_seconds: int = Field(ge=0, le=600)


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: list[Exercise] = Field(min_length=1, max_length=10)
    cooldown: str


class WorkoutPlan(BaseModel):
    overview: str
    safety_note: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)


class NutritionTip(BaseModel):
    title: str
    tip: str
    recovery_note: str
