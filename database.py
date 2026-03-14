import sqlite3


def init_db():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # جدول الأحلام مرتبط بالمستخدم
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dreams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        dream TEXT,
        interpretation TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )

    conn.commit()
    conn.close()


def save_dream(user_id, dream, interpretation):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO dreams (user_id, dream, interpretation) VALUES (?, ?, ?)",
        (user_id, dream, interpretation)
    )

    conn.commit()
    conn.close()


def get_user_dreams(user_id):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT dream, interpretation FROM dreams WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    )

    dreams = cursor.fetchall()

    conn.close()

    return dreams
