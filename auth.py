# User authentication logic
import bcrypt
import streamlit as st
from utils import get_db_connection

DB_PATH = "db/users.db"

# Helper functions for password hashing


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


# Database functions


def create_user(username: str, password: str) -> bool:
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        return False
    hashed = hash_password(password)
    c.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed)
    )
    conn.commit()
    conn.close()
    return True


def authenticate_user(username: str, password: str) -> bool:
    conn = get_db_connection(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and check_password(password, row[0]):
        return True
    return False


# Streamlit session management


def login_page():
    st.title("Login / Signup")
    mode = st.radio("Select mode", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button(mode):
        if mode == "Sign Up":
            if create_user(username, password):
                st.success("User created. Please log in.")
            else:
                st.error("Username already exists.")
        else:
            if authenticate_user(username, password):
                st.session_state["user"] = username
                st.success("Logged in!")
            else:
                st.error("Invalid credentials.")


def get_current_user():
    return st.session_state.get("user")


def logout():
    st.session_state.pop("user", None)
    st.success("Logged out.")
