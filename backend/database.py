import sqlite3, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "foodverse.db")

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT, input_name TEXT, result TEXT, created_at TEXT)""")

def save(kind, input_name, result):
    with _conn() as c:
        cur = c.execute("INSERT INTO history(kind,input_name,result,created_at) VALUES(?,?,?,?)",
                        (kind, input_name, json.dumps(result), datetime.now().isoformat(timespec="seconds")))
        return cur.lastrowid

def list_all():
    with _conn() as c:
        rows = c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 100").fetchall()
    return [{**dict(r), "result": json.loads(r["result"])} for r in rows]

def delete(i):
    with _conn() as c:
        c.execute("DELETE FROM history WHERE id=?", (i,))
