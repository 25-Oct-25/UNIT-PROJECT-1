# game.py
import random

class Gamification:
    def __init__(self, username):
        self.username = username
        self.score = 0
        self.streak = 0

    def add_points(self, points):
        self.score += points
        # Simple streak logic: if points > 0, increase streak, else reset
        if points > 0:
            self.streak += 1
        else:
            self.streak = 0
