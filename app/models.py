from app.database import get_db
import sqlite3

def create_user(username, email, password):
    with get_db() as db:
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_user_by_email(email):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(user) if user else None

def get_user_by_id(user_id):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(user) if user else None

def save_dream(user_id, dream_text, interpretation):
    with get_db() as db:
        db.execute(
            "INSERT INTO dreams (user_id, dream_text, interpretation) VALUES (?, ?, ?)",
            (user_id, dream_text, interpretation)
        )
        db.commit()

def get_user_dreams(user_id):
    with get_db() as db:
        dreams = db.execute(
            "SELECT * FROM dreams WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(d) for d in dreams]

def increment_dreams_used(user_id):
    with get_db() as db:
        db.execute("UPDATE users SET dreams_used = dreams_used + 1 WHERE id = ?", (user_id,))
        db.commit()

def get_dreams_used(user_id):
    with get_db() as db:
        used = db.execute("SELECT dreams_used FROM users WHERE id = ?", (user_id,)).fetchone()
        return used[0] if used else 0

def update_user_plan(user_id, plan):
    with get_db() as db:
        db.execute("UPDATE users SET plan = ? WHERE id = ?", (plan, user_id))
        db.commit()
