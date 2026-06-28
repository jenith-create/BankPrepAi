from flask import Flask, render_template, request
from services.ai_service import ask_ai
from db import chat_collection
app = Flask(__name__)

chat_history = []

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        question = request.form["question"]

        answer = ask_ai(question)

        chat_collection.insert_one({
            "question": question,
            "answer": answer
        })

    history = list(
        chat_collection.find().sort("_id", -1)
    )

    return render_template(
        "index.html",
        history=history
    )

if __name__ == "__main__":
    app.run(debug=True)