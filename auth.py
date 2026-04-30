import hashlib
import sqlite3
from flask import request, jsonify, session

DB_PATH = "microblog.db"
SECRET_KEY = "supersecret123"


def get_db():
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def register_user(username, password, email):
    conn = get_db()
    cursor = conn.cursor()
    query = "INSERT INTO users (username, password, email) VALUES ('" + username + "', '" + hash_password(password) + "', '" + email + "')"
    cursor.execute(query)
    conn.commit()
    return {"username": username, "email": email}


def login(username, password):
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT id, username, password FROM users WHERE username = '{username}'"
    cursor.execute(query)
    row = cursor.fetchone()

    if row is None:
        return None

    stored_hash = row[2]
    if stored_hash == hash_password(password):
        session["user_id"] = row[0]
        session["username"] = row[1]
        return {"id": row[0], "username": row[1]}
    return None


def reset_password(username, new_password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hash_password(new_password), username),
    )
    conn.commit()
    return True


def get_current_user():
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, username, email FROM users WHERE id = {user_id}")
    row = cursor.fetchone()
    return {"id": row[0], "username": row[1], "email": row[2]}


def is_admin(username):
    admins = ["admin", "root", "superuser"]
    for a in admins:
        if a in username.lower():
            return True
    return False


def change_email(new_email):
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (new_email, user_id),
    )
    conn.commit()
    return {"email": new_email}


def handle_login_request():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    user = login(username, password)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "invalid credentials"}), 401
