class Story:
    def __init__(self, title, genre, length, parts=None, last_choice=None):
        """
        initialize sotory object :
        - title: story's title
        - gener: type of story
        - length: length story(short or long)
        - parts: list of story part(chapters)
        - last_choice: the user last decision of selected option
        """
        self.title = title
        self.genre = genre
        self.length = length
        self.parts = parts if parts else []
        self.last_choice = last_choice  # story user's las choice

    def add_part(self, text):
        """Add new part"""
        self.parts.append(text)

    def get_summary(self):
        """return short summary of the story"""
        return f"{self.title} ({self.genre}, {len(self.parts)} parts)"

    def to_dict(self):
        """convert the story object to dict for json save"""
        return {
            "title": self.title,
            "genre": self.genre,
            "length": self.length,
            "parts": self.parts,
            "last_choice": self.last_choice
        }

    @staticmethod
    def from_dict(data):
        """load story object from dict json data"""
        return Story(
            title=data.get("title", "Untitled"),
            genre=data.get("genre", "Unknown"),
            length=data.get("length", "short"),
            parts=data.get("parts", []),
            last_choice=data.get("last_choice", None)
        )
