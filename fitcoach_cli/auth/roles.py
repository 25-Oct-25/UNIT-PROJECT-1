# -*- coding: utf-8 -*-
# Module: auth/roles.py
# Functions: 8  (_hash, add_user, set_role, delete_user, login, logout, current_role, require_role)
# Key features:
#   - Simple RBAC helpers for admin/coach/user roles
#   - Passwords stored as SHA-256 hashes (no plain text)
#   - Duplicate username checks and role validation
#   - Login/logout flow that sets `state.current_user`
#   - Authorization guard `require_role(...)` returning user-friendly messages
#   - Lightweight: no external crypto/runtime dependencies

from typing import Iterable, Optional
from ..core.models import AppState, User
import hashlib

#: Allowed roles in the system.
ROLES = {"admin", "coach", "user"}


def _hash(pw: str) -> str:
    """Return a SHA-256 hex digest for a plain-text password.

    Args:
        pw: Plain text password.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def add_user(state: AppState, username: str, role: str, password: str) -> str:
    """Create a user and append it to ``state.users``.

    Validates the role, prevents duplicate usernames, and stores a
    password hash (no plain text).

    Args:
        state: Application state container.
        username: Unique username to create.
        role: Target role, one of ``admin``, ``coach``, ``user`` (case-insensitive).
        password: Plain text password; will be hashed before storage.

    Returns:
        "OK" on success.

    Raises:
        ValueError: If the role is invalid or the username already exists.
    """
    role = role.lower()
    if role not in ROLES:
        raise ValueError("Role must be one of: admin, coach, user")
    if any(u.username == username for u in state.users):
        raise ValueError("Username already exists.")
    state.users.append(User(username=username, role=role, password_hash=_hash(password)))
    return "OK"


def set_role(state: AppState, username: str, role: str) -> str:
    """Update the role for an existing user.

    Args:
        state: Application state container.
        username: Username whose role will be updated.
        role: New role, one of ``admin``, ``coach``, ``user`` (case-insensitive).

    Returns:
        "OK" on success.

    Raises:
        ValueError: If the role is invalid or the user does not exist.
    """
    role = role.lower()
    if role not in ROLES:
        raise ValueError("Role must be one of: admin, coach, user")
    for u in state.users:
        if u.username == username:
            u.role = role
            return "OK"
    raise ValueError("User not found.")


def delete_user(state: AppState, username: str) -> str:
    """Delete a user by username.

    Args:
        state: Application state container.
        username: Username to remove.

    Returns:
        "OK" if a user was removed, otherwise "Not found".
    """
    before = len(state.users)
    state.users = [u for u in state.users if u.username != username]
    return "OK" if len(state.users) < before else "Not found"


def login(state: AppState, username: str, password: str) -> bool:
    """Attempt to authenticate and set the current user.

    Compares the provided password (after hashing) against the stored hash.

    Args:
        state: Application state container.
        username: Username to authenticate.
        password: Plain text password.

    Returns:
        True if credentials are valid and ``state.current_user`` is set; False otherwise.
    """
    for u in state.users:
        if u.username == username and u.password_hash == _hash(password):
            state.current_user = u.username
            return True
    return False


def logout(state: AppState) -> None:
    """Clear the current session (log out)."""
    state.current_user = None


def current_role(state: AppState) -> Optional[str]:
    """Get the role of the currently authenticated user.

    Args:
        state: Application state container.

    Returns:
        The role string if a user is logged in; otherwise ``None``.
    """
    if not state.current_user:
        return None
    for u in state.users:
        if u.username == state.current_user:
            return u.role
    return None


def require_role(state: AppState, allowed: Iterable[str]) -> Optional[str]:
    """Authorize access to an action based on the current user's role.

    Returns a user-friendly error message (string) when access is denied,
    or ``None`` when access is allowed. This makes it convenient to bubble
    messages directly to a CLI/UI without raising exceptions in normal flow.

    Args:
        state: Application state container.
        allowed: Iterable of allowed roles (e.g., ``("admin", "coach")``).

    Returns:
        None if access is permitted; otherwise a short error message such as
        "Login required." or "Forbidden. Requires role in [...], but you are '...'.".
    """
    r = current_role(state)
    if r is None:
        return "Login required."
    if r not in allowed:
        return f"Forbidden. Requires role in {list(allowed)}, but you are '{r}'."
    return None

