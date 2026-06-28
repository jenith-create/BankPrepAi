from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_ai(question):

    prompt = f"""
    You are an expert Banking Exam Tutor.

    Answer the following banking exam question.

    Question:
    {question}

    Provide:
    1. Correct answer
    2. Explanation
    3. Shortcut or exam tip
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content