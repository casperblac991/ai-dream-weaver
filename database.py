import sqlite3


def init_db():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dreams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        dream TEXT,
        interpretation TEXT,
        public INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username,password) VALUES (?,?)",
        (username,password)
    )

    conn.commit()
    conn.close()


def save_dream(user_id, dream, interpretation, public=0):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO dreams (user_id,dream,interpretation,public) VALUES (?,?,?,?)",
        (user_id,dream,interpretation,public)
    )

    conn.commit()
    conn.close()


def get_user_dreams(user_id):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT dream,interpretation FROM dreams WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    )

    dreams = cursor.fetchall()

    conn.close()

    return dreams


def get_public_dreams():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT dream,interpretation FROM dreams WHERE public=1 ORDER BY id DESC"
    )

    dreams = cursor.fetchall()

    conn.close()

    return dreams
