import bcrypt

class User:
    """Represents a game user with authentication, scores, and achievements."""
    def __init__(self, username: str, password: str, role: str = "user", hashed: bool = False, scores: dict = None, achievements: dict = None):
        self.username = username
        self.password = password if hashed else self.hash_password(password)
        self.role = role
        self.scores = scores
        self.achievements = achievements

    @staticmethod
    def hash_password (password: str) -> str:
        """Encrypt password using bcrypt."""
        return bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Check if the entered password matches the hashed password."""
        try:
            return bcrypt.checkpw(plain_password.encode("UTF-8"), hashed_password.encode("UTF-8"))
        except Exception as e:
            print(f"[verify_password error] {e}")
            return False

    def add_score(self,game_name: str, points: int):
        """Add or update the user's score for a specific game."""
        self.scores[game_name] = self.scores.get(game_name, 0) + points

    @property
    def total_score(self):
        """Return the total score from all games."""
        return sum(self.scores.values())

    def add_achievement(self, achievement: str):
        """Add a new achievement if not already earned."""
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def to_dict(self) -> dict:
        """Convert the user object to a dictionary for saving."""
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "scores": self.scores,
            "achievements": self.achievements
        }

    
    @staticmethod
    def from_dict(data: dict):
        """Create a User instance from stored dictionary data."""
        return User(
            data["username"],
            data["password"],
            role=data.get("role", "user"),
            hashed=True,
            scores=data['scores'],
            achievements=data['achievements']
        )