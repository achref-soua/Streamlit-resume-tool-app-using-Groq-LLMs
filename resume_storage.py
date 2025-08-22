# Resume storage and CRUD operations
import json
from utils import get_db_connection

DB_PATH = "db/resumes.db"

# Resume CRUD functions


def save_resume(user: str, name: str, data: dict):
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO resumes (user, name, data) VALUES (?, ?, ?)",
        (user, name, json.dumps(data)),
    )
    conn.commit()
    conn.close()


def load_resumes(user: str):
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, data FROM resumes WHERE user=?", (user,))
    rows = c.fetchall()
    conn.close()
    return [{"name": r[0], **json.loads(r[1])} for r in rows]


def update_resume(user: str, name: str, data: dict):
    save_resume(user, name, data)


def duplicate_resume(user: str, old_name: str, new_name: str):
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM resumes WHERE user=? AND name=?", (user, old_name))
    row = c.fetchone()
    if row:
        c.execute(
            "INSERT INTO resumes (user, name, data) VALUES (?, ?, ?)",
            (user, new_name, row[0]),
        )
        conn.commit()
    conn.close()


# Delete a resume
def delete_resume(user: str, name: str):
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM resumes WHERE user=? AND name=?", (user, name))
    conn.commit()
    conn.close()
