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
        public INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dream_id INTEGER,
        username TEXT,
        comment TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username,password) VALUES (?,?)",
        (username, password)
    )

    conn.commit()
    conn.close()


def save_dream(user_id, dream, interpretation, public=0):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO dreams (user_id,dream,interpretation,public) VALUES (?,?,?,?)",
        (user_id, dream, interpretation, public)
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


def get_public_dreams():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, dream, interpretation, likes FROM dreams WHERE public=1 ORDER BY likes DESC"
    )

    dreams = cursor.fetchall()

    conn.close()

    return dreams


def like_dream(dream_id):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE dreams SET likes = likes + 1 WHERE id=?",
        (dream_id,)
    )

    conn.commit()
    conn.close()


def add_comment(dream_id, username, comment):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (dream_id,username,comment) VALUES (?,?,?)",
        (dream_id, username, comment)
    )

    conn.commit()
    conn.close()


def get_comments(dream_id):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, comment FROM comments WHERE dream_id=?",
        (dream_id,)
    )

    comments = cursor.fetchall()

    conn.close()

    return comments
    def search_dreams(keyword):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT dream, interpretation FROM dreams WHERE dream LIKE ? AND public=1",
        ('%' + keyword + '%',)
    )

    results = cursor.fetchall()

    conn.close()

    return results
    def get_user_profile(username):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT dream, interpretation
        FROM dreams
        JOIN users ON dreams.user_id = users.id
        WHERE users.username = ?
        """,
        (username,)
    )

    dreams = cursor.fetchall()

    conn.close()

    return dreams
