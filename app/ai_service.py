from __future__ import annotations

from .config import get_settings
from .schemas import NutritionTip, UserInput, WorkoutPlan


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None
        if self.settings.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
            except ImportError as exc:
                raise RuntimeError("google-genai is not installed. Run: pip install -r requirements.txt") from exc

    @property
    def available(self) -> bool:
        return self.client is not None

    def _generate_structured(self, *, model: str, prompt: str, schema: type) -> object:
        if not self.client:
            raise RuntimeError("Gemini API key is not configured.")
        from google.genai import types
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.4,
            ),
        )
        if getattr(response, "parsed", None) is not None:
            return response.parsed
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return schema.model_validate_json(response.text)

    def generate_workout(self, user: UserInput) -> WorkoutPlan:
        prompt = f"""
You are FitBuddy, a conservative fitness-planning assistant. Create a safe, age-appropriate 7-day workout plan.
User: name={user.username}, age={user.age}, weight_kg={user.weight}, goal={user.goal}, intensity={user.intensity}.
Requirements:
- Exactly 7 days.
- Every day has a focus, warm-up, exercises, and cooldown.
- Include sets, reps or duration, and rest for every exercise.
- Keep intensity appropriate to the selected level and avoid dangerous challenges, extreme volume, or unsafe weight-loss practices.
- Do not prescribe calorie restriction, supplements, medication, or medical treatment.
- For a user under 18, emphasize technique, recovery, gradual progression, and adult/qualified-coach supervision for unfamiliar or strenuous exercises.
- If pain, dizziness, injury, or other concerning symptoms occur, advise stopping and seeking appropriate adult/medical guidance.
- Return only the requested structured object.
"""
        return self._generate_structured(model=self.settings.gemini_pro_model, prompt=prompt, schema=WorkoutPlan)  # type: ignore[return-value]

    def generate_nutrition_tip(self, user: UserInput) -> NutritionTip:
        prompt = f"""
Give one concise, practical nutrition/recovery tip for a FitBuddy user.
Goal: {user.goal}; intensity: {user.intensity}; age: {user.age}.
Avoid calorie targets, restrictive dieting, supplements, or medical claims. Favor balanced meals, hydration, sleep, recovery, and regular nutritious foods. Keep it age-appropriate. Return only the structured object.
"""
        return self._generate_structured(model=self.settings.gemini_flash_model, prompt=prompt, schema=NutritionTip)  # type: ignore[return-value]

    def update_workout(self, user: UserInput, original_plan: str, feedback: str) -> WorkoutPlan:
        prompt = f"""
Revise this FitBuddy 7-day workout plan using the user's feedback.
User profile: age={user.age}, goal={user.goal}, intensity={user.intensity}.
Feedback: {feedback}
Original plan:
{original_plan}
Rules:
- Preserve exactly 7 days and the same structured fields.
- Make only sensible changes supported by the feedback.
- Avoid dangerous challenges, extreme volume, restrictive dieting, supplements, medication, or medical treatment.
- Prioritize gradual progression, rest, technique, and age-appropriate training.
- Return only the requested structured object.
"""
        return self._generate_structured(model=self.settings.gemini_pro_model, prompt=prompt, schema=WorkoutPlan)  # type: ignore[return-value]


service = GeminiService()
