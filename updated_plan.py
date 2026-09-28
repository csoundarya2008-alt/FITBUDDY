"""
updated_plan.py
----------------
Revises an existing workout plan based on user feedback, using Gemini 1.5 Pro.
"""

from app.gemini_client import pro_model, DEMO_MODE


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """
    Update the workout plan based on user feedback.

    Args:
        original_plan (str): The user's current/original 7-day plan.
        user_feedback (str): Feedback text, e.g. "Add more cardio".

    Returns:
        str: The revised workout plan.
    """
    if DEMO_MODE:
        return _demo_updated_plan(original_plan, user_feedback)

    prompt = f"""
You are a professional fitness trainer assistant.

Update the following workout plan based on the user's feedback.
Keep the same 7-day structure (Day 1 - Day 7) but adjust exercises,
volume, or focus areas according to the feedback below.

Original workout plan:
{original_plan}

User feedback:
{user_feedback}

Return the full, revised 7-day plan in the same day-by-day format.
"""
    try:
        response = pro_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error updating plan: {e}"


def _demo_updated_plan(original_plan: str, user_feedback: str) -> str:
    return (
        f"[DEMO MODE — no GOOGLE_API_KEY configured]\n\n"
        f"Feedback received: \"{user_feedback}\"\n\n"
        f"(In live mode, Gemini 1.5 Pro would rewrite the plan below to incorporate this feedback.)\n\n"
        f"--- Original Plan ---\n{original_plan}"
    )
