from .ai_service import service
from .schemas import UserInput


def generate_nutrition_tip_with_flash(username: str, age: int, goal: str, intensity: str) -> str:
    user = UserInput(username=username, user_id="tip-user", age=age, weight=60, goal=goal, intensity=intensity)  # type: ignore[arg-type]
    if service.available:
        tip = service.generate_nutrition_tip(user)
        return f"{tip.title}\n\n{tip.tip}\n\nRecovery: {tip.recovery_note}"
    if service.settings.demo_mode:
        return "Balanced recovery tip\n\nBuild meals around regular nutritious foods, include a protein source, eat a variety of fruits and vegetables, drink water, and give your body enough time to recover.\n\nRecovery: Consistent sleep and rest days matter as much as training."
    raise RuntimeError("GEMINI_API_KEY is required when DEMO_MODE=false.")
