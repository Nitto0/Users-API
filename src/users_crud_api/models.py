import sqlite3


def init_users_db():
    users_db = sqlite3.connect("users.db")
    cur = users_db.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL
    )
    ''')

    users_db.commit()
    return users_db
