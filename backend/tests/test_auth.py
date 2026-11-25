"""Basic API regression test. Uses disposable CI database and test-only credentials."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-which-is-long-enough-123456"
os.environ["DATABASE_URL"] = "sqlite:///./ci-auth-test.db"
os.environ["APP_NAME"] = "EarnWorld Rewards"

from fastapi.testclient import TestClient
from app.main import app


def test_registration_login_and_protected_profile():
    with TestClient(app) as client:
        email = "ci-test@gmail.com"
        password = "test-password-1234"

        registered = client.post("/auth/register", json={"email": email, "password": password})
        assert registered.status_code == 201, registered.text
        token = registered.json()["access_token"]
        assert token

        duplicate = client.post("/auth/register", json={"email": email, "password": password})
        assert duplicate.status_code == 409

        logged_in = client.post("/auth/login", json={"email": email, "password": password})
        assert logged_in.status_code == 200, logged_in.text
        login_token = logged_in.json()["access_token"]

        profile = client.get("/auth/me", headers={"Authorization": f"Bearer {login_token}"})
        assert profile.status_code == 200
        assert profile.json()["email"] == email

        denied = client.get("/auth/me")
        assert denied.status_code == 401

        bad_login = client.post("/auth/login", json={"email": email, "password": "wrong-password"})
        assert bad_login.status_code == 401


def test_production_rejects_sqlite_database():
    import os
    import subprocess
    import sys
    from pathlib import Path
    env = os.environ.copy()
    env.update({
        "APP_ENV": "production",
        "JWT_SECRET_KEY": "production-test-secret-long-enough-123456789",
        "DATABASE_URL": "sqlite:///./must-not-start.db",
    })
    backend_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-c", "import app.main"], cwd=backend_dir, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Production requires managed PostgreSQL" in result.stderr
