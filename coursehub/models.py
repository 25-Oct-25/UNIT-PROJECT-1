from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    role: str        # "student" | "admin"
    email: str
    name: str

@dataclass
class Course:
    id: Optional[int]
    title: str
    level: str       # "beginner" | "intermediate" | "advanced"
    price: float
    summary: str

@dataclass
class Enrollment:
    id: Optional[int]
    user_id: int
    course_id: int
    progress: int    # 0..100
