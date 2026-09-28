# FitBuddy — AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application based on the supplied project documentation. It accepts a user's name, ID, age, weight, goal, and workout intensity; generates a 7-day workout plan and nutrition/recovery tip; stores the results; accepts feedback for an AI-powered revision; and exposes a protected admin dashboard.

## Important implementation note

The supplied documentation names the older `google-generativeai` SDK and Gemini 1.5 Pro/Flash. Google now recommends the newer `google-genai` SDK. This implementation therefore keeps the documented Pro/Flash architecture while using configurable, current model names (`gemini-2.5-pro` and `gemini-2.5-flash` by default). The model names can be changed in `.env` without changing application code.

## Project structure

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_flash_generator.py
│   ├── gemini_generator.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── updated_plan.py
│   └── templates/
│       ├── all_users.html
│       ├── index.html
│       └── result.html
├── data/
├── static/
│   └── styles.css
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## VS Code setup

1. Install Python 3.11+ and VS Code.
2. Open this folder in VS Code.
3. Create a virtual environment:

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env`.
6. For real Gemini generation, put your Google Gemini API key in `GEMINI_API_KEY` and set `DEMO_MODE=false`.
7. For a no-key local UI test, keep `DEMO_MODE=true`. In demo mode the app uses deterministic fallback content instead of calling Gemini.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000 — user interface
- http://127.0.0.1:8000/docs — FastAPI API documentation
- http://127.0.0.1:8000/health — health/configuration check
- http://127.0.0.1:8000/view-all-users — protected admin dashboard

The admin dashboard uses HTTP Basic authentication. The default local credentials are in `.env`; change them before any non-local deployment.

## Test

```bash
pytest -q
```

The tests run in demo mode and verify the home page, plan generation, feedback update, and admin authentication.

## API behavior

The primary browser workflow is:

1. `GET /` → input form.
2. `POST /generate-workout` → validates input, generates/stores workout + nutrition tip, and renders `result.html`.
3. `POST /submit-feedback` → loads the original plan, sends the plan + feedback to Gemini when configured, stores the updated plan, and renders the result.
4. `GET /view-all-users` → protected admin dashboard.
5. `POST /delete-user/{user_id}` → protected user deletion.

## Safety

This project is a fitness-planning demo, not medical care. The AI prompts explicitly avoid restrictive dieting, supplements, medication, dangerous challenges, and medical treatment. For minors, the prompts emphasize technique, recovery, gradual progression, and appropriate adult/qualified supervision.
