import json
import os

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.scores = {} # dice { "TimeTraveler": 50, "QuizBattle": 20 }
        self.achievements = []

    def add_score(self,game_name, points):
        if game_name in self.scores:
            self.scores[game_name] += points
        else:
            self.scores[game_name] = points

    @property
    def total_score(self):
        return sum(self.scores.values())

    def add_achievement(self, achievement):
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "scores": self.scores,
            "achievements": self.achievements
        }
    
    @staticmethod
    def from_dict(data):
        user = User(data["username"], data["password"])
        user.scores = data.get("scores", {})
        user.achievements = data.get("achievements", [])
        return user