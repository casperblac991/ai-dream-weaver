import sqlite3


def init_db():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    # جدول الأحلام
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dreams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dream TEXT,
        interpretation TEXT
    )
    """)

    # جدول المستخدمين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_dream(dream, interpretation):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO dreams (dream, interpretation) VALUES (?, ?)",
        (dream, interpretation)
    )

    conn.commit()
    conn.close()


def get_all_dreams():

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, dream, interpretation FROM dreams ORDER BY id DESC")

    dreams = cursor.fetchall()

    conn.close()

    return dreams
