import sqlite3


def init_db():
    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dreams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dream TEXT,
        interpretation TEXT
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
