from datetime import date, datetime

from flask import Flask, render_template, request

from db import chat_collection
from services.ai_service import ask_ai
from services.eligibility import CATEGORIES, EDUCATION, check_eligibility
from services.exams import get_exams

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        question = request.form["question"]
        answer = ask_ai(question)
        chat_collection.insert_one({"question": question, "answer": answer})

    history = list(chat_collection.find().sort("_id", -1))
    return render_template("index.html", history=history, active="ask")


@app.route("/exams")
def exams():
    return render_template("exams.html", exams=get_exams(), active="exams")


@app.route("/eligibility", methods=["GET", "POST"])
def eligibility():
    results, error = None, None

    if request.method == "POST":
        try:
            dob = datetime.strptime(request.form["dob"], "%Y-%m-%d").date()
            if dob >= date.today():
                raise ValueError
            education = request.form["education"]
            category = request.form["category"]
            if education not in EDUCATION or category not in CATEGORIES:
                raise ValueError
            raw_percent = request.form.get("percent", "").strip()
            percent = float(raw_percent) if raw_percent else None
        except (KeyError, ValueError):
            error = "Please check your details: use a valid date of birth and a valid percentage."
        else:
            results = [
                {"exam": exam, **check_eligibility(exam, dob, education, category, percent)}
                for exam in get_exams()
            ]

    return render_template(
        "eligibility.html",
        results=results,
        error=error,
        categories=CATEGORIES,
        education=EDUCATION,
        form=request.form,
        active="eligibility",
    )


if __name__ == "__main__":
    app.run(debug=True)
