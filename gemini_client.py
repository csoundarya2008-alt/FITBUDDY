"""
gemini_client.py
-----------------
Central place to configure the Google Generative AI SDK.
If no GOOGLE_API_KEY is set, the app still runs in "demo mode" and
returns clearly-labeled placeholder text instead of crashing, so you
can test the full flow (forms, DB, templates) before wiring a real key.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file in the project root, if present

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DEMO_MODE = not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here"

# Model names are fixed here in code (not in .env).
# Full list of valid, currently-available model ids: https://ai.google.dev/gemini-api/docs/models
# Both the workout-plan generator and the nutrition-tip generator now use
# "gemini-3.6-flash" as requested. If the API ever replies "model not found",
# open this file and change these to a model id currently listed on the page above.
PRO_MODEL_NAME = "gemini-3.6-flash"
FLASH_MODEL_NAME = "gemini-3.6-flash"

pro_model = None
flash_model = None

if not DEMO_MODE:
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    pro_model = genai.GenerativeModel(PRO_MODEL_NAME)
    flash_model = genai.GenerativeModel(FLASH_MODEL_NAME)
