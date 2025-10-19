from typing import Iterable, Optional
from ..core.models import AppState, User
import hashlib

ROLES = ("admin","coach","user")

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def add_user(state: AppState, username: str, role: str, password: str) -> str:
    role = role.lower()
    if role not in ROLES:
        raise ValueError("Role must be one of: admin, coach, user")
    if any(u.username == username for u in state.users):
        raise ValueError("Username already exists.")
    state.users.append(User(username=username, role=role, password_hash=_hash(password)))
    return "OK"

def set_role(state: AppState, username: str, role: str) -> str:
    role = role.lower()
    if role not in ROLES:
        raise ValueError("Role must be one of: admin, coach, user")
    for u in state.users:
        if u.username == username:
            u.role = role
            return "OK"
    raise ValueError("User not found.")

def delete_user(state: AppState, username: str) -> str:
    before = len(state.users)
    state.users = [u for u in state.users if u.username != username]
    return "OK" if len(state.users) < before else "Not found"

def login(state: AppState, username: str, password: str) -> bool:
    for u in state.users:
        if u.username == username and u.password_hash == _hash(password):
            state.current_user = u.username
            return True
    return False

def logout(state: AppState) -> None:
    state.current_user = None

def current_role(state: AppState) -> Optional[str]:
    if not state.current_user:
        return None
    for u in state.users:
        if u.username == state.current_user:
            return u.role
    return None

def require_role(state: AppState, allowed: Iterable[str]) -> Optional[str]:
    r = current_role(state)
    if r is None:
        return "Login required."
    if r not in allowed:
        return f"Forbidden. Requires role in {list(allowed)}, but you are '{r}'."
    return None
