"""
gemini_generator.py
--------------------
Generates a personalized 7-day workout plan using Gemini 1.5 Pro.
"""

from app.gemini_client import pro_model, DEMO_MODE


def generate_workout_gemini(user_input: dict) -> str:
    """
    Generate a personalized, structured 7-day workout plan.

    Args:
        user_input (dict): expects keys "goal" and "intensity"

    Returns:
        str: The generated (or demo) workout plan text.
    """
    goal = user_input.get("goal", "general fitness")
    intensity = user_input.get("intensity", "medium")

    if DEMO_MODE:
        return _demo_workout_plan(goal, intensity)

    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of
"{goal}", and prefers "{intensity}" intensity workouts.

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(repeat for Day 2-7)
"""
    try:
        response = pro_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating workout plan: {e}"


def _demo_workout_plan(goal: str, intensity: str) -> str:
    return f"""[DEMO MODE — no GOOGLE_API_KEY configured]

7-Day Workout Plan (Goal: {goal} | Intensity: {intensity})

Day 1: Upper Body Strength
Warm-up: 5 min jumping jacks + arm circles
Main Workout: Push-ups 3x12, Dumbbell rows 3x10, Shoulder press 3x10
Cooldown: Chest & shoulder stretches (2 min)

Day 2: Lower Body Strength
Warm-up: 5 min brisk walk + leg swings
Main Workout: Squats 3x15, Lunges 3x12/leg, Glute bridges 3x15
Cooldown: Hamstring & quad stretches (2 min)

Day 3: Cardio & Core
Warm-up: 5 min light jog
Main Workout: 20 min interval cardio, Plank 3x45s, Bicycle crunches 3x20
Cooldown: Deep breathing + core stretch

Day 4: Rest / Active Recovery
Light stretching, walking, or yoga (20-30 mins)

Day 5: Full Body Strength
Warm-up: 5 min dynamic stretching
Main Workout: Deadlifts 3x10, Bench press 3x10, Pull-ups 3x8
Cooldown: Full-body stretch (3 min)

Day 6: Cardio & Flexibility
Warm-up: 5 min light cardio
Main Workout: 25 min steady-state cardio, Yoga flow (15 min)
Cooldown: Static stretching

Day 7: Rest or Light Activity
Light walk, mobility work, or complete rest

Add a real GOOGLE_API_KEY to your .env file to generate a live, AI-personalized plan.
"""
