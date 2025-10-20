# Path: fitcoach_cli/core/models.py
# Description: Core dataclasses for user profiles, workouts, plans, recipes, users, and app state.

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Literal
import datetime

@dataclass
class UserProfile:
    """Basic profile and goal settings.

    Attributes:
        sex (str): "male" or "female".
        age (int): Age in years.
        height_cm (float): Height in centimeters.
        weight_kg (float): Weight in kilograms.
        activity (str): Activity level (sedentary, light, moderate, active, very_active).
        goal (str): Goal type (cut, bulk, recomp).
        created_at (str): ISO timestamp of creation.
    """
    sex: str = "male"            # "male" or "female"
    age: int = 25
    height_cm: float = 170.0
    weight_kg: float = 70.0
    activity: str = "moderate"   # sedentary, light, moderate, active, very_active
    goal: str = "recomp"         # cut, bulk, recomp
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

@dataclass
class Workout:
    """Single workout day entry.

    Attributes:
        Day (str): Day label (e.g., "Day 1").
        Focus (str): Focus area (e.g., "Upper", "Lower", "Full Body").
        Exercises (List[Dict[str, str]]): List of movements with set schemes.
    """
    Day: str
    Focus: str
    Exercises: List[Dict[str, str]]  # e.g., [{"name": "Bench Press", "sets": "4x6-8"}]

@dataclass
class WeeklyPlan:
    """Weekly training plan.

    Attributes:
        split (str): Split type (e.g., "upper-lower", "full-body", "ppl").
        days (int): Number of training days.
        workouts (List[Workout]): Sequence of workouts.
    """
    split: str
    days: int
    workouts: List[Workout] = field(default_factory=list)

@dataclass
class Recipe:
    """Nutrition recipe with macros.

    Attributes:
        name (str): Recipe name.
        kcal (int): Calories.
        protein (int): Protein grams.
        carbs (int): Carbs grams.
        fat (int): Fat grams.
        tags (List[str]): Optional tags (e.g., "breakfast", "chicken").
    """
    name: str
    kcal: int
    protein: int
    carbs: int
    fat: int
    tags: List[str] = field(default_factory=list)

# RBAC user
@dataclass
class User:
    """User record for simple RBAC.

    Attributes:
        username (str): Unique username.
        role (Literal["admin","coach","user"]): Role name.
        password_hash (str): Password hash (storage/verification handled elsewhere).
    """
    username: str
    role: Literal["admin", "coach", "user"] = "user"
    password_hash: str = ""

@dataclass
class AppState:
    """Application state container.

    Attributes:
        profile (UserProfile): Current user profile.
        plan (Optional[WeeklyPlan]): Current weekly plan.
        progress (List[Dict[str, float]]): Weight/progress log entries.
        workouts_log (List[Dict[str, float]]): Workout session entries.
        habits_log (List[Dict[str, float]]): Habit tracking entries.
        settings (Dict[str, dict]): App settings (e.g., language, window, brand).
        email_to (Optional[str]): Default recipient email for reports.
        email_from (Optional[str]): Default sender email for reports.
        users (List[User]): RBAC users.
        current_user (Optional[str]): Username of the active user.
        report_schedules (List[Dict]): Report scheduler jobs stored as dicts (JSON-friendly).
    """
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

    # Schedulers (stored as dicts for easy JSON serialization)
    report_schedules: List[Dict] = field(default_factory=list)
