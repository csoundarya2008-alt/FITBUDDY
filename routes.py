"""
routes.py
---------
Core routing logic for FitBuddy. Bridges the frontend templates, the
Gemini-powered generation modules, and the SQLite database.
"""

import os
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app import database
from app.schemas import UserInput, FeedbackRequest, WorkoutRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan
from app.gemini_client import PRO_MODEL_NAME, FLASH_MODEL_NAME

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Falls back to a default only if the user hasn't set one in .env yet.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")


# ---------------------------------------------------------------------------
# / — Home route: shows the input form
# ---------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# /generate-workout — Web form submission: generates plan + saves to DB
# NOTE: no user_id is collected from the form — the database assigns one
# automatically in sequence (first person = 1, next = 2, and so on).
# ---------------------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        # Validate with Pydantic
        user_data = UserInput(
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        # Save user — id is auto-assigned by the database
        new_user_id = database.save_user(
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )

        # Generate AI plan + nutrition tip
        plan = generate_workout_gemini(
            {"goal": user_data.goal, "intensity": user_data.intensity}
        )
        nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

        # Persist plan against the new user's auto-assigned id
        database.save_plan(new_user_id, plan, nutrition_tip)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "username": user_data.username,
                "user_id": new_user_id,
                "age": user_data.age,
                "weight": user_data.weight,
                "goal": user_data.goal,
                "intensity": user_data.intensity,
                "workout_plan": plan,
                "nutrition_tip": nutrition_tip,
                "updated_plan": None,
                "feedback_message": None,
                "is_new_user": True,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")


# ---------------------------------------------------------------------------
# /submit-feedback — Web form submission: revises plan based on feedback
# ---------------------------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
):
    user = database.get_user(user_id)
    original = database.get_original_plan(user_id)

    if not user or not original:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "username": "Unknown",
                "user_id": user_id,
                "age": None,
                "weight": None,
                "goal": None,
                "intensity": None,
                "workout_plan": None,
                "nutrition_tip": None,
                "updated_plan": None,
                "feedback_message": "No original plan found for this User ID. "
                "Please generate a plan first.",
                "feedback_error": True,
            },
        )

    updated = update_workout_plan(original, feedback)
    database.update_plan(user_id, updated)

    plan_record = database.get_plan_record(user_id)
    nutrition_tip = plan_record.nutrition_tip if plan_record else None

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user.name,
            "user_id": user.id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": original,
            "nutrition_tip": nutrition_tip,
            "updated_plan": updated,
            "feedback_message": "Your plan has been updated based on your feedback!",
            "feedback_error": False,
        },
    )


# ---------------------------------------------------------------------------
# Admin login — /view-all-users is password protected.
# Password comes from ADMIN_PASSWORD in .env; session cookie remembers login.
# ---------------------------------------------------------------------------
@router.get("/admin-login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if request.session.get("is_admin"):
        return RedirectResponse(url="/view-all-users", status_code=303)
    return templates.TemplateResponse(
        "admin_login.html", {"request": request, "error": None}
    )


@router.post("/admin-login", response_class=HTMLResponse)
def admin_login_submit(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse(url="/view-all-users", status_code=303)
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Incorrect password. Please try again."},
    )


@router.get("/admin-logout")
def admin_logout(request: Request):
    request.session.pop("is_admin", None)
    return RedirectResponse(url="/admin-login", status_code=303)


# ---------------------------------------------------------------------------
# /view-all-users — Admin dashboard (password required)
# ---------------------------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/admin-login", status_code=303)
    user_data = database.get_all_users_with_plans()
    return templates.TemplateResponse(
        "all_users.html", {"request": request, "users": user_data}
    )


@router.post("/delete-user/{user_id}")
def delete_user_route(request: Request, user_id: int):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/admin-login", status_code=303)
    database.delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)


# ---------------------------------------------------------------------------
# JSON API endpoints (for /docs testing, mobile clients, etc.)
# ---------------------------------------------------------------------------
@router.post("/api/generate-plan")
def api_generate_plan(user_data: UserInput):
    try:
        new_user_id = database.save_user(
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )
        plan = generate_workout_gemini(
            {"goal": user_data.goal, "intensity": user_data.intensity}
        )
        nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)
        database.save_plan(new_user_id, plan, nutrition_tip)

        return {
            "message": "Workout plan generated and saved successfully!",
            "user_id": new_user_id,
            "workout_plan": plan,
            "nutrition_tip": nutrition_tip,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")


@router.post("/api/generate-workout/gemini")
def api_generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini(
            {"goal": request.goal, "intensity": request.intensity}
        )
        return {"model": PRO_MODEL_NAME, "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/nutrition-tip")
def api_get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return {"model": FLASH_MODEL_NAME, "goal": goal, "nutrition_tip": tip}


@router.post("/api/update-plan/{user_id}")
def api_update_user_plan(user_id: int, data: FeedbackRequest):
    original = database.get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    database.update_plan(user_id, updated)
    return {"updated_plan": updated}


@router.get("/api/users")
def api_get_all_users(password: str):
    """Simple query-param password check so the admin data can't be
    pulled through the JSON API without the password either."""
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    return database.get_all_users_with_plans()
