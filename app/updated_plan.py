from .ai_service import service
from .schemas import UserInput


def update_workout_plan(original_plan: str, feedback: str, *, username: str, user_id: str, age: int, weight: float, goal: str, intensity: str) -> str:
    user = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)  # type: ignore[arg-type]
    if service.available:
        plan = service.update_workout(user, original_plan, feedback)
        return plan.model_dump_json(indent=2)
    if service.settings.demo_mode:
        return f"{original_plan}\n\n--- Updated from feedback ---\nFeedback applied: {feedback}\n\nNote: Demo mode does not call Gemini; use a GEMINI_API_KEY to generate a true AI revision."
    raise RuntimeError("GEMINI_API_KEY is required when DEMO_MODE=false.")
