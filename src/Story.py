
class Story:

    def __init__(self, title, genre, length, parts=None, last_choice=None):
        """
        Initialize a Story object.

        Args:
            title (str): Story title.
            genre (str): Story genre.
            length (str): 'short' or 'long'.
            parts (list, optional): List of story parts.
            last_choice (str, optional): The user's last selected choice.
        """
        self.title = title
        self.genre = genre
        self.length = length
        self.parts = parts if parts else []
        self.last_choice = last_choice  # Tracks user's most recent decision


    def add_part(self, text):
        """
        Add a new part to the story, avoiding duplicates.

        Args:
            text (str): The new story text to be added.
        """
        if not self.parts or self.parts[-1] != text:
            self.parts.append(text)
        else:
            print("⚠️ Duplicate story part detected, skipping addition.")


    def get_summary(self):
        """
        Return a short summary of the story.

        Returns:
            str: A string like 'Title (Genre, X parts)'.
        """
        return f"{self.title} ({self.genre}, {len(self.parts)} parts)"


    def to_dict(self):
        """
        Convert the story object into a dictionary for JSON storage.

        Returns:
            dict: Serializable story data.
        """
        return {
            "title": self.title,
            "genre": self.genre,
            "length": self.length,
            "parts": self.parts,
            "last_choice": self.last_choice,
            "created_at": getattr(self, "created_at", "Unknown"),

        }


    @staticmethod
    def from_dict(data):
        """
        Create a Story object from a dictionary loaded from JSON.

        Args:
            data (dict): JSON-like dictionary containing story data.

        Returns:
            Story: A fully initialized Story object.
        """
        return Story(
            title=data.get("title", "Untitled"),
            genre=data.get("genre", "Unknown"),
            length=data.get("length", "short"),
            parts=data.get("parts", []),
            last_choice=data.get("last_choice", None),
        )
