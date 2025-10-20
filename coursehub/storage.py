import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "coursehub.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT CHECK(role IN ('student','admin')) NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            level TEXT CHECK(level IN ('beginner','intermediate','advanced')) NOT NULL,
            price REAL NOT NULL,
            summary TEXT NOT NULL
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            progress INTEGER DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
            UNIQUE(user_id, course_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )""")
        con.commit()

def query_one(sql, params=()):
    with get_conn() as con:
        return con.execute(sql, params).fetchone()

def query_all(sql, params=()):
    with get_conn() as con:
        return con.execute(sql, params).fetchall()

def execute(sql, params=()):
    with get_conn() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
