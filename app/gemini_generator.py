from .ai_service import service
from .schemas import UserInput


def _demo_plan(user: UserInput) -> str:
    return f"""FitBuddy demo plan for {user.username}\nGoal: {user.goal}\nIntensity: {user.intensity}\n\nDay 1 — Full Body\nWarm-up: 5–10 min easy movement\nMain: Bodyweight squat 3x8–12; incline push-up 3x8–12; glute bridge 3x10–15; plank 3x20–30 sec\nCooldown: 5 min easy stretching\n\nDay 2 — Cardio + Mobility\nWarm-up: 5 min\nMain: Brisk walk/cycle 20–30 min; gentle mobility 10 min\nCooldown: 5 min\n\nDay 3 — Upper Body\nWarm-up: 5–10 min\nMain: Incline push-up 3x8–12; resistance-band row 3x10–15; shoulder raises 2x10–12; dead bug 3x8/side\nCooldown: 5 min\n\nDay 4 — Recovery\nEasy walk 15–25 min + gentle mobility\n\nDay 5 — Lower Body\nWarm-up: 5–10 min\nMain: Squat 3x8–12; reverse lunge 2x8/side; glute bridge 3x10–15; calf raise 2x12–15\nCooldown: 5 min\n\nDay 6 — Cardio + Core\nWarm-up: 5 min\nMain: Brisk cardio 20–30 min; bird dog 3x8/side; plank 3x20–30 sec\nCooldown: 5 min\n\nDay 7 — Rest / Light Activity\nEasy walking and gentle mobility as comfortable.\n\nSafety: Stop if something hurts or you feel unwell; focus on technique and recovery."""


def generate_workout_gemini(username: str, user_id: str, age: int, weight: float, goal: str, intensity: str) -> str:
    user = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)  # type: ignore[arg-type]
    if service.available:
        plan = service.generate_workout(user)
        return plan.model_dump_json(indent=2)
    if service.settings.demo_mode:
        return _demo_plan(user)
    raise RuntimeError("GEMINI_API_KEY is required when DEMO_MODE=false.")
