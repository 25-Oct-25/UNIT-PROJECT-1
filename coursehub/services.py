from typing import Optional
from . import storage

def ensure_user(email: str, name: str, role: str):
    row = storage.query_one("SELECT id FROM users WHERE email=?", (email,))
    if row: return row[0]
    return storage.execute("INSERT INTO users(role,email,name) VALUES(?,?,?)", (role, email, name))

def get_user(email: str):
    return storage.query_one("SELECT id, role, email, name FROM users WHERE email=?", (email,))

def add_course(title: str, level: str, price: float, summary: str):
    return storage.execute("INSERT INTO courses(title,level,price,summary) VALUES(?,?,?,?)",
                           (title, level, price, summary))

def list_courses(level: Optional[str] = None):
    if level:
        return storage.query_all("SELECT id,title,level,price,summary FROM courses WHERE level=?", (level,))
    return storage.query_all("SELECT id,title,level,price,summary FROM courses")

def search_courses(keyword: str):
    kw = f"%{keyword}%"
    return storage.query_all(
        "SELECT id,title,level,price,summary FROM courses WHERE title LIKE ? OR summary LIKE ?", (kw, kw))

def get_course(course_id: int):
    return storage.query_one("SELECT id,title,level,price,summary FROM courses WHERE id=?", (course_id,))

def enroll(user_id: int, course_id: int):
    return storage.execute("INSERT OR IGNORE INTO enrollments(user_id, course_id, progress) VALUES(?,?,0)",
                           (user_id, course_id))

def my_courses(user_id: int):
    return storage.query_all("""
        SELECT e.id, c.id, c.title, c.level, e.progress, c.price
        FROM enrollments e JOIN courses c ON c.id=e.course_id
        WHERE e.user_id=? ORDER BY c.title
    """, (user_id,))
