from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import secrets

from .config import get_settings
from .database import delete_user, get_all_users, get_db, get_user, save_plan, save_user, update_plan
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()


def admin_guard(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    settings = get_settings()
    if not (secrets.compare_digest(credentials.username, settings.admin_username) and secrets.compare_digest(credentials.password, settings.admin_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials", headers={"WWW-Authenticate": "Basic"})
    return credentials.username


def render_result(request: Request, user, *, message: str | None = None):
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "workout_plan": user.updated_plan or user.original_plan,
            "original_plan": user.original_plan,
            "nutrition_tip": user.nutrition_tip,
            "message": message,
        },
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
        plan = generate_workout_gemini(**data.model_dump())
        tip = generate_nutrition_tip_with_flash(data.username, data.age, data.goal, data.intensity)
        user = save_user(db, **data.model_dump())
        save_plan(db, user, plan, tip)
        return render_result(request, user)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"error": str(exc)}, status_code=400)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(db, payload.user_id)
        if not user:
            raise ValueError("User ID was not found. Generate a plan first.")
        updated = update_workout_plan(
            user.original_plan, payload.feedback,
            username=user.username, user_id=user.user_id, age=user.age,
            weight=user.weight, goal=user.goal, intensity=user.intensity,
        )
        user = update_plan(db, user, updated, payload.feedback)
        return render_result(request, user, message="Your workout plan has been updated from your feedback.")
    except Exception as exc:
        user = get_user(db, user_id)
        if user:
            return render_result(request, user, message=f"Update failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, _: str = Depends(admin_guard), db: Session = Depends(get_db)):
    users = get_all_users(db)
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users})


@router.post("/delete-user/{user_id}")
def remove_user(user_id: str, _: str = Depends(admin_guard), db: Session = Depends(get_db)):
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/view-all-users", status_code=303)


@router.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key), "demo_mode": settings.demo_mode}
