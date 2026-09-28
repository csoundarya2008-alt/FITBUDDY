"""
gemini_flash_generator.py
--------------------------
Generates a concise nutrition or recovery tip using Gemini Flash
(fast/lightweight model, good for short responses).
"""

from app.gemini_client import flash_model, DEMO_MODE


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a nutrition or recovery tip using Gemini Flash based on
    the user's fitness goal.

    Args:
        goal (str): User's fitness goal - e.g. "weight loss", "muscle gain".

    Returns:
        str: Generated tip.
    """
    if DEMO_MODE:
        return _demo_nutrition_tip(goal)

    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand. Keep it to 2-3 sentences."
    )
    try:
        response = flash_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating tip: {e}"


def _demo_nutrition_tip(goal: str) -> str:
    goal_lower = goal.lower()
    if "muscle" in goal_lower or "gain" in goal_lower:
        return (
            "[DEMO MODE] Prioritize protein! Aim for a good source of protein "
            "(chicken, fish, beans, or Greek yogurt) with every meal to support muscle growth and recovery."
        )
    if "loss" in goal_lower or "lean" in goal_lower or "fat" in goal_lower:
        return (
            "[DEMO MODE] Focus on a moderate calorie deficit with plenty of protein and fiber "
            "to stay full — think vegetables, lean protein, and whole grains."
        )
    return (
        "[DEMO MODE] Stay hydrated and eat a balanced mix of protein, complex carbs, "
        "and healthy fats throughout the day to fuel your workouts and recovery."
    )
