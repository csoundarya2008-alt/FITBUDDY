# FitBuddy – AI Fitness Plan Generator (FastAPI + Gemini)

FitBuddy generates personalized 7-day workout plans and nutrition tips
using Google's Gemini models, with a FastAPI backend, Jinja2 frontend,
and SQLite storage.

## Project Structure

```
fitbuddy/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── routes.py                  # All routes (web + JSON API)
│   ├── database.py                # SQLAlchemy models + DB helpers
│   ├── schemas.py                 # Pydantic request models
│   ├── gemini_client.py           # Gemini SDK configuration
│   ├── gemini_generator.py        # Gemini Pro → workout plan
│   ├── gemini_flash_generator.py  # Gemini Flash → nutrition tip
│   ├── updated_plan.py            # Gemini Pro → feedback-based revision
│   ├── templates/
│   │   ├── index.html             # Input form
│   │   ├── result.html            # Plan + tip + feedback form
│   │   ├── admin_login.html       # Password gate for the admin dashboard
│   │   └── all_users.html         # Admin dashboard (password protected)
│   └── static/
│       └── images/
├── requirements.txt
├── .env.example
└── README.md
```

Running the app auto-creates `fitbuddy.db` (SQLite) in the project root.

---

## 1. Setup in VS Code

1. Open the `fitbuddy` folder in VS Code (`File → Open Folder…`).
2. Open a terminal in VS Code: `Terminal → New Terminal`.
3. Create and activate a virtual environment:

   **macOS / Linux**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. (Recommended) In VS Code, select the venv interpreter:
   `Ctrl/Cmd+Shift+P → Python: Select Interpreter → ./venv`

---

## 2. Configure your Gemini API key

1. Get a free API key from **Google AI Studio**: https://aistudio.google.com/app/apikey
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env      # macOS/Linux
   copy .env.example .env    # Windows
   ```
3. Open `.env` and fill in your values:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   ADMIN_PASSWORD=choose-a-password
   SESSION_SECRET_KEY=any-long-random-string
   ```

   - `GOOGLE_API_KEY` — your Gemini API key.
   - `ADMIN_PASSWORD` — required to open `/view-all-users`. Change it from the
     default (`changeme123`) before sharing the app with anyone.
   - `SESSION_SECRET_KEY` — used to sign the admin login cookie; any random
     string works.

   The Gemini **model name** (`gemini-3.6-flash`, used for both plan
   generation and nutrition tips) is set directly in `app/gemini_client.py`,
   not in `.env`. If the API ever replies "model not found", open that file
   and change `PRO_MODEL_NAME` / `FLASH_MODEL_NAME` to a valid id from
   https://ai.google.dev/gemini-api/docs/models.

> **No key yet?** The app still runs in **DEMO MODE** and returns clearly
> labeled placeholder plans/tips, so you can test the full flow (forms,
> database, feedback loop, admin page) before wiring a real key.

---

## 3. Run the application

From the project root (`fitbuddy/`):

```bash
uvicorn app.main:app --reload
```

You should see Uvicorn start on `http://127.0.0.1:8000`, plus a console
message telling you whether you're in DEMO MODE or live Gemini mode.

- App (form): http://127.0.0.1:8000
- Admin login: http://127.0.0.1:8000/admin-login (password = your `ADMIN_PASSWORD`)
- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs

---

## 4. Test it

### Via the browser
1. Go to http://127.0.0.1:8000
2. Fill in Name, Age, Weight, Goal (e.g. "muscle gain"), Intensity — there's no
   User ID field; one is assigned automatically (first person = 1, next = 2, ...).
3. Click **Generate Plan** → you'll see your assigned User ID, your 7-day plan,
   and a nutrition tip.
4. Scroll down, enter **that User ID**, add feedback (e.g. "add more cardio"),
   click **Submit Feedback** → the plan is revised and both versions are shown.
5. Click **Admin login** (or go to `/admin-login`), enter your `ADMIN_PASSWORD`,
   and you'll land on `/view-all-users` — every registered user with their
   original + updated plans in a table (with a delete option and a logout link).

### Via Swagger UI (`/docs`)
Try the JSON endpoints directly:
- `POST /api/generate-plan` — create a user + generate a plan
- `POST /api/update-plan/{user_id}` — revise a plan with feedback
- `GET /api/users` — list all users and plans

### Via curl
```bash
curl -X POST http://127.0.0.1:8000/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"username":"Alex","user_id":1,"age":28,"weight":72.5,"goal":"muscle gain","intensity":"High"}'
```

---

## Notes

- **Database**: SQLite file `fitbuddy.db` is created automatically on first run.
  Delete this file at any time to reset all data.
- **Models used**: `gemini-1.5-pro` for structured workout generation/updates,
  `gemini-1.5-flash` for fast nutrition tips. Change these in `app/gemini_client.py`
  if you want to use a different Gemini model version.
- **Troubleshooting**:
  - `ModuleNotFoundError` → make sure your venv is activated and
    `pip install -r requirements.txt` completed successfully.
  - Gemini errors (quota / auth) → check your `.env` key is correct and has
    Gemini API access enabled in Google AI Studio.
  - Port already in use → run `uvicorn app.main:app --reload --port 8001`.
