from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Literal
import datetime

@dataclass
class UserProfile:
    sex: str = "male"            # "male" or "female"
    age: int = 25
    height_cm: float = 170.0
    weight_kg: float = 70.0
    activity: str = "moderate"   # sedentary, light, moderate, active, very_active
    goal: str = "recomp"         # cut, bulk, recomp
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

@dataclass
class Workout:
    Day: str
    Focus: str
    Exercises: List[Dict[str, str]]  # e.g., [{"name": "Bench Press", "sets": "4x6-8"}]

@dataclass
class WeeklyPlan:
    split: str
    days: int
    workouts: List[Workout] = field(default_factory=list)

@dataclass
class Recipe:
    name: str
    kcal: int
    protein: int
    carbs: int
    fat: int
    tags: List[str] = field(default_factory=list)

# RBAC user
@dataclass
class User:
    username: str
    role: Literal["admin", "coach", "user"] = "user"
    password_hash: str = ""

@dataclass
class AppState:
    profile: UserProfile = field(default_factory=UserProfile)
    plan: Optional[WeeklyPlan] = None
    progress: List[Dict[str, float]] = field(default_factory=list)   # [{"date": "...", "weight": 0.0}]
    workouts_log: List[Dict[str, float]] = field(default_factory=list)
    habits_log: List[Dict[str, float]] = field(default_factory=list)
    settings: Dict[str, dict] = field(default_factory=lambda: {"lang": "ar", "window": {}, "brand": {}})

    # Email settings
    email_to: Optional[str] = None
    email_from: Optional[str] = None

    # RBAC
    users: List[User] = field(default_factory=list)
    current_user: Optional[str] = None

    # Schedulers (stored كـ dicts لتسهيل الـ JSON)
    report_schedules: List[Dict] = field(default_factory=list)
