import json
import os

class FileHandler:
    STORIES_FILE = "data/stories.json"

    @staticmethod
    def load_stories(username):
        """load the user's saved story"""
        if os.path.exists(FileHandler.STORIES_FILE):
            with open(FileHandler.STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(username, {}).get("stories", [])
        return []

    @staticmethod
    def save_stories(username, stories):
        """Safe storys for users"""
        os.makedirs("data", exist_ok=True)
        data = {}
        if os.path.exists(FileHandler.STORIES_FILE):
            with open(FileHandler.STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        if username not in data:
            data[username] = {}

        data[username]["stories"] = stories

        with open(FileHandler.STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def set_last_story(username, story_title):
        """save the last story the user worked on"""
        os.makedirs("data", exist_ok=True)
        data = {}
        if os.path.exists(FileHandler.STORIES_FILE):
            with open(FileHandler.STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        if username not in data:
            data[username] = {}

        data[username]["last_story"] = story_title

        with open(FileHandler.STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_last_story(username):
        """bring last story saved"""
        if os.path.exists(FileHandler.STORIES_FILE):
            with open(FileHandler.STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(username, {}).get("last_story")
        return None
