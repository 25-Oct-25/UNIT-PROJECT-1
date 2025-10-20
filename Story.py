class Story:
    def __init__(self, title, genre, length, parts=None):
        self.title = title
        self.genre = genre
        self.length = length
        self.parts = parts if parts else []

    def add_part(self, text):
        """Add new part to the story"""
        self.parts.append(text)

    def get_summary(self):
        """return a short summary of the story"""
        return f"{self.title} ({self.genre}, {len(self.parts)} parts)"

    def to_dict(self):
        """convert the story object to a dictionary for json storage"""
        return {
            "title": self.title,
            "genre": self.genre,
            "length": self.length,
            "parts": self.parts
        }

    @staticmethod
    def from_dict(data):
        """load object Story from dict"""
        return Story(
            title=data["title"],
            genre=data["genre"],
            length=data["length"],
            parts=data["parts"]
        )
