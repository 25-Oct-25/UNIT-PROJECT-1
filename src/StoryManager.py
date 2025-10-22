from src.FileHandler import FileHandler
from src.AiHelper import AIHelper
from src.Story import Story
from src.EmailHelper import EmailHelper
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from colorama import Fore, Style, init

init(autoreset=True, convert=True)


class StoryManager:
    def __init__(self, username):
        """Initialize StoryManager with the current username and helper classes."""
        self.username = username
        self.file_handler = FileHandler()
        self.ai_helper = AIHelper()

    # MAIN MENU 

    def resume_last_story(self):
        """Load and continue the user's most recent story if available."""
        last_story_title = self.file_handler.get_last_story(self.username)
        if not last_story_title:
            print(Fore.YELLOW + "⚠️ No recent story found.")
            return

        stories_data = self.file_handler.load_stories(self.username)
        stories = [Story.from_dict(s) for s in stories_data]
        selected = next((s for s in stories if s.title == last_story_title), None)

        if not selected:
            print(Fore.RED + "❌ Last story not found.")
            return

        print(Fore.CYAN + f"\n📖 Your last story was: {selected.title}")
        choice = input("Do you want to continue it? (y/n): ").strip().lower()
        if choice == "y":
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")

    def start_new_story(self):
        """Start a new story by getting user input, generating the first part, and saving it."""
        print(Fore.CYAN + "\n🪄 Let's create your new story!" + Style.RESET_ALL)
        title = input("Enter a title for your story: ").strip()
        genre = input("Choose a genre (Drama, Adventure, Fantasy, Romance): ").strip()
        length = input("Do you want it short or long? ").strip().lower()
        prompt = input("Write the opening for your story: ").strip()

        print(Fore.LIGHTBLUE_EX + "\n✨ Generating the first part of your story...\n")
        result = self.ai_helper.generate_part(prompt, genre, length)

        story = Story(title, genre, length)
        story.add_part(result["text"])

        stories = self.file_handler.load_stories(self.username)
        stories.append(story.to_dict())
        self.file_handler.save_stories(self.username, stories)
        self.file_handler.set_last_story(self.username, story.title)

        print(Fore.CYAN + f"\n📚 You’re now reading: '{story.title}' 🌙")
        print(Fore.CYAN + "=" * 50)
        print(f"Genre: {story.genre.capitalize()} | Length: {story.length.capitalize()}")
        print("=" * 50 + "\n" + Style.RESET_ALL)

        self._print_story_text(result["text"])
        self._ask_user_choice(result, story, stories)

    # ASK USER CHOICE 

    def _ask_user_choice(self, result, story, stories):
        """Display the generated choices and handle user's selection for the next part."""

        if not result["options"] or len(result["options"]) < 3:
            print(Fore.YELLOW + "⚠️ AI did not generate full options, adding defaults..." + Fore.RESET)
            result["options"] = [
                "1. Continue the journey.",
                "2. Change direction of the story.",
                "3. End the story gracefully."
            ]


        print(Fore.CYAN + "\nChoose what happens next:" + Style.RESET_ALL)
        for opt in result["options"]:
            print(Fore.LIGHTYELLOW_EX + opt)
        print(Fore.LIGHTRED_EX + "0. 🛑 Stop and save progress to contune later" + Style.RESET_ALL)

        while True:
            choice = input(Fore.CYAN + "\nEnter 1, 2, 3 to continue or 0 to stop: ").strip()
            if choice == "0":
                print(Fore.GREEN + "\n✅ Progress saved. You can resume later.")
                self._save_stories(stories)
                print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")
                return
            elif choice in ["1", "2", "3"]:
                index = int(choice) - 1
                if index < len(result["options"]):
                    story.last_choice = result["options"][index]
                    self._story_loop(story, stories, auto_continue=True)
                    break
                else:
                    print(Fore.RED + "⚠️ This choice is unavailable, please try again.")
            else:
                print(Fore.RED + "❌ Invalid input. Please enter 1, 2, 3 or 0.")

    # STORY LOOP 

    def _story_loop(self, selected, stories, auto_continue=False):
        """Generate and display the next part of the story, continuing based on user choices."""

        print(Fore.LIGHTBLUE_EX + "\n✨ Generating the next part...\n")

        prompt = (
            f"Summary of previous parts:\n{self._summarize_story(selected.parts[:-1])}\n\n"
            f"Here’s the last scene of the story:\n{selected.parts[-1][-500:]}"
        )

        if selected.last_choice:
            prompt += f"\n\nContinue the story focusing on the choice: {selected.last_choice}"

        prompt += "\n\nContinue naturally from where the story left off. Do NOT restart or repeat previous events."

        result = self.ai_helper.generate_part(prompt, selected.genre, selected.length)
        new_part = result["text"]
        selected.add_part(new_part)

        part_number = len(selected.parts)
        print(Fore.CYAN + f"\n🪄 Part {part_number}:")
        print(Fore.LIGHTBLUE_EX + "-" * 40)
        self._print_story_text(new_part)
        print(Fore.LIGHTBLUE_EX + "-" * 40)
        print(Fore.GREEN + f"🕯️ End of Part {part_number} — progress saved automatically.\n")

        self._save_stories(stories)

        lines = [l.strip() for l in new_part.split("\n") if l.strip()]
        has_choices = any(line.startswith(("1.", "2.", "3.")) for line in lines)
        is_true_end = "THE END" in new_part.upper() and not has_choices

        if is_true_end:
            print(Fore.MAGENTA + "\n🏁 The story has reached its end. Well done!")
            print(Fore.LIGHTBLUE_EX + "=" * 50)
            print("Generated using AI Interactive Story Creator 🌙")
            print("=" * 50 + "\n")
            print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")
            return

        self._ask_user_choice(result, selected, stories)

    # STORY MANAGEMENT 

    def load_old_stories(self):
        """Load and allow the user to continue one of their saved stories."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n📂 No saved stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print(Fore.CYAN + "\n📜 Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.title} ({s.genre}, {len(s.parts)} parts)")

        choice = input(Fore.CYAN + "\nEnter the number of the story to continue: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(stories):
            selected = stories[int(choice) - 1]
            print(Fore.LIGHTBLUE_EX + f"\n✨ Continuing '{selected.title}'...")
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print(Fore.RED + "⚠️ Invalid selection. Returning to main menu.")

    def view_old_story(self):
        """Display a list of all saved stories with their details (title, genre, parts count)."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n📂 You don’t have any saved stories.")
            return

        print(Fore.CYAN + "\n📚 Your old stories:")
        for s in stories_data:
            print(f"• {s['title']} ({s['genre']}, {len(s['parts'])} parts)")

    def delete_story(self):
        """Allow the user to delete one of their saved stories (with confirmation)."""
        stories_data = self.file_handler.load_stories(self.username)

        if not stories_data:
            print(Fore.YELLOW + "📭 No saved stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print(Fore.CYAN + "\n🗑️ Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.get_summary()}")

        choice = input(Fore.CYAN + "\nEnter the number of the story to delete (or 0 to cancel): ").strip()

        if choice == "0":
            print(Fore.LIGHTBLUE_EX + "❎ Deletion canceled. Returning to main menu...")
            return

        if not choice.isdigit() or int(choice) not in range(1, len(stories) + 1):
            print(Fore.RED + "⚠️ Invalid choice.")
            return

        selected_story = stories[int(choice) - 1]
        confirm = input(Fore.YELLOW + f"Are you sure you want to delete '{selected_story.title}'? (y/n): ").strip().lower()
        if confirm != "y":
            print(Fore.LIGHTBLUE_EX + "❎ Deletion canceled. Returning to main menu...")
            return

        deleted_story = stories.pop(int(choice) - 1)
        self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])

        last_story = self.file_handler.get_last_story(self.username)
        if last_story == deleted_story.title:
            data = self.file_handler._read_data()
            if self.username in data and "last_story" in data[self.username]:
                del data[self.username]["last_story"]
                self.file_handler._write_data(data)
            print(Fore.CYAN + "🗒️ Removed from recent story record.")

        print(Fore.GREEN + f"✅ Story '{deleted_story.title}' has been deleted successfully!")

    def export_story(self):
        """Export a story as a TXT or PDF file, or send it via email with attachments."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n⚠️ No stories to export.")
            return

        print(Fore.CYAN + "\n📤 Select a story to export:")
        for i, s in enumerate(stories_data, start=1):
            print(f"{i}. {s['title']}")

        choice = input(Fore.CYAN + "Enter number: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories_data) + 1):
            print(Fore.RED + "❌ Invalid choice.")
            return

        selected = stories_data[int(choice) - 1]
        title = selected['title'].replace(' ', '_')

        export_dir = "Exports"
        os.makedirs(export_dir, exist_ok=True)

        print(Fore.CYAN + "\n📦 Choose export type:")
        print(Fore.LIGHTBLUE_EX + "1. 📄 Export as TXT file")
        print("2. 🧾 Export as PDF file")
        print("3. ✉️ Send via Email")

        export_choice = input(Fore.CYAN + "Enter 1, 2, or 3: ").strip()
        creation_date = datetime.now().strftime("%d %b %Y")

        #  1. TXT Export 
        if export_choice == "1":
            txt_path = os.path.join(export_dir, f"{title}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {selected['title']}\n")
                f.write(f"Genre: {selected['genre']}\n")
                f.write(f"Created on: {creation_date}\n")
                f.write(f"Author: {self.username}\n\n")
                for i, part in enumerate(selected["parts"], start=1):
                    f.write(f"--- Part {i} ---\n{part}\n\n")
                f.write("\nGenerated using AI Interactive Story Creator 🌙")

            print(Fore.GREEN + f"\n✅ Story exported successfully as '{txt_path}'")

        # 2. PDF Export 
        elif export_choice == "2":
            pdf_path = os.path.join(export_dir, f"{title}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            page_number = 1

            def draw_footer():
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(colors.grey)
                c.drawCentredString(width / 2, 40, f"Page {page_number}")

            y = height - 100
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(width / 2, y, selected['title'])
            y -= 30
            c.setFont("Helvetica-Oblique", 13)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, y, f"{selected['genre'].capitalize()} Story")
            y -= 20
            c.setFont("Helvetica", 11)
            c.setFillColor(colors.grey)
            c.drawCentredString(width / 2, y, f"Created on: {creation_date}")
            y -= 40

            for i, part in enumerate(selected["parts"], start=1):
                if y <= 100:
                    draw_footer()
                    c.showPage()
                    page_number += 1
                    y = height - 100
                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(colors.darkred)
                c.drawString(80, y, f"Part {i}")
                y -= 20
                c.setFont("Helvetica", 12)
                c.setFillColor(colors.black)
                for line in part.split("\n"):
                    if y <= 80:
                        draw_footer()
                        c.showPage()
                        page_number += 1
                        y = height - 100
                        c.setFont("Helvetica", 12)
                    c.drawString(80, y, line[:100])
                    y -= 16
                y -= 25

            draw_footer()
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColor(colors.grey)
            c.drawCentredString(width / 2, 60, "Generated using AI Interactive Story Creator 🌙")
            c.save()

            print(Fore.GREEN + f"\n✅ Story exported successfully as '{pdf_path}'")

        # 3. EMAIL EXPORT 
        elif export_choice == "3":
            email_helper = EmailHelper()
            receiver_email = input(Fore.CYAN + "Enter recipient email: ").strip()

            print(Fore.CYAN + "\n📧 Choose email attachment format:")
            print(Fore.LIGHTBLUE_EX + "1. Send as PDF")
            print("2. Send as TXT")
            attach_choice = input(Fore.CYAN + "Enter 1 or 2: ").strip()
            attachments = []

            if attach_choice == "1":
                pdf_path = os.path.join(export_dir, f"{title}.pdf")
                c = canvas.Canvas(pdf_path, pagesize=A4)
                width, height = A4
                y = height - 100
                c.setFont("Helvetica-Bold", 22)
                c.setFillColor(colors.darkblue)
                c.drawCentredString(width / 2, y, selected['title'])
                y -= 40
                for part in selected["parts"]:
                    c.setFont("Helvetica", 12)
                    c.setFillColor(colors.black)
                    for line in part.split("\n"):
                        if y <= 100:
                            c.showPage()
                            y = height - 100
                        c.drawString(80, y, line[:100])
                        y -= 16
                    y -= 25
                c.save()
                attachments.append(pdf_path)
                print(Fore.GREEN + f"📎 PDF ready: {pdf_path}")

            elif attach_choice == "2":
                txt_path = os.path.join(export_dir, f"{title}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"Title: {selected['title']}\nGenre: {selected['genre']}\n")
                    f.write(f"Created on: {creation_date}\nAuthor: {self.username}\n\n")
                    for i, part in enumerate(selected["parts"], start=1):
                        f.write(f"--- Part {i} ---\n{part}\n\n")
                    f.write("\nGenerated using AI Interactive Story Creator 🌙")
                attachments.append(txt_path)
                print(Fore.GREEN + f"📎 TXT ready: {txt_path}")
            else:
                print(Fore.RED + "❌ Invalid choice. Cancelled.")
                return

            subject = f"Your Story: {selected['title']}"
            body = f"Hey 🌙,\nHere’s your story '{selected['title']}' attached for you!"
            email_helper.send_email(receiver_email, subject, body, attachments=attachments)

        else:
            print(Fore.RED + "⚠️ Invalid option. Returning to main menu.")


    def _print_story_text(self, text):
        """Print the story text without showing the choice options."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        story_only = []
        for line in lines:
            if not line.startswith(("1.", "2.", "3.")):
                story_only.append(line)
            else:
                break
        print(Fore.WHITE + "\n".join(story_only)+Fore.RESET)

    def _summarize_story(self, parts):
        """Generate a short summary of previous story parts to avoid repetition in AI generation."""
        if not parts:
            return ""
        text = " ".join(parts)
        return text[-600:] if len(text) > 600 else text

    def _save_stories(self, stories):
        """Save the updated list of stories for the current user."""
        story_dicts = [s.to_dict() if isinstance(s, Story) else s for s in stories]
        self.file_handler.save_stories(self.username, story_dicts)

