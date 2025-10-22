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

def update_progress(user_id: int, course_id: int, delta: int):
    row = storage.query_one("SELECT progress FROM enrollments WHERE user_id=? AND course_id=?",
                            (user_id, course_id))
    if not row: return 0
    newp = max(0, min(100, row[0] + delta))
    storage.execute("UPDATE enrollments SET progress=? WHERE user_id=? AND course_id=?",
                    (newp, user_id, course_id))
    return newp

def recommend(user_id: int, limit: int = 3):
    top_level = storage.query_one("""
        SELECT c.level, COUNT(*) cnt
        FROM enrollments e JOIN courses c ON c.id=e.course_id
        WHERE e.user_id=? GROUP BY c.level ORDER BY cnt DESC LIMIT 1
    """, (user_id,))
    level = top_level[0] if top_level else None
    if level:
        return storage.query_all("""
            SELECT id, title, level, price, summary
            FROM courses
            WHERE level=? AND id NOT IN (SELECT course_id FROM enrollments WHERE user_id=?)
            LIMIT ?
        """, (level, user_id, limit))
    return storage.query_all("SELECT id,title,level,price,summary FROM courses ORDER BY price ASC LIMIT ?",(limit,))

def get_enrollment(user_id: int, course_id: int):
    return storage.query_one(
        "SELECT id, user_id, course_id, progress FROM enrollments WHERE user_id=? AND course_id=?",
        (user_id, course_id)
    )

def can_issue_certificate(user_id: int, course_id: int):
    row = get_enrollment(user_id, course_id)
    if not row:
        return False, "Not enrolled in this course."
    if row[3] < 100:
        return False, f"Current progress is {row[3]}% — need 100%."
    return True, None

def add_resource_link(course_id: int, title: str, url: str) -> int:
    cr = storage.query_one("SELECT id FROM courses WHERE id=?", (course_id,))
    if not cr:
        raise ValueError("Course does not exist.")
    return storage.execute("INSERT INTO resources(course_id, title, url) VALUES(?,?,?)",
                           (course_id, title.strip(), url.strip()))

def list_resource_links(course_id: int):
    return storage.query_all(
        "SELECT id, title, url, created_at FROM resources WHERE course_id=? ORDER BY created_at DESC", (course_id,)
    )

def list_available_courses_for_user(user_id: int):
    return storage.query_all("""
        SELECT c.id, c.title, c.level, c.price, c.summary
        FROM courses c
        WHERE c.id NOT IN (SELECT course_id FROM enrollments WHERE user_id=?)
        ORDER BY c.title
    """, (user_id,))
