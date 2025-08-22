# Utility functions
import sqlite3
import re
import os


def get_db_connection(path: str):
    conn = sqlite3.connect(path)
    return conn


def validate_resume_name(name: str) -> bool:
    # Only allow alphanumeric and underscores, min 3 chars
    return bool(re.match(r"^[\w]{3,}$", name))


def get_groq_api_key():
    from dotenv import load_dotenv

    load_dotenv()
    return os.getenv("GROQ_API_KEY")
