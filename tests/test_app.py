from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_and_feedback():
    response = client.post("/generate", data={
        "name": "Test User",
        "age": 25,
        "gender": "male",
        "weight": 70,
        "height": 175,
        "fitness_goal": "weight loss",
        "experience_level": "beginner"
    })
    assert response.status_code == 200

def test_admin_requires_auth():
    # 1. Unauthenticated request should return 401
    assert client.get("/view-all-users").status_code == 401

    # 2. Seed a test user
    client.post("/generate", data={
        "name": "Test User",
        "age": 25,
        "gender": "male",
        "weight": 70,
        "height": 175,
        "fitness_goal": "weight loss",
        "experience_level": "beginner"
    })

    # 3. Authenticated request should succeed and contain 'Test User'
    response = client.get("/view-all-users", auth=("admin", "testpass"))
    assert response.status_code == 200
    assert "Test User" in response.text
    # 1. Unauthenticated request should be unauthorized
    assert client.get("/view-all-users").status_code == 401

    # 2. Seed/Create a test user first (adjust payload fields to match your app's schema)
    client.post("/generate", json={
        "name": "Test User",
        "age": 25,
        "gender": "male",
        "weight": 70,
        "height": 175,
        "fitness_goal": "weight loss",
        "experience_level": "beginner"
    })

    # 3. Authenticated request should now succeed and display 'Test User'
    response = client.get("/view-all-users", auth=("admin", "testpass"))
    assert response.status_code == 200
    assert "Test User" in response.text