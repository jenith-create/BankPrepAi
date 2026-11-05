"""Load exams.json into MongoDB (safe to re-run: it updates by exam_id).

Usage:
    pip install pymongo python-dotenv
    python seed_exams.py

Reads MONGO_URI from your environment or .env file.
Optional: MONGO_DB (default "banking_ai").
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGO_URI")
if not uri:
    raise SystemExit("MONGO_URI is not set. Add it to your .env file.")

db_name = os.getenv("MONGO_DB", "banking_ai")
exams = json.loads((Path(__file__).parent / "exams.json").read_text(encoding="utf-8"))

collection = MongoClient(uri)[db_name]["exams"]
collection.create_index("exam_id", unique=True)

for exam in exams:
    collection.update_one({"exam_id": exam["exam_id"]}, {"$set": exam}, upsert=True)
    print(f"Saved {exam['exam_id']}")

print(f"Done: {len(exams)} exams in {db_name}.exams")
