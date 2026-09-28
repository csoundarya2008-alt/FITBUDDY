"""
main.py
-------
FastAPI entry point for FitBuddy - AI Fitness Plan Generator.

Run with:
    uvicorn app.main:app --reload

Then visit:
    http://127.0.0.1:8000        (the app)
    http://127.0.0.1:8000/docs   (interactive API docs)
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.database import init_db
from app.routes import router
from app.gemini_client import DEMO_MODE

load_dotenv()

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generates personalized workout plans and nutrition tips using Gemini AI.",
    version="1.0.0",
)

# Session middleware — required so /view-all-users can remember that an
# admin has logged in with the correct password (see routes.py).
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-only-insecure-secret-change-me"),
)

# Static files (images/css/js)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()
    if DEMO_MODE:
        print(
            "\n⚠️  FitBuddy is running in DEMO MODE (no valid GOOGLE_API_KEY found).\n"
            "   Plans and tips will be placeholder text.\n"
            "   Add your key to a .env file to enable live Gemini responses.\n"
        )
    else:
        print("\n✅ FitBuddy started with Gemini API key configured.\n")

    if not os.getenv("ADMIN_PASSWORD"):
        print(
            "⚠️  No ADMIN_PASSWORD set in .env — the admin page will fall back to "
            "the default password 'changeme123'. Set ADMIN_PASSWORD in .env for real use.\n"
        )


# Register all routes
app.include_router(router)
