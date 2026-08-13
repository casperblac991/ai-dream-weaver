import sqlite3
from pathlib import Path

root = Path(__file__).parent
for name in ("blog", "articles", "templates"):
    print(f"{name}_html={len(list((root / name).glob('*.html')))}")
try:
    with sqlite3.connect(root / "app" / "weaver.db") as conn:
        for table in ("blog_posts", "users", "email_subscribers"):
            try:
                print(f"db_{table}={conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}")
            except sqlite3.Error as exc:
                print(f"db_{table}=unavailable:{exc}")
except sqlite3.Error as exc:
    print("db=unavailable", exc)
print("BLOG_SAMPLE")
for path in sorted((root / "blog").glob("*.html"))[:20]:
    print(path.name)
