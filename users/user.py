import bcrypt

class User:
    def __init__(self, username: str, password: str, role: str = "user", hashed: bool = False):
        self.username = username
        self.password = password if hashed else self.hash_password(password)
        self.role = role
        self.scores = {} # dice { "TimeTraveler": 50, "QuizBattle": 20 }
        self.achievements = []

    @staticmethod
    def hash_password (password: str) -> str:
        """Encrypt password using bcrypt"""
        return bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify that plain password matches the hashed one"""
        try:
            return bcrypt.checkpw(plain_password.encode("UTF-8"), hashed_password.encode("UTF-8"))
        except Exception as e:
            print(f"[verify_password error] {e}")
            return False

    def add_score(self,game_name: str, points: int):
        self.scores[game_name] = self.scores.get(game_name, 0) + points

    @property
    def total_score(self):
        return sum(self.scores.values())

    def add_achievement(self, achievement: str):
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,  # hashed string
            "role": self.role,
            "scores": self.scores,
            "achievements": self.achievements
        }

    
    @staticmethod
    def from_dict(data: dict):
        return User(
            data["username"],
            data["password"],
            role=data.get("role", "user"),
            hashed=True
        )