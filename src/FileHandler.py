import json
import os


class FileHandler:
    """Handles saving, loading, and managing story data for each user."""
    STORIES_FILE = "data/stories.json"

    # ---------- Internal Helper Methods ----------

    @staticmethod
    def _read_data():
        """
        Safely read and return JSON data from the stories file.
        Returns an empty dict if the file doesn't exist or is invalid.
        """
        if not os.path.exists(FileHandler.STORIES_FILE):
            return {}

        try:
            with open(FileHandler.STORIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If the file is empty or corrupted
            return {}

    @staticmethod
    def _write_data(data):
        """
        Safely write JSON data to the stories file.
        Creates directories automatically if missing.
        """
        os.makedirs(os.path.dirname(FileHandler.STORIES_FILE), exist_ok=True)
        with open(FileHandler.STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------- Public Methods ----------

    @staticmethod
    def load_stories(username):
        """
        Load all stories belonging to a specific user.
        Returns a list of story dictionaries.
        """
        data = FileHandler._read_data()
        return data.get(username, {}).get("stories", [])

    @staticmethod
    def save_stories(username, stories):
        """
        Save or update the list of stories for a specific user.
        """
        data = FileHandler._read_data()

        if username not in data:
            data[username] = {}

        data[username]["stories"] = stories
        FileHandler._write_data(data)

    @staticmethod
    def set_last_story(username, story_title):
        """
        Save the title of the last story the user worked on.
        """
        data = FileHandler._read_data()

        if username not in data:
            data[username] = {}

        data[username]["last_story"] = story_title
        FileHandler._write_data(data)

    @staticmethod
    def get_last_story(username):
        """
        Retrieve the title of the user's last saved story.
        Returns None if no story exists.
        """
        data = FileHandler._read_data()
        return data.get(username, {}).get("last_story")
