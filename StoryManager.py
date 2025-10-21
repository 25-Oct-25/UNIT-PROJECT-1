from FileHandler import FileHandler
from AiHelper import AIHelper
from Story import Story
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os


class StoryManager:
    def __init__(self, username):
        self.username = username
        self.file_handler = FileHandler()
        self.ai_helper = AIHelper()

    def resume_last_story(self):
        """contune last story saved"""
        last_story_title = self.file_handler.get_last_story(self.username)
        if not last_story_title:
            print("No recent story found.")
            return

        stories_data = self.file_handler.load_stories(self.username)
        stories = [Story.from_dict(s) for s in stories_data]
        selected = next((s for s in stories if s.title == last_story_title), None)

        if not selected:
            print("Last story not found in records.")
            return

        print(f"\nYour last story was: {selected.title}")
        choice = input("Do you want to continue it? (y/n): ").strip().lower()
        if choice == "y":
            self._continue_story(selected, stories)
        else:
            print("Returning to main menu.")

    def start_new_story(self):
        """to start new story"""
        title = input("Enter a title for your story: ").strip()
        genre = input("Choose a genre (Drama, Adventure, Fantasy, Romance): ").strip()
        length = input("Do you want it short or long? ").strip().lower()
        prompt = input("Write the opening for your story: ").strip()

        print("\nGenerating the first part of your story...\n")
        result = self.ai_helper.generate_part(prompt, genre, length)
        story_part = result["text"]
        story = Story(title, genre, length)
        story.add_part(story_part)
        story.last_choice = result["choice"]

        stories = self.file_handler.load_stories(self.username)
        stories.append(story.to_dict())
        self.file_handler.save_stories(self.username, stories)
        self.file_handler.set_last_story(self.username, story.title)

        
        print(f"\n Starting your interactive story: '{story.title}'") 
        print("=" * 50)
        print(f"Genre: {story.genre.capitalize()} | Length: {story.length.capitalize()}")
        print("=" * 50 + "\n")

        print(story_part)
        self._story_continuation_loop(story, stories)

    def load_old_stories(self):
        """load old story"""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("No stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print("\n Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.get_summary()}")

        choice = input("Choose a story number to continue: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories) + 1):
            print("Invalid choice.")
            return

        selected = stories[int(choice) - 1]
        self._continue_story(selected, stories)

    def view_old_story(self):
        """view old story"""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("No saved stories.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print("\nYour saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.get_summary()}")

        choice = input("Enter story number to view: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories) + 1):
            print("Invalid choice.")
            return

        selected = stories[int(choice) - 1]
        print(f"\n {selected.title} ({selected.genre})")
        print("-" * 40)
        for idx, part in enumerate(selected.parts, start=1):
            print(f"\nPart {idx}:\n{part}\n")
        print("-" * 40)

    def export_story(self):
        """export story as PDF or TXT"""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("No stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print("\nYour saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.get_summary()}")

        choice = input("Enter the number of the story to export: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories) + 1):
            print("Invalid choice.")
            return

        selected = stories[int(choice) - 1]
        print("\n1. Export as TXT")
        print("2. Export as PDF")
        file_type = input("Choose (1 or 2): ").strip()

        os.makedirs("exports", exist_ok=True)
        filename_base = f"exports/{selected.title.replace(' ', '_')}"

        if file_type == "1":
            with open(filename_base + ".txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {selected.title}\nGenre: {selected.genre}\nLength: {selected.length}\n\n")
                for idx, part in enumerate(selected.parts, start=1):
                    f.write(f"Part {idx}:\n{part}\n\n")
            print(f"TXT exported: {filename_base}.txt")

        elif file_type == "2":
            pdf = SimpleDocTemplate(filename_base + ".pdf", pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], alignment=1, fontSize=22, spaceAfter=20)
            subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], alignment=1, textColor="#555", spaceAfter=15)
            body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=12, leading=16)

            elements.append(Paragraph(selected.title, title_style))
            elements.append(Paragraph(f"{selected.genre} | {selected.length}", subtitle_style))
            elements.append(HRFlowable(width="80%", color="#888", spaceAfter=20))

            for idx, part in enumerate(selected.parts, start=1):
                elements.append(Paragraph(f"<b>Part {idx}</b>", styles["Heading3"]))
                elements.append(Paragraph(part.replace("\n", "<br/>"), body_style))
                elements.append(Spacer(1, 10))

            pdf.build(elements)
            print(f"PDF exported: {filename_base}.pdf")

        else:
            print("Invalid choice.")

    

    def _continue_story(self, selected, stories):
        """contune saved story"""
        print(f"\n Continuing '{selected.title}'...\n")
        result = self.ai_helper.generate_part(selected.parts[-1], selected.genre, selected.length)
        new_part = result["text"]
        selected.last_choice = result["choice"]
        selected.add_part(new_part)
        self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])
        self.file_handler.set_last_story(self.username, selected.title)
        print(new_part)
        self._story_continuation_loop(selected, stories)

    def _story_continuation_loop(self, selected, stories):
        """loop to ask user if want to contune story or stop"""
        while True:
            cont = input("\nDo you want to continue the story? (y/n): ").strip().lower()

            if cont == "y":
                print("\n Continuing the story...\n")
                result = self.ai_helper.generate_part(selected.parts[-1], selected.genre, selected.length)
                new_part = result["text"]
                selected.last_choice = result["choice"]
                selected.add_part(new_part)
                self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])

                print(new_part)

                # check if there is end of the story
                if "THE END" in new_part.upper().replace(".", "").strip():
                    print("\n🏁 The story has reached its end. Congratulations!")
                    print("=" * 50)
                    print("Thank you for playing this interactive story!")
                    print("=" * 50 + "\n")
                    self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])
                    break

            elif cont == "n":
                print("\n✅ Story progress saved. You can resume it later.")
                self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])
                break

            else:
                print("Please enter 'y' or 'n'.")
