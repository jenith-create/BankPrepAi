# BankPrepAi

A Flask web app that helps students prepare for Indian banking exams. It has three parts:

- **Ask**: chat with an AI tutor about banking concepts and exam topics. Conversations are saved in MongoDB.
- **Exams**: a list of banking exams (IBPS, SBI, RBI) with application dates, exam dates and a status worked out from today's date.
- **Eligibility**: enter your date of birth, category and education to see which exams you meet the rules for.

> For learning purposes. Dates and eligibility rules change, so always confirm them in the official notification.

**Live demo:** https://bankprepai-chay.onrender.com/

## Tech stack

- Python, Flask, Gunicorn
- MongoDB Atlas (PyMongo)
- Groq API for the AI answers
- Bootstrap 5 and a custom stylesheet
- GitHub Actions (CI) and Render (CD)

## How it works

| Feature | How it's built |
|---|---|
| AI answers | `services/ai_service.py` sends the question to the Groq API |
| Exam list | `services/exams.py` reads the `exams` collection and computes each exam's status |
| Eligibility | `services/eligibility.py` applies plain Python rules to the exam data. No AI is involved, so answers come only from the stored data |

Exam data lives in MongoDB, so it can be corrected without changing code. Each exam records its source link, when it was last checked, and how well its details are confirmed.

## Project structure

```
.
├── .github/workflows/ci.yml   # test and deploy pipeline
├── app.py                     # Flask routes
├── db.py                      # MongoDB connection and collections
├── exams.json                 # exam data
├── seed_exams.py              # loads exams.json into MongoDB
├── requirements.txt
├── services/
│   ├── ai_service.py          # Groq calls
│   ├── exams.py               # exam list and status
│   └── eligibility.py         # eligibility rules
├── static/
│   └── style.css
└── templates/
    ├── base.html              # header and navigation
    ├── index.html             # Ask page
    ├── exams.html
    └── eligibility.html
```

## Run it locally

**1. Clone the repo and create a virtual environment**

```bash
git clone https://github.com/jenith-create/ai-banking-assistant.git
cd ai-banking-assistant
python -m venv venv
```

Activate it:

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Mac/Linux: `source venv/bin/activate`

**2. Install the packages**

```bash
pip install -r requirements.txt
```

**3. Create a `.env` file in the project root**

```
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/
MONGO_DB=ai_banking_assistant
GROQ_API_KEY=your_key_here
```

Never commit this file. It is listed in `.gitignore`.

**4. Load the exam data**

```bash
python seed_exams.py
```

It is safe to run again: it updates exams by `exam_id` instead of creating duplicates.

**5. Start the app**

```bash
python app.py
```

Open http://127.0.0.1:5000.

## Updating exam data

Exam details change with every notification. To update one:

1. Edit the document in the `exams` collection in MongoDB Atlas, or edit `exams.json` and run `python seed_exams.py`.
2. Update its `last_verified` date.

Each exam has a `verification` field (`good`, `partial` or `low`). Anything not `good` shows a warning on the site and makes eligibility results say "verify" instead of a firm yes.

## CI/CD

Every push to `main` triggers `.github/workflows/ci.yml`:

1. **Test**: install dependencies and check the code compiles.
2. **Deploy**: if the checks pass, call the Render deploy hook so the new version goes live.

Pull requests run the checks but do not deploy.

**GitHub secrets** (Settings → Secrets and variables → Actions):

- `RENDER_DEPLOY_HOOK`: the deploy hook URL from the Render service settings

## Deploy on Render

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment variables:** `MONGO_URI`, `MONGO_DB`, `GROQ_API_KEY`
- **Auto-Deploy:** off, so deploys only happen after the tests pass

In MongoDB Atlas, allow Render to connect under Network Access.

## Roadmap

- Make the chat assistant answer using the exam data
- Study timetable generator
- Tests for the eligibility rules
- Confirm the remaining exam details against official notifications

## Data sources

Exam dates and rules were gathered from the official IBPS exam calendar and notifications as reported by news and coaching sites. They are not a substitute for the official notifications at [ibps.in](https://www.ibps.in), [sbi.co.in/web/careers](https://sbi.co.in/web/careers) and [rbi.org.in](https://www.rbi.org.in).
